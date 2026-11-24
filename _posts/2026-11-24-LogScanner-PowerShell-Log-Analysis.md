---
title: "LogScanner: Making PowerShell Automation Logs Easier to Search"
excerpt: "Follow a timeout search through synthetic New-LogEntry logs with LogScanner, keeping every match tied to its source and checking what an empty result means."
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

I've used `New-LogEntry` in scripts and automations for years. It gives me a consistent record of what happened, but investigating failures still meant opening files in a text editor and searching manually.

That works. It becomes rather less enjoyable when the question involves several files, a particular severity and a time window. The information is there; finding it again should not become another job.

I built [LogScanner](https://github.com/SingularVector/LogScanner) to make those searches repeatable, with every result tied to its original file and line. My [New-LogEntry article]({{ '/powershell/howto/PowerShell-New-LogEntry-Revised/' | relative_url }}) covers writing the logs. Here, let's ask something of them.

## Start with a question, and two small files

Suppose we want to find **timeout warnings or errors recorded on 5 October**, then inspect the surrounding entries. This is a worked example using the repository's **synthetic logs**, not an account of a production incident.

PowerShell already has `Select-String`, which is often enough for a quick search. What I wanted here was a severity filter that reads the severity field, a time filter that compares timestamps, and a message search that does not accidentally match the prefix.

LogScanner is a small Go CLI using the standard library. There is no database or background service. Building it requires **Go 1.23 or later**; the compiled executable needs neither Go, PowerShell nor .NET on the machine running it.

From a terminal:

```sh
git clone https://github.com/SingularVector/LogScanner.git
cd LogScanner
go build -o bin/logscanner ./cmd/logscanner
./bin/logscanner summary --recursive ./examples/logs
```

On Windows, build with `go build -o bin/logscanner.exe ./cmd/logscanner` and invoke `.\bin\logscanner.exe` instead. The remaining commands use the Linux/macOS spelling, from the repository root. Paths in the output use the operating system's separators.

The sample summary reports two files, twelve parsed entries, no malformed lines and no read errors. Five entries have `ERROR` severity. That gives us a small collection we can inspect ourselves before pointing the tool at anything larger.

## Narrow the search

Ask our question directly:

```sh
./bin/logscanner scan --recursive --min-level warning --contains timeout --ignore-case --since 2026-10-05T00:00:00 --until 2026-10-05T23:59:59 ./examples/logs
```

There are several flags, but they express one request: include subdirectories, keep warnings and errors, look for “timeout” regardless of case, and restrict the recorded date. Put flags before the file or directory paths.

The bundled samples produce two matches:

```text
[10/05/2026 10:18:49 PM] - [WARNING]: Connection timeout; retrying | File: examples/logs/application.log | Line: 3
[10/05/2026 10:18:49 PM] - [WARNING]: Worker TIMEOUT | File: examples/logs/nested/worker.log | Line: 2
```

`--min-level warning` includes `WARNING` and `ERROR`; `--level error` would select only `ERROR`. All supplied filters must match. Neither line above is an error entry, but both deserve a look when investigating a timeout.

Both time bounds are inclusive. A date alone means midnight: `--until 2026-10-05` would exclude these late-evening entries. A small detail, and a convincing way to get an empty report :)

The source timestamps have no timezone. Filters compare the recorded wall-clock values without conversion and reject timezone-bearing arguments. Searching several servers' logs does not automatically put them on the same timeline.

## Follow the match back to its context

The worker result points to line 2 of `examples/logs/nested/worker.log`. Open that file and the surrounding entries are straightforward:

```text
[10/05/2026 10:18:49 PM] - [INFO]: Worker started
[10/05/2026 10:18:49 PM] - [WARNING]: Worker TIMEOUT
[10/05/2026 10:18:49 PM] - [ERROR]: Worker failed
```

The timeout search did not return “Worker failed”, because that message does not contain “timeout”. It did give us the place to look next.

That distinction matters more with real logs. A matching entry is a lead, not a diagnosis. These synthetic entries share a timestamp and contain no job identifiers, so they cannot demonstrate timing, establish a cause or reliably connect separate jobs. A search tool cannot recover context the automation never recorded.

## Keep the result useful

To pass those same matches to another tool, add `--output jsonl`:

```sh
./bin/logscanner scan --recursive --min-level warning --contains timeout --ignore-case --since 2026-10-05T00:00:00 --until 2026-10-05T23:59:59 --output jsonl ./examples/logs > timeouts.jsonl
```

Each line is a JSON object with the timestamp, severity, message, source file, line number and original text. We can process the result without scraping the terminal display, and still return to the source. The timestamp retains its original format; it does not imply UTC.

An empty result needs more care. LogScanner sends results to standard output and diagnostics to standard error. Malformed lines are skipped and counted; read failures are reported. Add `--strict` when malformed input should make the command fail.

The compiled executable returns:

| Code | Meaning |
| --- | --- |
| `0` | At least one match, with no fatal errors |
| `1` | No matches, with no fatal errors |
| `2` | Invalid arguments, discovery/read/output failure, or malformed lines with `--strict` |

Finding an `ERROR` entry does not itself produce code `2`: the code describes the search outcome, not the health of the automation. If a wrapper only keeps standard output, it can lose the very explanation needed to interpret an empty file. Use the compiled executable when checking these codes; `go run` wraps nonzero exits.

## Know what the files can tell us

The supported input is the current `New-LogEntry` format in UTF-8, with `MM/dd/yyyy` dates and a 12-hour clock. Historical variants, localised timestamps and UTF-16 files need compatibility checks. Untagged entries become `UNSPECIFIED` and are excluded by minimum-severity filters.

Each physical line is a separate entry, including lines from a multiline message. Results retain source order rather than a global timestamp sort. The tool reads incrementally, but does not tail live logs or read compressed archives. The [repository documentation](https://github.com/SingularVector/LogScanner#usage) covers the other filters and options.

For our small investigation, we have two timeout warnings and know exactly where to inspect them. That is the useful outcome: less time hunting through files, with enough traceability to check what a result actually means.

Try the bundled samples first, then a representative log from your own automation. Testing and feature requests are welcome; drop me a line or leave a comment, and I will be happy to take a look.
