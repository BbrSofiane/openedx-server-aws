<a href="https://gitmoji.dev">
  <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square" alt="Gitmoji">
</a>

[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/BbrSofiane/openedx-server-aws)

# openedx-server-aws

# TODO Add deploy with pulumi button

A Single instance Open edX Server in AWS.

Deployment in a public subnet of your default VPC.

## Getting started

### Prerequisites

Register for Ubuntu 20.04 offical image on AWS Marketplace

1. Create a virtualenv
2. pip install -r requirements.txt

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

### Clean up

[1]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws

copy rsa to rsa.pem
Permissions issue on windows https://superuser.com/a/1296046
