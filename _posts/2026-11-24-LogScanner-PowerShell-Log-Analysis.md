---
title: "LogScanner: Making PowerShell Automation Logs Easier to Search"
excerpt: "Why I built a small Go CLI to search New-LogEntry logs by severity, message and time, with traceable results and JSON Lines output."
date: 2026-11-24 08:00:00 +0100
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Go
  - Logging
  - Automation
  - LogScanner
  - IT-ToolBox
toc: true
---

## Writing the logs was only half the job

In [PowerShell Logging: New-LogEntry Revisited](/powershell/howto/PowerShell-New-LogEntry-Revised/), I went through the changes to my logging function: predictable output, buffering, coordinated file writes and optional secret redaction.

That dealt with getting useful information into a file. Finding it again was still a separate job.

I've used `New-LogEntry` in scripts and automations for years. Investigating failures across those logs meant opening files in a text editor and searching manually. That works, but it becomes repetitive when the question involves several files, a particular severity and a specific time window.

I built [LogScanner](https://github.com/SingularVector/LogScanner) to make that investigation repeatable from the command line, while keeping every result tied to the file and line it came from.

## Why a separate tool?

PowerShell already has `Select-String`, and Linux has perfectly useful tools for searching text. For a quick search, those are often enough.

What I wanted here was a tool that understands the structure of the logs my function produces. A severity filter should inspect the severity field. A time filter should compare parsed timestamps. A message search should examine the message rather than accidentally matching something in its prefix.

LogScanner is a small Go CLI built using the standard library. It reads local files, applies filters and writes results to the terminal or to another command. There is no database or background service to configure, and a compiled executable does not need PowerShell, .NET or Go installed on the machine running it.

It understands one log format. That keeps the scope manageable and the behavior explicit.

## Start with the included examples

The repository includes synthetic logs generated with `New-LogEntry`, so you can try the tool without supplying production data.

To build from source, you need Go 1.23 or later:

```sh
git clone https://github.com/SingularVector/LogScanner.git
cd LogScanner
go build -o bin/logscanner ./cmd/logscanner
./bin/logscanner summary --recursive ./examples/logs
```

On Windows, build and run the executable from PowerShell:

```powershell
go build -o bin/logscanner.exe ./cmd/logscanner
.\bin\logscanner.exe summary --recursive .\examples\logs
```

The recursive summary of the bundled samples is:

```text
Files: 2
Parsed entries: 12
Matches: 12
Malformed lines: 0
Read errors: 0
INFO: 4
WARNING: 2
ERROR: 5
UNSPECIFIED: 1
```

For the remaining examples, I'm using `./bin/logscanner` from the repository root. On Windows, use `.\bin\logscanner.exe` instead. If you put the executable on your `PATH`, you can call it as `logscanner`.

## Find the errors, then narrow the question

Start with errors across the example directory and its subdirectories:

```sh
./bin/logscanner scan --recursive --level error ./examples/logs
```

One of the matching lines looks like this:

```text
[10/05/2026 10:18:49 PM] - [ERROR]: Connection refused | File: examples/logs/application.log | Line: 4
```

The original entry remains readable, with its source path and one-based line number attached. You can go back to the surrounding entries when the matching line alone doesn't explain the failure. Path separators follow the operating system.

For a more specific question, look for timeouts at warning severity or above:

```sh
./bin/logscanner scan --recursive --min-level warning --contains timeout --ignore-case ./examples/logs
```

That matches two entries in the bundled samples. All supplied filters must match, and the text filter applies to the message itself.

`--level error` means exactly `ERROR`. `--min-level warning` includes `WARNING` and `ERROR`. Entries written without a severity tag are classified as `UNSPECIFIED` and excluded by minimum-severity filters.

Place flags before file or directory paths. You can also pass several paths, or use `--include "worker-*.log"` when discovering files in directories. Quote the pattern so the shell doesn't expand it first.

## Restrict the time window

This example selects errors recorded during 5 October 2026:

```sh
./bin/logscanner scan --recursive --level error --since 2026-10-05T00:00:00 --until 2026-10-05T23:59:59 ./examples/logs
```

Both bounds are inclusive. A date without a time means midnight, so `--until 2026-10-05` does **not** include the whole of that day.

There is another limitation inherited from the source format: its timestamps do not contain a timezone. LogScanner compares the recorded wall-clock values without converting them, and rejects timezone-bearing filter arguments. It cannot automatically align logs written in different timezones.

## Keep the output useful outside the terminal

Readable output is useful while investigating. For further processing, JSON Lines avoids having to parse the display format again:

```sh
./bin/logscanner scan --recursive --level error --output jsonl ./examples/logs > errors.jsonl
```

Each matching entry becomes one JSON object with a timestamp, severity, message, source file, line number and the original log text. The timestamp remains in its source format; it does not imply UTC.

If you only need counts, use `summary`:

```sh
./bin/logscanner summary --recursive --level error ./examples/logs
```

For the bundled samples, that reports twelve parsed entries and five matches. Severity counts describe the matching entries; the parsed-entry count includes every entry successfully parsed during the scan.

## A clean result needs a clean scan

An empty search result is only useful if the files were actually read successfully.

LogScanner sends results to standard output and diagnostics to standard error. Malformed lines are skipped and counted. File read failures are also reported, while scanning continues through other files where possible.

Use `--strict` when malformed input should make the command fail:

```sh
./bin/logscanner scan --recursive --strict --level error ./examples/logs
```

The executable uses these exit codes:

| Code | Meaning |
| --- | --- |
| `0` | At least one match, with no fatal errors |
| `1` | No matches, with no fatal errors |
| `2` | Invalid arguments, discovery/read/output failure, or malformed lines with `--strict` |

Finding an `ERROR` entry therefore does not itself produce exit code `2`. The code describes the search outcome, not the health of the automation that wrote the log.

Use the compiled executable when handling these codes in scripts. `go run` wraps nonzero program exits.

## Boundaries worth knowing

The supported format is the timestamped UTF-8 output of the current `New-LogEntry` formatter:

```text
[10/05/2026 10:18:49 PM] - [ERROR]: Connection refused
```

The date is `MM/dd/yyyy`, with a 12-hour clock and AM/PM marker. Older variants, localized timestamps and UTF-16 files need compatibility checks; LogScanner does not support those formats automatically.

Multiline messages are another detail carried over from the logger. `New-LogEntry` prefixes each physical line separately, and LogScanner treats each as an independent entry. The file doesn't record enough information to reconstruct the original message grouping.

The reader processes input incrementally, including lines larger than 64 KiB. It does not load the whole log into memory. Results retain source order rather than being globally sorted by timestamp, and the current version works with local, uncompressed files. It does not tail live logs or read compressed archives.

The repository has automated tests and CI covering Windows, Linux and macOS, including parsing, filtering, JSON output and executable exit behavior. That matters for a tool whose usefulness depends on giving the same answer to the same question.

## Where it fits

`New-LogEntry` gives my automations a consistent way to record what happened. LogScanner gives me a repeatable way to ask questions of those records afterwards.

If you're already using the revised logging function, the [LogScanner repository](https://github.com/SingularVector/LogScanner) includes the source, sample logs and full command reference. Try the samples first, then check a representative file from your own automation before scanning a larger collection.

Testing and feature requests are always welcome so drop me a line and I will be happy reply back or implement it!
