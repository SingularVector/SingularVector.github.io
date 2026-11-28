---
title: "Why Does sort Put 10 Before 2?"
slug: sort-numbers-as-numbers
date: 2026-12-08
categories:
  - Linux
tags:
  - linux
  - shell
  - coreutils
description: "Understand numeric sorting with sort -n, reverse the order with -r, and choose a report column with -k, one step at a time."
---

Suppose a script produces a list of counts. You pass it through `sort`, expecting the smallest number first, and get `1`, `10`, `2`.

We have apparently broken counting. A promising start :)

The command is doing what we asked, but we left out one detail: those lines should be compared as numbers. Let's see the difference with a small file.

## Those Numbers Are Still Text

Using your text editor, create a new file called `numbers.txt` in a practice directory, with one number per line:

```text
2
10
1
```

Open a Linux terminal in that directory and run:

```bash
# Display the file's lines in text order.
sort numbers.txt
```

```text
1
10
2
```

`sort` reads the file and displays its lines in order. It leaves the original file unchanged.

By default, it compares text. Here, `10` comes before `2` because its first character is `1`. To us these are quantities; to the command they are still lines of text.

## Tell sort These Are Numbers

The `-n` option tells `sort` to compare **numeric values**. Add it between the command and the filename:

```bash
# Compare the numbers, with the smallest first.
sort -n numbers.txt
```

```text
1
2
10
```

That looks rather more reassuring. The input file has not changed; we have changed how the command compares its contents.

If you want the largest number first, add `-r`, which means **reverse the order**:

```bash
# Keep the numeric comparison, but reverse the result.
sort -n -r numbers.txt
```

```text
10
2
1
```

Keeping `-n` and `-r` separate makes each instruction visible: compare numbers, then put the largest first. Reversing text order alone would still give us the wrong answer.

## Choose a Column with -k

What if the numbers have names beside them? Create another practice file, `jobs.txt`, containing:

```text
backup 2
cleanup 10
inventory 1
```

Each line has two **fields**: the job name is field **1**, and the count is field **2**. Here, spaces separate the fields; `sort` also recognizes tabs by default. Field numbers start at one.

The `-k` option chooses the **key**, meaning the part of each line used for comparison. To compare the second field:

```bash
# Compare field two, keeping each complete line together.
sort -k 2,2 jobs.txt
```

```text
inventory 1
cleanup 10
backup 2
```

Why write `2,2`? The numbers describe a range:

- The first `2` means **start at field two**.
- The second `2` means **end at field two**.

We are selecting one field, not asking the command to sort it twice. Writing only `-k 2` would select everything from field two to the end of the line, including any later columns.

Notice that `10` still comes before `2`. Choosing a field does not change how its contents are compared. We already know the option for that:

```bash
# Compare field two as a number, with the smallest count first.
sort -n -k 2,2 jobs.txt
```

```text
inventory 1
backup 2
cleanup 10
```

The job names move with their counts. `-k` chooses **what to compare**; `-n` chooses **how to compare it**. Add the familiar `-r` if you want the largest count first.

Our sample has no header and no spaces inside the job names. A longer name such as `daily backup` would occupy two fields, so check the actual input before counting columns.

## Try It on /etc/passwd

On Linux, try sorting the local account file:

```bash
sort /etc/passwd
```

You can pipe the file through `cat`, but `sort` can read it directly. The output looks like it is sorted by username because each line starts with the username. That also explains the result when every username is lowercase. Plain `sort` compares the whole line as text, starting at the left.

Imagine the file contained these two entries:

```text
alice:x:1002:1002:Alice:/home/alice:/bin/bash
bob:x:1001:1001:Bob:/home/bob:/bin/bash
```

Plain `sort` puts Alice first. To put Bob first by sorting on the user ID (UID), count the fields from the left. The username is field one, `x` is field two, and the UID is field three. This time the fields are separated by colons, so we need `-t ':'` to tell `sort` where to split each line.

```bash
# Split each line at colons and compare field three as a number.
sort -t ':' -k 3,3 -n /etc/passwd
```

`-k 3,3` starts and ends at the UID, and `-n` puts the smaller number first. In our two-line example, that means Bob's `1001` comes before Alice's `1002`. Both commands display the result and leave the file alone.

### Further Reading

- [GNU Coreutils: sort command reference](https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html)
