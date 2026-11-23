---
title: "Before Moving Files, Check the Filesystem"
slug: which-filesystem-holds-your-files
date: 2026-12-05
featured: true
feature_title: "Which filesystem is filling up?"
feature_description: "Trace a directory to its mount before moving or deleting files to reclaim space."
categories:
  - Linux
tags:
  - linux
  - rhcsa
  - filesystems
  - troubleshooting
description: "Use df, findmnt and lsblk to identify the filesystem behind a Linux directory and understand where moving or deleting files can reclaim space."
---

Suppose a service cannot write its logs under `/var/log`. You check the available space and notice that `/home` has plenty. Before moving anything, there is a question worth answering: which filesystem is actually running out of space?

The directory names alone will not tell us. `/var/log` might use the root filesystem, a separate `/var` filesystem, or its own mount. `/home` might share that space, or have an entirely separate allocation.

Let's use a few read-only commands to work out where the files live. This is the useful part of learning the filesystem hierarchy: knowing which storage a file operation will affect.

## One Tree Can Contain Several Filesystems

Linux presents files through one directory tree starting at `/`. Mounting a filesystem attaches it at a directory called a **mount point**. Paths below that directory use the mounted filesystem until another mount takes over further down the tree.

For our example, assume this layout:

- `/` is on a filesystem called `rhel-root`, including `/etc`, `/var` and `/var/log`.
- `/home` is a separate filesystem called `rhel-home`.

![An illustrative Linux directory tree. The root filesystem contains etc and var/log. A separate home filesystem is mounted at home, so its free space belongs to a different filesystem.]({{ '/assets/images/rhcsa/filesystem-boundaries.svg' | relative_url }})

The `/home` directory is still part of the same tree. Its contents use a different filesystem. That boundary matters much more than how close two paths look in the terminal.

## Ask About the Path That Is Failing

On a RHEL lab machine, start with:

```bash
df -hT /var/log /home
```

These commands inspect the machine; they do not change its mounts or files. Use existing paths on your system. The output below is a **simplified, illustrative example**, not a measurement from a server:

```text
Filesystem             Type  Size  Used Avail Use% Mounted on
/dev/mapper/rhel-root   xfs    20G   19G  1.0G  95% /
/dev/mapper/rhel-home   xfs   100G  4.0G   96G   4% /home
```

`df` reports space for the filesystem containing each supplied path. `-h` makes sizes easier to read, and `-T` adds the filesystem type.

The first row answers our question: `/var/log` uses the filesystem mounted at `/`. It does not need to have its own row labelled `/var/log`.

The 96 GB available under `/home` belongs to the second filesystem. Deleting a file there will not free space on `rhel-root`. Both filesystems could even reside on the same physical disk; their free-space figures are still separate.

Also, `-T` does not filter out virtual filesystems. A bare `df -hT` may include entries such as `tmpfs`. Supplying the path is what keeps this investigation focused.

## Find the Mount Behind a Directory

For the mount itself, use:

```bash
findmnt -T /var/log
```

Here **`-T` means target path**, unlike `df -T`, where it means filesystem type. Same letter, different command. Convenient, in the usual Linux sense :)

`findmnt` identifies the filesystem serving the supplied path even when that path is not itself a mount point. In our example, its `TARGET` is `/` and its `SOURCE` is `/dev/mapper/rhel-root`.

Read `TARGET`, `SOURCE` and `FSTYPE` together: where the filesystem is attached, what supplies it, and its type. The `OPTIONS` column can also help explain behaviour, such as a read-only mount. Available space does not guarantee that writes are permitted.

To see the wider mount hierarchy:

```bash
findmnt
```

This is particularly useful if `/var` or `/var/log` turns out to have a separate mount. Check the machine's actual layout rather than assuming it matches the example.

## Use lsblk for the Device View

```bash
lsblk
```

`lsblk` shows block devices and their relationships: disks, partitions and logical volumes, along with mount points where available. It helps you connect a name such as `rhel-root` to the storage layout beneath it.

Its `SIZE` column describes device capacity. It is not the amount of free space available for a new log file. For that question, return to `df`.

A mounted network filesystem or a `tmpfs` does not need to appear as a local block device. An entry missing from `lsblk` is therefore not evidence that the mount is missing. Use `findmnt` for the mounted-filesystem view.

## What This Changes Before You Move Files

With our example layout, moving a file from `/var/log` to another directory on `rhel-root` changes its location without transferring its data to another filesystem. It will not solve a space shortage on that filesystem.

Moving data to a different filesystem can release source space after the source copy is removed, but that decision needs more than a free-space figure. A service may expect a particular path, ownership or SELinux context. Do not move active logs elsewhere just because `/home` looks inviting.

Likewise, mounting storage over a directory that already contains files makes those existing contents temporarily inaccessible through that path. It does not delete them or reclaim their space. The directory name can stay the same while the filesystem reached through it changes.

{% assign links_article = site.posts | where_exp: 'post', 'post.published != false' | where_exp: 'post', 'post.hidden != true' | where_exp: 'post', 'post.date <= site.time' | where: 'slug', 'linux-hard-and-symbolic-links' | first %}
{% if links_article %}
There is a further wrinkle after deletion: [hard links and open files can keep storage in use]({{ links_article.url | relative_url }}). That article explains why removing one filename does not always release its data.
{% endif %}

These checks establish which filesystem to investigate. They do not identify the largest files or prove that a write failure is caused by space rather than permissions, quotas or another constraint. The useful first step is smaller: before deciding what to remove or relocate, make sure the proposed change would affect the filesystem that needs it.

### Further Reading

- [GNU df: filesystem space usage](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html)
- [findmnt: find the filesystem for a path](https://man7.org/linux/man-pages/man8/findmnt.8.html)
- [lsblk: block devices and their relationships](https://man7.org/linux/man-pages/man8/lsblk.8.html)
- [mount: attaching filesystems to the directory tree](https://man7.org/linux/man-pages/man8/mount.8.html)
- *Red Hat RHCSA 10 Cert Guide*, Chapter 3: Essential File Management Tools, my study reference.
