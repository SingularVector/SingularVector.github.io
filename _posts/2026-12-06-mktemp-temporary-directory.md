---
title: "mktemp: Give Your Script Its Own Temporary Directory"
slug: mktemp-temporary-directory
date: 2026-12-06
categories:
  - Linux
tags:
  - bash
  - scripting
  - linux
  - temporary-files
description: "Create a private temporary directory with mktemp, understand its filename template, and clean up a Bash script's workspace when it exits."
---

A script needs somewhere to unpack an archive or prepare a report. `/tmp/report` sounds reasonable, until another run uses the same directory. Or yesterday's files are still there, patiently waiting to become today's input.

We could keep inventing directory names, but there is a command for that already :)

## Let mktemp Create It

[`mktemp`](https://man7.org/linux/man-pages/man1/mktemp.1.html) creates a temporary file or directory and prints its path. With `-d`, we get a directory:

```bash
# Create a unique directory inside TMPDIR, or /tmp if TMPDIR is unset or empty.
# Capture its path so later commands use the directory actually created.
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/sv-report.XXXXXX")
```

There are three separate pieces here. `XXXXXX` is the part `mktemp` replaces with random characters. `${TMPDIR:-/tmp}` chooses the parent directory. `$(...)` captures the command's output into `work_dir`.

Importantly, the command **creates** the directory; it does not just suggest an unused name. Ordinary permissions make it private to its owner, subject to any stricter `umask`. The parent directory must already exist and be writable.

That solves the shared-name problem. It does not make the contents disappear when we finish.

## Give the Workspace an Exit Plan

For a standalone **Bash script on Linux**, we can check creation and register cleanup together. Save this as a script and run it with `bash`; it contains `exit`, so do not paste it into your interactive shell as a single block.

```bash
#!/usr/bin/env bash

# Stop before doing any work if a temporary directory cannot be created.
if ! work_dir=$(mktemp -d "${TMPDIR:-/tmp}/sv-report.XXXXXX")
then
    printf 'Could not create the temporary workspace.\n' >&2
    exit 1
fi

# Remove only this run's workspace; keep work_dir unchanged after creation.
cleanup()
{
    rm -rf -- "$work_dir"
}

trap cleanup EXIT

# Stand-in for the report preparation work.
printf 'Report prepared\n' > "$work_dir/report.txt"
cat "$work_dir/report.txt"
```

The `if` checks whether creation succeeded. `>&2` sends the failure message to standard error. We register the `EXIT` trap only after obtaining a valid path.

The trap calls `cleanup` when Bash exits, including through an explicit `exit`. The quotes preserve the path as one argument, and `--` ends option parsing for `rm`. The recursive removal is deliberate: this directory holds only the scratch files created by this run. Do not repoint the variable at a shared directory.

An `EXIT` trap cannot handle every interruption, including `SIGKILL` or a machine crash. It also removes our workspace after an ordinary failed run, so copy out anything needed for diagnosis before exiting.

Temporary means disposable, not automatically deleted. Let `mktemp` create the workspace, check that it succeeded, and make its lifetime explicit.

### Further Reading

- [mktemp command reference](https://man7.org/linux/man-pages/man1/mktemp.1.html)
- [Bash manual: expansions and the trap builtin](https://man7.org/linux/man-pages/man1/bash.1.html)
