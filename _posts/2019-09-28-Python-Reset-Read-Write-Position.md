---
title: "Reset Read or Write position in a file with Python with seek()"
excerpt: "How do I go back to the beginning of file after reading it with the read() method in Python?"
toc: true
categories:
  - Python
tags:
  - Python
  - Seek
  - Read
  - Python IO
  - Python file management
last_modified_at: 2026-11-02
---

This is something I used to stumble over early in my Python work: read a file, read it again, and get an empty string. The text has not disappeared. The open stream is already positioned at its end.

## Read, rewind, read again

Use a context manager so the file closes when the block finishes:

```python
with open("message.txt", "r", encoding="utf-8") as source:
    first_read = source.read()
    second_read = source.read()
    source.seek(0)
    repeated_read = source.read()

assert second_read == ""
assert repeated_read == first_read
```

Choose the encoding appropriate to the file rather than relying on the machine's default. `read()` without a size reads the remaining content, advancing the current position. At end-of-file, another text read returns `""`.

`seek(0)` resets the stream to the start; its default `whence` is zero, so `seek(0, 0)` expresses the same operation. This assumes a seekable stream: a pipe or other non-seekable input may not support it.

In an interactive Python shell, evaluating a string shows its representation, including escape sequences such as `\n`. `print(first_read)` displays the text with newlines. That difference is display behaviour, not a change to the file.

## Text positions are not arbitrary byte offsets

The earlier article described relative and end-relative offsets without distinguishing text from binary streams. For a text file, use zero or a position previously returned by `tell()`:

```python
with open("message.txt", "r", encoding="utf-8") as source:
    first_line = source.readline()
    position = source.tell()
    remainder = source.read()
    source.seek(position)
    assert source.read() == remainder
```

The value from `tell()` is a position cookie for the text stream, not necessarily a character count. Nonzero offsets relative to the current position or end are not supported in ordinary text mode. Encoding and newline translation make arbitrary arithmetic on those positions unreliable.

## Binary streams use byte positions

```python
import os

with open("payload.bin", "rb") as source:
    source.seek(2, os.SEEK_SET)
    source.seek(1, os.SEEK_CUR)
    source.seek(-1, os.SEEK_END)
    last_byte = source.read(1)
```

This example assumes a seekable file with at least one byte; the final operation reads its last byte. For a text parser, do not switch to byte offsets and assume that landing in the middle of a multibyte character is valid.

Rewinding also does not erase or truncate a file opened for updating. Writing, truncating and append-mode behaviour are separate concerns. For a large sequential input, processing it once or reopening it may be a better design than keeping all content in memory and repeatedly rereading it.

Reference: Python's [I/O documentation](https://docs.python.org/3/library/io.html#io.TextIOBase.seek).
