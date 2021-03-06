"""
Open edX Instance deployment and provision.

"""

from pulumi import export, Config, ResourceOptions
from pulumi_aws import ec2, iam, GetAmiFilterArgs
import provisioners


def decode_key(key):
    if key.startswith('-----BEGIN RSA PRIVATE KEY-----'):
        return key
    return key.encode('ascii')

config = Config()

key_name = config.get('keyName')
public_key = config.get('publicKey')

private_key = config.require_secret('privateKey').apply(decode_key)
private_key_passphrase = config.get_secret('privateKeyPassphrase')


tags = {"pulumi_managed": "true", "auto_off": "true"}

size = "t2.large"
ami = ec2.get_ami(
    most_recent=True,
    owners=["679593333241"],
    filters=[
        GetAmiFilterArgs(
            name="name",
            values=["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"],
        ),
    ],
)

# TODO Create a security group
security_group = ec2.SecurityGroup(
    f"openedx-sg",
    description="Basic Open edX security group",
    egress=[
        ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    ingress=[
        ec2.SecurityGroupIngressArgs(
            protocol=ec2.ProtocolType.TCP,
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        ec2.SecurityGroupIngressArgs(
            protocol=ec2.ProtocolType.TCP,
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        ec2.SecurityGroupIngressArgs(
            protocol=ec2.ProtocolType.TCP,
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
        ec2.SecurityGroupIngressArgs(
            protocol=ec2.ProtocolType.TCP,
            from_port=18000,
            to_port=18999,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={**tags, "Name": "Open edX"},
)

# TODO Create an EC2 instance
#user_data = ""
with open("config.sh") as f:
    user_data = f.read()

if key_name is None:
    key = ec2.KeyPair("openedx-key", public_key=public_key)
    key_name = key.key_name

openedx_instance = ec2.Instance(
    f"openedx-instance",
    instance_type=size,
    vpc_security_group_ids=[security_group.id],
    #user_data=user_data,
    ami=ami.id,
    key_name=key_name,
    root_block_device=ec2.InstanceRootBlockDeviceArgs(
        delete_on_termination=True,
        volume_size=50,
        encrypted=True,
    ),
    tags={**tags, "Name": "Open edX"}
)

# TODO Provision EC2 instance
conn = provisioners.ConnectionArgs(
    host=openedx_instance.public_ip,
    username="ubuntu",
    private_key=private_key,
    private_key_passphrase=private_key_passphrase
)    

config_file = provisioners.RemoteExec(
    "config-file",
    conn=conn,
    commands=[
        "echo 'export PUBLIC_IP=$(curl ifconfig.me)' >> .bashrc && source .bashrc && echo -e \"EDXAPP_LMS_BASE: \"$PUBLIC_IP\"\nEDXAPP_CMS_BASE: \"$PUBLIC_IP:18010\"\" > config.yml",
        #'source .bashrc && echo -e "EDXAPP_LMS_BASE: "$PUBLIC_IP"\nEDXAPP_CMS_BASE: "$PUBLIC_IP:18010"" > config.yml',
        "cat config.yml"
    ],
    opts=ResourceOptions(depends_on=[openedx_instance]),
)

copy_script = provisioners.CopyFile(
    "copy-install-script",
    conn=conn,
    src="edx.platform-install.sh",
    dest="edx.platform-install.sh",
    opts=ResourceOptions(depends_on=[openedx_instance]),
)
"""
run_install_script = provisioners.RemoteExec(
    "run-install-script",
    conn=conn,
    commands=[
        "chmod +x edx.platform-install.sh"
    ],
    opts=ResourceOptions(depends_on=[copy_script]),
)
"""
export("public_ip", openedx_instance.public_ip)
export("public_dns", openedx_instance.public_dns)
