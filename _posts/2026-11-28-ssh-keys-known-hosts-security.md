---
title: "SSH Keys, Known Hosts, and the Security We Stop Thinking About"
date: 2026-11-28
categories:
  - Linux
tags:
  - ssh
  - linux
  - security
  - homelab
description: "Revisit SSH host identity, fingerprint verification, user keys and agent forwarding before familiar shortcuts become security habits."
toc: true
---

I SSH into almost everything in my homelab.

Raspberry Pis, Linux machines, Proxmox hosts—if a device gives me SSH access, chances are I use it. Often enough that `ssh user@host` barely feels like a command anymore. It is muscle memory.

Familiarity is useful until it turns a security decision into a reflex. A host-key warning appears, I recognise the IP address, and my fingers are already looking for the offending entry in `known_hosts`.

Usually, I have rebuilt the machine. But “usually” is doing rather a lot of work there.

## Two identities in one connection

When I type:

```bash
ssh user@server
```

SSH first needs to establish the server's identity, then authenticate my user account.

With the usual OpenSSH file-based setup, those checks involve different keys and files:

| File | Where | What it does |
| --- | --- | --- |
| `~/.ssh/known_hosts` | My client | Records host identities I trust |
| `~/.ssh/authorized_keys` | The remote account | Lists public keys allowed to authenticate to that account |
| `~/.ssh/id_ed25519` | My client | Holds a private user key |

Servers have their own host keys, separate from my user key pair. Changing my login key does not repair a server-identity warning. These paths describe a common setup; administrators can configure other locations or use certificate-based trust.

The distinction is simple enough. Remembering it while troubleshooting is the useful part.

## A changed host key needs an explanation

Anyone who rebuilds lab machines has probably seen:

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

I certainly have. In my case, it is usually an IP address now belonging to a rebuilt machine. My old habit was to open `known_hosts` in Vim and remove the entry.

That removes the warning. It does not verify the replacement server.

Before changing the trust record, compare the fingerprint presented by SSH with one obtained through a trusted route. For a lab machine, that might be the hypervisor console. On the server's trusted console, this prints the fingerprint of its Ed25519 **host** public key:

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Use the host-key type and path configured on that server; the client must be presenting the same key type for the comparison to mean anything. For a managed system, use the administrator's established verification process.

Once the changed identity is verified and expected, remove the obsolete record on the client:

```bash
ssh-keygen -R 192.168.1.20
```

For a nonstandard port, the lookup includes the port:

```bash
ssh-keygen -R '[192.168.1.20]:2222'
```

Use the hostname or address SSH actually checked. Reconnect and compare the displayed fingerprint before accepting it. `-R` handles hashed entries too; it is less error-prone than guessing which line to edit.

The same verification matters on a first connection. With trust on first use, accepting the initial key creates a reference for later connections; acceptance alone does not prove who supplied it. Fetching a key with `ssh-keyscan` over the same untrusted network does not independently establish its authenticity either.

The warning is doing its job. My job is to explain the change before making it disappear.

## My private key does not travel to the server

With public-key authentication, the remote account authorises my public key. My client proves possession of the corresponding private key by producing a signature that the server can verify.

The private key itself is not sent to the server. It is also not the secret that encrypts every byte of the session: SSH establishes separate session encryption keys.

That makes copying a private key onto each destination unnecessary. A server needs the public key and suitable account policy, not a copy of my credentials.

## The agent I stopped thinking about

`ssh-agent` can hold user keys and perform authentication signatures for the client. A quick inventory is:

```bash
ssh-add -l
```

This lists fingerprints of identities available through the current agent. An empty list means no identities are loaded; an agent-connection error means the client cannot reach one. Neither result proves that no private-key files exist on disk.

To load a particular key with a one-hour lifetime:

```bash
ssh-add -t 1h ~/.ssh/id_ed25519
```

For a passphrase-protected key, loading it normally prompts for the passphrase. The lifetime limits its availability in that agent; it does not revoke the public key on any server. Desktop integrations can also manage loading differently.

Agent forwarding extends access to that signing capability through a remote session. The private key is not copied there, but someone able to access the forwarded agent socket can potentially authenticate using its loaded identities while that access exists.

That is enough reason to avoid enabling forwarding everywhere. A [jump-host connection using `ProxyJump`]({% post_url 2026-11-04-ssh-config-beyond-host-aliases %}#reach-an-internal-host-with-proxyjump) lets my local client handle destination authentication without forwarding the agent. It is a useful distinction when all I need is a route through another machine.

## RSA because my fingers remember it

My first instinct when generating a key is still often RSA. Mostly because it is what I remember typing.

For a new general-purpose key on systems that support it, Ed25519 is a sensible choice:

```bash
ssh-keygen -t ed25519
```

Choose a passphrase for an interactive personal key, and do not overwrite an existing key accidentally. Compatibility and organisational cryptographic policy still matter; Ed25519 is not a universal answer for every environment.

RSA keys are not automatically broken. A key's algorithm and the signature algorithm used with it are separate considerations. Habit alone, though, is a poor way to choose either.

## Permissions belong to the right machine

On a Unix-like client, conservative permissions for my directory and private key are:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
```

On the **remote account**, the corresponding baseline is:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

These commands assume the files already exist and belong to the intended account. They do not fix incorrect ownership, parent-directory permissions or ACLs. Windows requires its own access-control handling.

`600` means owner read/write. For a directory, `700` also grants the owner traversal: the execute bit is about reaching entries inside it.

The distinction behind the permissions matters: a private key must stay confidential; `authorized_keys` contains public keys, but its integrity controls who can log in. It must not be writable by someone who should not control that account. OpenSSH's server-side checks also consider ownership and other relevant paths.

## Keep the useful habit, lose the automatic response

I do not need another introduction to host aliases here; [SSH Config Beyond Host Aliases]({% post_url 2026-11-04-ssh-config-beyond-host-aliases %}) covers identities, routing and configuration inspection.

The habit I want to change is smaller: pause when a server's identity changes, verify the fingerprint, and only then update the trust record. Check what the agent holds before assuming its convenience is harmless.

SSH makes connecting feel routine. Deciding which machine and account to trust still deserves a moment of attention.

### References

- [OpenSSH client and host authentication](https://man.openbsd.org/ssh)
- [Key generation, fingerprints and known-host removal](https://man.openbsd.org/ssh-keygen)
- [Authentication agent](https://man.openbsd.org/ssh-agent)
- [Loading and inspecting agent identities](https://man.openbsd.org/ssh-add)
- [Server authentication files and permissions](https://man.openbsd.org/sshd)
- [Client configuration and agent forwarding](https://man.openbsd.org/ssh_config)
