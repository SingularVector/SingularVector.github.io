---
title: "The Disk Has Space. Why Can't the Service Write?"
slug: disk-has-space-service-cannot-write
date: 2026-12-09
categories:
  - Linux
tags:
  - linux
  - permissions
  - troubleshooting
  - automation
description: "Follow a small Linux permissions lab to distinguish file writes, directory access and file creation, then check which account actually runs the service."
toc: true
---

Suppose an application cannot write its log. You check the filesystem: plenty of space. You try the path yourself, perhaps with `sudo`, and it works.

Excellent. We have established that *you* can write there. The application might still have a different opinion :)

Free space answers a capacity question. It does not tell us whether a particular process can reach a file, modify it or create its replacement. Let's separate those operations with a small lab, then bring the service account into the picture.

{% assign filesystem_article = site.posts | where_exp: 'post', 'post.published != false' | where_exp: 'post', 'post.hidden != true' | where_exp: 'post', 'post.date <= site.time' | where: 'slug', 'which-filesystem-holds-your-files' | first %}
{% if filesystem_article %}
If you have not yet checked which filesystem serves the failing path, start with [Before Moving Files, Check the Filesystem]({{ filesystem_article.url | relative_url }}). Here, we will assume we have already identified it.
{% endif %}

## A Writable File Behind a Closed Door

Use **Bash as an ordinary user on a Linux lab machine**, with a writable local temporary directory. Do not use `sudo`: a privileged account can bypass the permissions we want to observe. This exercise uses ordinary owner permissions, without extra ACLs or security policies changing the result.

Run the blocks in order in the same terminal. `mktemp` creates a new private directory; all our changes stay inside it.

{% assign mktemp_article = site.posts | where_exp: 'post', 'post.published != false' | where_exp: 'post', 'post.hidden != true' | where_exp: 'post', 'post.date <= site.time' | where: 'slug', 'mktemp-temporary-directory' | first %}
{% if mktemp_article %}
For a closer look at the template and temporary-directory cleanup, see [mktemp: Give Your Script Its Own Temporary Directory]({{ mktemp_article.url | relative_url }}).
{% endif %}

```bash
# Create a unique directory (-d), replacing XXXXXX with random characters.
# Use TMPDIR if it is set and non-empty; otherwise use /tmp.
# Capture the created directory's path in lab with $(...).
lab=$(mktemp -d "${TMPDIR:-/tmp}/sv-write-lab.XXXXXX")

mkdir "$lab/logs"
chmod 700 "$lab/logs"

printf 'Initial entry\n' > "$lab/logs/app.log"
chmod 600 "$lab/logs/app.log"

printf 'Baseline write\n' >> "$lab/logs/app.log"
```

The directory's owner has `rwx`; the file's owner has `rw-`. The baseline append should succeed. Now remove just the directory's owner execute permission:

```bash
chmod u-x "$lab/logs"

printf 'Blocked write\n' >> "$lab/logs/app.log"
```

Expect **Permission denied**; the shell's exact wording will vary. The file still has its write bit. We changed the directory, not the file.

On a directory, `x` means **search permission**: the ability to resolve names inside it. Opening `app.log` through this path requires search permission on every directory along the way. The file's own permissions only become useful once the process can reach it.

![The lab directory allows traversal, but logs has mode 600 and lacks owner search permission. Path lookup stops there before reaching app.log, even though the file itself permits owner writes.]({{ '/assets/images/rhcsa/write-permissions-path.svg' | relative_url }})

Inspect the directory itself:

```bash
ls -ld "$lab" "$lab/logs"
namei -l "$lab/logs/app.log"
```

`ls -d` shows each directory's own entry. `namei -l`, from util-linux, follows the path and displays modes, owners and groups for its components. In this deliberately broken state, expect it to stop at the inaccessible part. It is a useful alternative to staring harder at the final filename.

Restore the missing permission and try again:

```bash
chmod u+x "$lab/logs"

printf 'Write after restoring search permission\n' >> "$lab/logs/app.log"
cat "$lab/logs/app.log"
```

The blocked entry should be absent; the other three lines should be present. Nothing about the available disk space changed.

## Appending Is Not Creating

There is another distinction worth testing before we leave this directory. Keep search permission, but remove the owner's directory write permission:

```bash
chmod u-w "$lab/logs"

printf 'Existing file still writable\n' >> "$lab/logs/app.log"
touch "$lab/logs/new.log"
```

The append should succeed. Creating `new.log` should fail.

Appending to our existing file needs search permission through the directories and write permission on the file. Creating a new directory entry also needs **write and search permission on the containing directory**. The existing file's write bit does not grant that.

This helps explain a service that writes happily until its log is rotated or it needs a new output file. Those operations may involve creating or renaming entries, rather than reopening the same file. Establish which operation failed before changing permissions.

Restore the directory and remove our disposable files:

```bash
chmod u+w "$lab/logs"

rm "$lab/logs/app.log"
rmdir "$lab/logs"
rmdir "$lab"
```

These cleanup commands assume the expected results above. If you created extra files while experimenting, inspect them before removing the directory.

## Now Ask Who Is Doing the Writing

In the lab, we owned everything. A service usually introduces a different account. Your successful terminal test may have used a different user, different groups and more privileges.

For a systemd service, replace `example.service` with the real unit name:

```bash
systemctl show example.service -p User -p Group -p MainPID
```

These are read-only checks. `User` and `Group` describe the configured identity; `MainPID` identifies the running main process. With its actual PID substituted for `1234`, inspect that process too:

```bash
ps -o pid,euser,egroup,args -p 1234
```

That shows its effective user and primary group. An inactive service has no running main process to inspect. A blank unit setting is not enough to establish the identity of every worker either: applications can start children or change their own credentials.

Use `id` to see your current shell's user and group memberships. Compare the **process that fails** with the owners and groups along its target path, rather than assuming your shell represents it. Supplementary groups can matter too; the short `ps` view above is not a complete access check.

In the ordinary mode-bit model, owner, group and other are distinct classes. If the process owns a file, Linux checks the owner bits; it does not fall back to a more generous group or other setting when those owner bits deny access.

The fix should follow the intended ownership and access model. Giving everyone write access may change the symptom, but it leaves us without an explanation of who should be allowed to write there.

## When the Mode Bits Are Not the Answer

This lab isolates ordinary permissions. A real service can also encounter ACL restrictions, SELinux denials or a read-only filesystem. Free blocks do not rule out an exhausted inode allocation or a user quota either. Read the actual error before treating every write failure as the same problem.

Systemd can give a service a more restricted filesystem view through settings such as `ProtectSystem` or `ReadOnlyPaths`. Running a command as the same account outside the unit does not reproduce those restrictions. The [systemd execution documentation](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Sandboxing) explains that boundary; disabling protections is not a useful first diagnostic step.

For now, we have a more precise question than “why can't it write?” Which process, through which path, trying to perform which operation? That is enough to distinguish a writable file behind an inaccessible directory from a directory that cannot accept a new file. Both can happen on a disk with plenty of room.

### Further Reading

- [Linux pathname resolution and directory search permission](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
- [Opening and creating files: permission errors](https://man7.org/linux/man-pages/man2/open.2.html)
- [namei: inspect the components of a path](https://man7.org/linux/man-pages/man1/namei.1.html)
- [systemd execution identities and filesystem restrictions](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)
