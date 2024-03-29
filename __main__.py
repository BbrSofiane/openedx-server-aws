"""
Open edX Instance deployment and provision.

"""

from pulumi import export, Config, ResourceOptions, get_stack
from pulumi_aws import ec2, iam, GetAmiFilterArgs

import provisioners


def decode_key(key):
    if key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
        return key
    return key.encode("ascii")


stack = get_stack()
config = Config()

key_name = config.get("keyName")
public_key = config.get("publicKey")

private_key = config.require_secret("privateKey").apply(decode_key)
private_key_passphrase = config.get_secret("privateKeyPassphrase")

tags = {"pulumi_managed": "true", "auto_off": "true"}
size = "t3a.large"

# TODO make this a config variable
OPENEDX_RELEASE = "open-release/lilac.master"

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

# Create a security group
security_group = ec2.SecurityGroup(
    "openedx-sg",
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
            from_port=18000,
            to_port=18999,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={**tags, "Name": f"Open edX {stack}"},
)

if key_name is None:
    key = ec2.KeyPair("openedx-key", public_key=public_key)
    key_name = key.key_name

# TODO Make the spot price a config variable
openedx_instance = ec2.Instance(
    "openedx-instance",
    # spot_price="0.03",
    instance_type=size,
    vpc_security_group_ids=[security_group.id],
    ami=ami.id,
    key_name=key_name,
    root_block_device=ec2.InstanceRootBlockDeviceArgs(
        delete_on_termination=True,
        volume_size=50,
        encrypted=True,
    ),
    tags={**tags, "Name": f"Open edX {stack}"},
)

# Provision EC2 instance
conn = provisioners.ConnectionArgs(
    host=openedx_instance.public_ip,
    username="ubuntu",
    private_key=private_key,
    private_key_passphrase=private_key_passphrase,
)


# https://openedx.atlassian.net/wiki/spaces/OpenOPS/pages/1969455764/Koa+Native+Open+edX+platform+Ubuntu+20.04+64+bit+Installation
install_openedx = provisioners.RemoteExec(
    "install-openedx",
    conn=conn,
    commands=[
        "sudo locale-gen en_GB en_GB.UTF-8",
        "sudo dpkg --configure -a",
        "sudo apt-get update",
        "sudo apt-get upgrade -y",
        "echo -e \"EDXAPP_LMS_BASE: '$(curl ipinfo.io/ip)'\nEDXAPP_CMS_BASE: '$(curl ipinfo.io/ip):18010'\" > config.yml",
        'export LC_ALL="en_GB.UTF-8"',
        'export LC_CTYPE="en_GB.UTF-8"',
        #f"wget https://raw.githubusercontent.com/edx/configuration/{OPENEDX_RELEASE}/util/install/ansible-bootstrap.sh -O - | sudo -E bash",
        #f"wget https://raw.githubusercontent.com/edx/configuration/{OPENEDX_RELEASE}/util/install/generate-passwords.sh -O - | bash",
        #f"export OPENEDX_RELEASE={OPENEDX_RELEASE} && wget https://raw.githubusercontent.com/edx/configuration/{OPENEDX_RELEASE}/util/install/native.sh -O - | bash & > install.out",
    ],
    opts=ResourceOptions(depends_on=[openedx_instance], parent=openedx_instance),
)

export("public_ip", openedx_instance.public_ip)
export("public_dns", openedx_instance.public_dns)
