---
title: "Extract It Where? Making Sense of tar Archives"
date: 2026-12-01
published: false
categories:
  - Linux
tags:
  - linux
  - rhcsa
  - tar
  - filesystems
description: "Create, inspect and extract tar archives with deliberate destination paths. Use -C to reduce accidental overwrites, and understand its security limits."
---

An archive has a filename. Its contents have filenames too. When you extract it, those names need somewhere to go.

That last detail deserves more attention than it usually gets. `tar -xvf backup.tar` can be perfectly valid syntax and still put files somewhere you did not intend. Run it in a working directory full of useful files, and the archive may have a few opinions about replacing them.

For this instalment of my RHCSA preparation series, let’s create an archive, inspect what it contains, and extract it into a directory we deliberately choose. The option worth remembering is **`-C`**.

## Build a Small Archive We Can Explain

These examples target GNU tar on a RHEL lab machine. Use your ordinary account and a new practice directory:

```bash
mkdir ~/rhcsa-tar-lab
cd ~/rhcsa-tar-lab
mkdir bundle
echo 'archived revision' > bundle/notes.txt
tar -cvf notes.tar bundle
```

Choose a different practice directory name if it already exists. Run the examples in order; all deliberate overwrites below happen inside this lab directory.

The options are easier to read when each has a job:

| Option | Job |
| --- | --- |
| `-c` | Create an archive |
| `-t` | List its contents |
| `-x` | Extract its contents |
| `-v` | Show processed filenames |
| `-f` | Specify the archive filename |
| `-C` | Change tar’s working directory |
| `-z`, `-j`, `-J` | Use gzip, bzip2 or xz compression when creating |

In `-cvf notes.tar`, the archive filename follows `f`. `bundle` is what we put inside it. No compression has happened yet.

## Look Before Extracting

```bash
tar -tvf notes.tar
```

The listing includes `bundle/` and `bundle/notes.txt`, together with metadata. It does not say that the archive must be restored into your home directory or back to its original location.

The stored pathname is **relative**. If you extract in `/home/student`, it becomes `/home/student/bundle/notes.txt`. Extract in another directory, and that destination changes.

GNU tar normally removes a leading `/` when archiving absolute paths. Archiving `/etc` therefore normally stores names such as `etc/hosts`. A restore into `/tmp` would produce `/tmp/etc/hosts`, not `/etc/hosts`.

An archive listing helps you understand names and layout. It does not establish that a downloaded archive is trustworthy.

## Make the Destination Explicit with `-C`

```bash
mkdir restored
tar -xvf notes.tar -C restored
cat restored/bundle/notes.txt
```

The output is `archived revision`. The directory must already exist; tar creates the archived subdirectories beneath it.

`-C restored` changes tar’s working directory for extraction. Your shell stays in the lab directory. Changing directory yourself before extracting also works, but `-C` records the destination in the command you can read and review.

| Stored member | Extraction directory | Resulting path |
| --- | --- | --- |
| `bundle/notes.txt` | `restored` | `restored/bundle/notes.txt` |
| `etc/hosts` | `/tmp/restore-check` | `/tmp/restore-check/etc/hosts` |

`-C` does not flatten the archive or remove its directory structure.

## Why This Is a Safety Habit

Let’s demonstrate an overwrite using only disposable files:

```bash
mkdir working
mkdir working/bundle
echo 'local changes worth keeping' > working/bundle/notes.txt
tar -xvf notes.tar -C working
cat working/bundle/notes.txt
```

The local changes have been replaced by `archived revision`. We explicitly chose `working`, and tar obeyed. **The important combination is an explicit destination and a fresh, empty directory.**

For an archive you did not create, an extraction directory should be under your control, with parent directories that untrusted users cannot modify. Use a separate empty directory for each archive, and extract with your ordinary account. This avoids mixing archive contents with existing work and reduces opportunities involving pre-existing symbolic links. GNU tar’s [security guidance](https://www.gnu.org/software/tar/manual/html_section/Security.html) recommends this approach.

The empty directory provides room to inspect filenames, links and contents before deciding what belongs in a live location. Root privileges would give mistakes a much larger area to work in. They are unnecessary for inspecting a bundle of text files.

**`-C` is a destination selector, not a sandbox.** It does not stop an archive from containing unsafe software, restrict the process to that directory, or make extraction immune to vulnerabilities. Your account can still write elsewhere where its permissions allow. GNU tar has its own pathname protections; do not casually disable them with options such as `-P`, which preserves absolute names.

For genuinely untrusted material, use an appropriately isolated environment and current tools. A directory named `safe` has no special powers, however reassuring the name looks :)

## Restore One File, Keeping Its Stored Path

You do not need to unpack everything to recover one member:

```bash
mkdir selected
tar -xvf notes.tar -C selected bundle/notes.txt
cat selected/bundle/notes.txt
```

Use the member name shown by `tar -t`: here, `bundle/notes.txt`, rather than just `notes.txt`. The result still includes the `bundle` directory.

If the archive has an unfamiliar extension, `file notes.tar` can help identify its format. Extensions are useful labels; they are not evidence about the contents.

## Add Compression Without Changing the Restore Habit

Create a gzip-compressed archive directly:

```bash
tar -czvf notes.tar.gz bundle
tar -tvf notes.tar.gz
mkdir restored-gzip
tar -xvf notes.tar.gz -C restored-gzip
```

GNU tar detects the compression when listing or extracting this archive file, so the extraction command does not need `-z`. You still need `-x` and the archive filename after `-f`.

For creation, `-j` selects bzip2 and capital `-J` selects xz. Compression reduces size; it does not encrypt the archive. Which compression format you choose does not change the need to inspect paths and choose a destination.

## `-C` Helps When Creating Archives Too

You can also choose where tar looks for the files being archived:

```bash
tar -cvf flat-notes.tar -C bundle notes.txt
tar -tvf flat-notes.tar
```

This archive contains `notes.txt`, without the `bundle/` prefix. `-C bundle` changes the directory before tar processes the following filename. We have made a different archive layout deliberately, rather than discovering it during restoration.

For revision, explain three things before pressing Enter: **which archive, which stored paths, and which destination**. Inspect with `-t`, extract into a fresh directory with `-C`, then verify the result. That habit is useful long after you have forgotten the date of your exam.

### References

- [GNU tar: tutorial and extraction examples](https://www.gnu.org/software/tar/manual/html_chapter/Tutorial.html)
- [GNU tar: choosing files and stored names](https://www.gnu.org/software/tar/manual/html_chapter/Choosing.html)
- [GNU tar: position-sensitive options, including -C](https://www.gnu.org/software/tar/manual/html_node/Position_002dSensitive-Options.html)
- [GNU tar: security guidance](https://www.gnu.org/software/tar/manual/html_section/Security.html)
- [GNU tar manual](https://www.gnu.org/software/tar/manual/tar.html)
- *Red Hat RHCSA 10 Cert Guide*, Chapter 3: Essential File Management Tools, my study reference.
