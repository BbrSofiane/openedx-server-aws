<a href="https://gitmoji.dev">
  <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square" alt="Gitmoji">
</a>

# Open edX Instance Using Amazon EC2

[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/BbrSofiane/openedx-server-aws)

A Single instance Open edX Server in AWS.

The VM will be deployed in a public subnet of your default VPC.

## Getting started

### Prerequisites

1. Register for [Ubuntu 20.04](https://aws.amazon.com/marketplace/pp/Canonical-Group-Limited-Ubuntu-2004-LTS-Focal/B087QQNGF1) offical image on AWS Marketplace
1. [Install Pulumi](https://www.pulumi.com/docs/get-started/install/)
1. [Configure Pulumi for AWS](https://www.pulumi.com/docs/intro/cloud-providers/aws/setup/)
1. [Configure Pulumi for Python](https://www.pulumi.com/docs/intro/languages/python/)
1. Create a virtualenv
1. pip install -r requirements.txt

### Deploying and running the program

First, create a stack, using `pulumi stack init`.

```
$ pulumi stack init dev
```

Next, generate an OpenSSH keypair for use with your server - as per the AWS [Requirements][1]

```
$ ssh-keygen -t rsa -f rsa -b 4096 -m PEM
```

This will output two files, `rsa` and `rsa.pub`, in the current directory. Be sure not to commit these files!

We then need to configure our stack so that the public key is used by our EC2 instance, and the private key used
for subsequent SCP and SSH steps that will configure our server after it is stood up.

```
$ cat rsa.pub | pulumi config set publicKey --
$ cat rsa | pulumi config set privateKey --secret --
```

If your key is protected by a passphrase, add that too:

```
$ pulumi config set privateKeyPassphrase --secret [yourPassphraseHere]
```

Notice that we've used `--secret` for both `privateKey` and `privateKeyPassphrase`. This ensures their are
stored in encrypted form in the Pulumi secrets system.

Also set your desired AWS region:

```
$ pulumi config set aws:region eu-west-2
```

From there, you can run `pulumi up` and all resources will be provisioned and configured.

The installation script for Open edX can take up to 2 hours. In the meantime you can still connect to your instance.

### Connect to your instance

To view the host name and IP address of the instance via `pulumi stack output`

```
Current stack outputs (2):
    OUTPUT      VALUE
    public_dns  your-instance-dns-name
    public_ip   your-instance-ip-address
```

You can use the ssh key to connect to your instance:

```
$ ssh -i rsa ubuntu@$(pulumi stack output public_ip)
```

If you are using [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) you will need to:

1. Copy the private into .pem: `cp rsa rsa.pem`
1. [Change permissions](https://superuser.com/a/1296046) on `rsa.pem`.

### Clean up

To clean up resources, run pulumi destroy and answer the confirmation question at the prompt.

[1]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws
