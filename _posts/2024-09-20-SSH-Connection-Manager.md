---
title: "SSH Connection Manager in Command Line"
excerpt: "Managing multiple SSH connections and hosts can sometimes be problematic. In this post, I will show how you can easily save multiple connections directly in the terminal (Linux) to take advantage of tab completion, passwordless authentication, and more."
categories:
  - Linux
  - Howto

tags:
  - Linux
  - Tips
  - HowTo

toc: true
header:
  teaser: "/assets/images/ssh-connection-manager/ssh_logo.jpg"
---

## Managing SSH Connections

In the Windows ecosystem, tools like Remote Desktop Manager help handle and manage multiple connections to the various servers within the infrastructure. But how can we achieve something similar for SSH connections to frequently accessed servers in Linux?

Let’s explore how this can be done efficiently in the command line.

## SSH Config file

First, if it doesn’t already exist, create the .ssh directory in a convenient location (I keep mine in my $HOME directory):

```bash
mkdir .ssh
```

Next, create a file named config, adjust its default permissions, and open it with your favorite text editor:

```bash
touch config

chmod 600 config

vim config
```

This file is automatically sourced by the terminal, allowing you to easily connect to machines defined in it. Here's a sample of the configuration I use to manage my servers:

```bash
Host node_01
        Hostname node01.lab.com
        User pscustomobject
        IdentityFile /home/pscustomobject/.ssh/id_rsa
Host node_02
        Hostname node02.example.com
        User adminuser
        Port 4242

## Set connection defaults for all hosts, this is overriden by host options
Host *
     ForwardAgent no
     ForwardX11 no
     ForwardX11Trusted yes
     User pscustomobject
     Port 22
     Protocol 2
     ServerAliveInterval 60
     ServerAliveCountMax 30

```

## Key Notes

- The IdentityFile directive points to the location of your private key. This can be stored in a shared or networked location for easier access across multiple devices.
- The *Host ** section defines defaults for all hosts, which individual host entries can override.

Once the SSH configuration is in place, you can connect to any of the defined hosts simply by issuing the command:

```bash
ssh node_01
```

Better yet, tab completion will work just as it does for standard commands, so you don’t have to remember the exact name of each node.

## Additional Tips

I highly recommend reading the *ssh_config* man page (*man ssh_config*) to discover the numerous other options you can use in your config file to further streamline and simplify SSH connection management.
