---
title: "SSH Connection Manager in Command Line"
excerpt: "Use OpenSSH host aliases with the correct config path, option precedence and a local configuration check before connecting."
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
last_modified_at: 2026-11-02
---

When several servers have different usernames, ports and keys, an OpenSSH client configuration is often enough to stop reconstructing the connection command every time. Each `Host` entry gives the connection a memorable alias.

## Create the client configuration

On Linux or macOS, the normal per-user location is `~/.ssh/config`. Create it without depending on your current working directory:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

Open that file in your editor. The OpenSSH **client** reads it; it is not a shell startup file sourced by the terminal. The original commands created `.ssh` and `config` relative to the current directory, which could put the file somewhere SSH never consulted.

## Put specific hosts before general defaults

```sshconfig
Host node_01
    HostName node01.example.com
    User deploy
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host node_02
    HostName node02.example.com
    User adminuser
    Port 4242

Host *
    ForwardAgent no
    ForwardX11 no
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Replace the example hostnames, accounts and key path. Most scalar options use the **first obtained value**, so put more specific blocks before `Host *`. `IdentityFile` is one of the options that can accumulate multiple values; do not assume every directive follows the same override rule.

`IdentitiesOnly yes` limits which configured identities the first host offers, rather than trying every key available through an agent. It does not create a key, install a public key on a server or guarantee a login without prompts. Authentication and any key passphrase still need an appropriate setup.

Keep private keys under suitable access controls. Placing one on a shared or network location, as the old article suggested, is not a general distribution strategy; the SSH configuration only needs the path accessible to this client.

## Inspect before connecting

```bash
ssh -G node_01
```

`-G` prints the evaluated configuration without opening the SSH session. For this example, confirm the resulting hostname, username, port and identities. With configurations you did not write, inspect any `Match exec` clauses before evaluating them: those clauses can run local commands during configuration processing.

Then connect with the alias:

```bash
ssh node_01
```

Host-key checking still applies. Verify an unfamiliar server fingerprint through the normal trusted channel; an alias does not establish server identity.

Tab completion depends on the shell and its completion setup. Some installations suggest aliases from SSH configuration, while others need completion support enabled; defining a `Host` entry alone does not guarantee it.

References: [OpenSSH client configuration](https://man.openbsd.org/ssh_config) and [ssh command options](https://man.openbsd.org/ssh).
