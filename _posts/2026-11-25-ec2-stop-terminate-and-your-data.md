---
title: "EC2: What Survives Stop and Terminate?"
date: 2026-11-25
categories:
  - DevOps
tags:
  - AWS
  - EC2
  - storage
description: "Understand EC2 storage persistence, DeleteOnTermination and the checks to make before stopping or replacing an instance."
toc: true
---

“The data is on the server” is an incomplete answer in EC2. It could mean a persistent EBS volume, temporary instance store, or a filesystem mounted from another service. Those have different lifetimes.

That distinction matters when stopping a lab instance, retiring a server or applying an infrastructure change that replaces one. The instance disappearing and the data disappearing are separate events—but the configuration can connect them.

## Identify the storage first

Instance store is temporary storage on disks attached to the physical host. It suits caches, buffers and scratch data that can be rebuilt. Not every instance type provides it. See AWS's [instance store overview](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html).

EBS volumes have a separate lifecycle from the instance, subject to their deletion settings. For a normal reboot, stop/start or termination, use this distinction:

| Action | EBS volume | Instance store |
| --- | --- | --- |
| Reboot | Data retained | Data retained during a normal reboot |
| Stop/start an EBS-backed instance | Data retained | Data erased |
| Terminate | Deleted or retained according to each volume's setting | Data lost |

Do not treat reboot persistence as a durability guarantee for instance store: losing the host can also mean losing its local data. Persistent information needs storage and recovery arrangements that survive the instance.

## Check every volume's deletion setting

For EBS, the setting that connects termination to deletion is `DeleteOnTermination`:

- `true`: terminating the instance deletes that volume.
- `false`: the volume remains after termination and continues to incur charges.

Check the instance's **Storage** tab and the **Delete on termination** column for every block device. Do not assume that “data disk” means “retained”: defaults depend on how and when the volume was attached. AWS documents the combinations in [preserving volumes on termination](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/preserving-volumes-on-termination.html).

A retained volume still needs a recovery path: identify the filesystem, application configuration and any encryption keys needed to use it. Keeping a disk is useful; knowing how to recover from it is considerably more useful.

## Stopping is not a complete reset

For an EBS-backed instance, stopping preserves its EBS data but loses RAM contents in an ordinary stop. On restart, the automatically assigned public IPv4 address can change; an associated Elastic IP is the relevant exception. Check the actual address before assuming an SSH failure means the machine is broken.

Stopped instances can still leave billable resources, including EBS volumes. AWS explains these lifecycle details in [Stop and start Amazon EC2 instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html).

## Take a recoverable backup before a destructive change

An EBS snapshot captures data written to the volume, not writes still buffered by the application or operating system. Coordinate writes with the application; for a root volume, AWS recommends stopping the instance before taking the snapshot. See [creating EBS snapshots](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html).

Before termination or replacement, identify the mounted storage, inspect deletion settings, preserve required data and confirm the recovery procedure. This applies just as much when the deletion comes from a [Terraform replacement plan]({% post_url 2026-11-03-terraform-plan-before-apply %}) as when someone clicks **Terminate** in the console.

The important boundary is the data's lifetime. Once that is explicit, deciding whether an instance can safely disappear becomes a much more practical conversation.
