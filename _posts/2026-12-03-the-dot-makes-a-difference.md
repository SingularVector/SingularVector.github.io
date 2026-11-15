---
title: "The Dot Makes a Difference: Copying Files in Linux"
date: 2026-12-03
published: false
categories:
  - Linux
tags:
  - linux
  - bash
  - rhcsa
  - filesystems
description: "Compare three cp commands to see why hidden files disappear, directory nesting changes, and a destination slash can catch a mistaken path."
---

A directory copy can finish without an error and still leave you with the wrong result: an extra directory level, or a missing configuration file whose name starts with a dot.

For this RHCSA preparation article, let’s compare three commands that look almost interchangeable. The useful part is knowing which files the shell passes to `cp`, and which directory level you intend to copy.

## One Source, Three Empty Destinations

Use Bash and GNU `cp` on your Linux lab machine, as an ordinary user. Start with a new directory; choose another name if this one already exists:

```bash
mkdir ~/rhcsa-copy-lab
cd ~/rhcsa-copy-lab
mkdir source whole visible contents
echo 'application notes' > source/notes.txt
echo 'setting=enabled' > source/.settings
```

`source` contains one visible file and one hidden file. Check both:

```bash
ls -a source
```

Alongside `.` and `..`, you should see `.settings` and `notes.txt`. Hidden files are ordinary files with names starting with a dot; “hidden” does not mean unimportant.

## Copy the Directory Itself

```bash
cp -a source whole/
ls -a whole/source
```

Because `whole` already exists as a directory, the result is **`whole/source/`**, containing both files.

`-a` is archive mode: it copies recursively, preserves symbolic links as links, and attempts to preserve attributes such as permissions, ownership and timestamps. What can be preserved depends on your privileges and the destination filesystem.

There is no wildcard here. `cp` walks the source directory itself, including hidden entries.

## Copy What the Wildcard Matches

```bash
cp -a source/* visible/
ls -a visible
```

You get **`visible/notes.txt`**, but no `.settings`.

With the usual Bash settings, the shell expands `source/*` before starting `cp`. In this example, it passes `source/notes.txt` as the source argument. `cp` never receives `.settings`, so archive mode cannot make it copy that file.

This is a selection problem, not a permissions problem. Adding more preservation options would solve precisely nothing :)

The omission applies to names matched at this level. If the wildcard selects a visible subdirectory, `cp -a` still copies hidden entries inside that subdirectory as it descends into it.

## Copy the Contents, Including Hidden Entries

```bash
cp -a source/. contents/
ls -a contents
```

Now **`contents/notes.txt`** and **`contents/.settings`** both exist, without an extra `source` directory.

The `.` in `source/.` means the directory itself, addressed through its current-directory entry. GNU `cp` copies its contents into the existing destination. It does not depend on a wildcard matching each filename.

| Command | Result in these existing destinations |
| --- | --- |
| `cp -a source whole/` | `whole/source/`, including hidden entries |
| `cp -a source/* visible/` | Non-hidden source entries directly in `visible/` |
| `cp -a source/. contents/` | All source entries directly in `contents/` |

When the destination is your current directory, the last form becomes `cp -a source/. .`. Those dots have separate jobs: **`source/.` is the source; the standalone `.` is the destination**.

## Make a Missing Destination Fail Clearly

Stay in the same lab directory. There is no directory named `missing`:

```bash
cp source/notes.txt missing
ls -l missing
```

This succeeds by creating a **regular file named `missing`**. The command cannot infer that you meant a directory.

Try another destination that also does not exist:

```bash
cp source/notes.txt missing-directory/
```

The trailing `/` requires a directory, so this command fails instead of creating a file under the mistaken name. Read the diagnostic; the exact wording varies.

That slash is useful when your intention is “put this file inside an existing directory.” It does not prevent overwriting a file inside a valid destination. Likewise, `cp -a` preserves attributes; it does not turn a copy into a synchronisation operation or remove unrelated destination files.

Before copying, decide whether you want the directory or its contents, whether hidden entries must be included, and whether the destination already exists. Then inspect the resulting level with `ls -a`. A successful command is only useful if it copied what you meant.

### References

- [GNU Coreutils: cp](https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html)
- [GNU cp command reference](https://www.man7.org/linux/man-pages/man1/cp.1@@coreutils.html)
- [Bash filename expansion](https://www.gnu.org/software/bash/manual/html_node/Filename-Expansion.html)
- *Red Hat RHCSA 10 Cert Guide*, Chapter 3: Essential File Management Tools, my study reference.
