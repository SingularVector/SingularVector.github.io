---
title: "PowerShell Logging: New-LogEntry Revisited"
excerpt: "A closer look at the revised New-LogEntry function: predictable output, buffer management, concurrent file writes and optional secret redaction."
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Logging
  - Automation
  - IT-ToolBox
toc: true
header:
  teaser: "/assets/images/PowerShell_Logo.png"
---

## Revisiting New-LogEntry

Logging is one of those things that looks incredibly simple until it isn't.

Writing a timestamp and a message to a file takes a couple of lines of PowerShell. Then you start using the same function in larger automations, have several processes writing to the same file, add buffering, hit a filesystem error or, even worse, discover that you've happily written a password or bearer token into a log file.

At that point things get slightly more interesting.

I've had my `New-LogEntry` function around for quite some time and I've used different versions of it in several scripts and automations. While working on the latest version of **IT-ToolBox** I decided it was finally time to revisit it properly rather than just keep adding bits and pieces to the original function.

The public interface is still very familiar, but quite a lot has changed underneath, particularly around output handling, buffering and concurrent writes.

In this post I'll go through the parts that are actually useful when consuming the function and, more importantly, a few things to be aware of if you're replacing an older copy.

## Getting the current function

The revised standalone implementation is available in the [New-LogEntry directory of PowerShell-Functions](https://github.com/SingularVector/PowerShell-Functions/tree/master/New-LogEntry).

One important difference compared to the old single-file version is that the function is now split into `Private` and `Public` components, so keep the directory intact when downloading or cloning the repository.

From inside the `New-LogEntry` directory you can load it with:

```powershell
. ./New-LogEntry.ps1
```

Simply copying `Public/New-LogEntry.ps1` somewhere else will not work as it depends on the helper functions loaded by the root script.

The standalone version requires PowerShell 7.1 or later.

`New-LogEntry` is also part of [IT-ToolBox 3.0](https://github.com/SingularVector/IT-ToolBox), which has a PowerShell 7.4 baseline. If you're already using the module there is obviously no reason to load the standalone version:

```powershell
Import-Module IT-ToolBox -RequiredVersion 3.0.0
```

All examples below refer to this revised implementation. The older `New-LogEntry` repository is still around, but it should not be considered interchangeable with this version and Windows PowerShell 5.1 is no longer a compatibility target.

Yes, I finally stopped pretending PowerShell 5.1 is going to live forever.

## Start with an explicit log path

The basic use of the function has not really changed:

```powershell
$logPath = Join-Path -Path (Get-Location) -ChildPath 'new-logentry-demo.log'

New-LogEntry -LogMessage 'Inventory started' -LogFilePath $logPath
```

By default the message is appended to the file and displayed in the console.

Each physical line receives its own timestamp and an `INFO`, `WARNING` or `ERROR` tag and files are written using UTF-8 without a byte-order mark.

You can still omit `-LogFilePath`. In that case the function derives the filename from the calling script and the current timestamp, or uses the current directory when called interactively.

That's handy for quick scripts, but for an actual automation I normally prefer to specify the path explicitly:

```powershell
$logPath = Join-Path $PSScriptRoot 'Logs\automation.log'
```

There is another reason for doing this: the default filename is calculated when the function is called. It is not a filename reserved once and automatically reused for the whole execution of your script.

For unattended scripts you will probably also want to suppress console output:

```powershell
New-LogEntry -LogMessage 'Inventory completed' `
    -LogFilePath $logPath `
    -NoConsole
```

## Log messages should not become script results

This was one of the behaviours I particularly wanted to clean up.

A logging function should not unexpectedly put strings into the success pipeline and leave you wondering why the array that was supposed to contain twenty server objects now contains twenty servers and fifteen log messages.

Informational messages displayed in the console therefore use `Write-Host`, while warnings and errors use the corresponding PowerShell streams.

If you actually want the formatted log entry back, you have to explicitly ask for it with `-PassThru`:

```powershell
$entry = New-LogEntry -LogMessage 'Returning this entry deliberately' `
    -LogFilePath $logPath `
    -NoConsole `
    -PassThru

$entry
```

For message severity the preferred syntax is now `-Level`:

```powershell
New-LogEntry -LogMessage 'Optional configuration was not supplied' `
    -Level WARNING `
    -LogFilePath $logPath `
    -NoConsole
```

The old `-IsWarningMessage` and `-IsErrorMessage` switches are still available for compatibility, so existing scripts do not immediately need to be rewritten.

Just don't mix the two approaches. Use either `-Level` or one of the compatibility switches; conflicting combinations are rejected.

There is one PowerShell behaviour here that is worth mentioning.

When console output is enabled, `-Level ERROR` writes to PowerShell's error stream. If your script uses:

```powershell
$ErrorActionPreference = 'Stop'
```

that can turn the log call into a terminating error.

`-NoConsole` suppresses that stream output, but it does **not** hide an actual failure while writing the log file.

That's intentional. A disk write failing and an error message being logged are two very different things and I don't want the former to silently disappear.

## Pipeline input and multiline messages

`New-LogEntry` also accepts messages through the pipeline:

```powershell
$entries = @(
    'Checking server01'
    'Checking server02'
    "Summary`nTwo servers checked"
) | New-LogEntry -LogFilePath $logPath -NoConsole -PassThru

$entries.Count
# 4
```

The multiline message becomes two separate log entries, each with its own timestamp and severity prefix.

I find this much more useful than having a nicely formatted first line followed by an anonymous second line in the log file, especially once you're searching or parsing it later.

Pipeline input is collected and written at the end of the invocation instead of taking the file lock for every individual object.

There is a trade-off though: if you pipe a very long-running operation into `New-LogEntry`, entries are not immediately written one by one.

If you're using logging to follow the progress of something that runs for hours, separate calls at meaningful points in the script make more sense.

## Working with the buffer

The original function had an internal message buffer which I found useful, particularly when collecting diagnostic information that I might only want to save if something goes wrong.

What I didn't particularly like was accessing the internal `$messageBuffer` variable directly.

That becomes especially ugly once the function lives inside a module.

The revised version exposes proper buffer operations instead.

Start by clearing any existing entries:

```powershell
New-LogEntry -ClearBuffer
```

Then add messages without writing them anywhere:

```powershell
New-LogEntry -LogMessage 'Configuration loaded' -BufferOnly

New-LogEntry -LogMessage 'Optional setting missing' `
    -BufferOnly `
    -Level WARNING
```

You can inspect the current buffer with:

```powershell
$bufferedEntries = @(New-LogEntry -GetBuffer)

$bufferedEntries.Count
# 2
```

`-BufferOnly` does exactly what the name suggests: no file write and no console output.

`-GetBuffer` returns the entries without removing them.

When you're ready to write everything:

```powershell
New-LogEntry -FlushBuffer -LogFilePath $logPath -NoConsole

@(New-LogEntry -GetBuffer).Count
# 0
```

After a successful flush the entries are removed from the buffer.

`-ClearBuffer`, on the other hand, simply throws them away. It doesn't flush them first, so use that one with some intention.

One important detail is that this is a buffer belonging to the loaded function's script scope.

It is not a separate queue for every log file and it isn't shared between PowerShell processes.

If you have several unrelated operations sharing the same loaded module instance, they also share that buffer.

## What happens when a write fails

This is one of those things that is very easy not to think about while everything is working.

When flushing the buffer, the function synchronizes taking the buffer snapshot, writing it to disk and removing the entries.

Buffered entries are only removed after the file write succeeds.

So if the write fails:

```text
buffer -> write fails -> buffer remains
```

rather than:

```text
buffer -> write fails -> congratulations, your logs are gone
```

You can therefore correct the problem and retry the flush.

This doesn't magically turn an in-memory buffer into durable storage. If the PowerShell process disappears, the buffer disappears with it.

There is also a less obvious edge case: a filesystem operation can potentially fail after part of the content has already been written.

If you retry in that situation you may get duplicate entries.

So this gives us useful failure handling, not exactly-once delivery.

`New-LogEntry` is still a local logging helper, not Kafka wearing a PowerShell hat.

## Several processes, one file

Another area I wanted to improve was concurrent writing.

It's quite common for an automation to eventually grow into several workers or scheduled tasks writing to the same log file, and simply calling `Add-Content` from all of them and hoping for the best isn't much of a synchronization strategy.

File writes now use a named mutex derived from the resolved log path.

This means processes using this implementation and targeting the same resolved file coordinate their writes, while another log file receives its own lock.

You can control how long the function waits for that lock:

```powershell
New-LogEntry -LogMessage 'Worker completed' `
    -LogFilePath $logPath `
    -LockTimeoutSeconds 10 `
    -NoConsole
```

The default timeout is 30 seconds.

If the mutex cannot be acquired within that period the write fails rather than waiting forever.

The caller then gets to decide whether that means retrying, aborting or doing something else.

There are a few limits worth keeping in mind.

The mutex can only coordinate software that actually uses it. Another application writing directly to the same file knows absolutely nothing about our lock.

It is also not a distributed lock between different machines.

Finally, different paths referring to the same physical file can result in different mutex names, so if multiple processes are writing to one log file, use a consistent path.

## Redacting message content

Logs have an annoying tendency to become accidental credential databases.

Most of the time nobody intentionally writes a password to a log file. It usually gets there inside an exception, HTTP request, debug object or some other value that seemed harmless when the logging code was written.

The revised function therefore has optional secret redaction.

`-RedactSecrets` enables a set of built-in patterns for common cases such as bearer tokens, password assignments and API keys.

You can also supply your own patterns for application-specific data:

```powershell
# All values below are demonstration data.
$message = 'Authorization: Bearer demo-token password=demo-password sessionId=demo-session'

$redactedEntry = New-LogEntry `
    -LogMessage $message `
    -LogFilePath $logPath `
    -RedactSecrets `
    -RedactPattern 'sessionId=\S+' `
    -NoConsole `
    -PassThru

$redactedEntry
```

Redaction happens before the entry is formatted, buffered, written to disk, displayed or returned through `-PassThru`.

The original variable is left untouched.

You can also change the replacement text using `-RedactionText`.

The value is treated literally, including dollar signs. For example using `$0` as your replacement text won't accidentally tell the regular expression engine to put the matched secret back into the log, which would rather defeat the point of the whole exercise.

Obviously this is not magic.

No collection of regular expressions can identify every possible secret in every possible format.

A bare token, some obscure application field or differently structured data may still get through.

The safest password to redact is still the one you never send to the logging function in the first place.

## Testing the behaviour

While rewriting the function I also spent quite a bit of time on the Pester tests.

The current test suite covers formatting, severity levels, pipeline behaviour, buffering, redaction and conflicting parameter combinations.

There are also regression tests around the less exciting things that usually become very exciting at 2 AM: failed writes, retry behaviour, literal replacement strings and automatically generated paths.

For concurrency testing I start three separate PowerShell processes.

Each process writes twenty entries directly and buffers another twenty before flushing them.

At the end I expect exactly 120 distinct messages in the file.

The test verifies that there are no missing or duplicated messages rather than simply checking that a mutex exists somewhere in the code and declaring victory.

The failure tests also create a real filesystem error, verify that buffered entries survive it and then retry against a valid destination.

Those paths are probably less glamorous than checking that:

```powershell
New-LogEntry 'Hello World'
```

works, but they're also the reason I bothered revisiting the function in the first place.

## Closing notes

The complete [implementation, tests and change history](https://github.com/SingularVector/PowerShell-Functions/tree/master/New-LogEntry) are available in my **PowerShell-Functions** repository.

If you're using [IT-ToolBox](https://github.com/SingularVector/IT-ToolBox), the revised function is included there as well.

If you're replacing one of my older versions, there are four things I would check before simply dropping this one into an existing automation:

- the new PowerShell requirement;
- that you're loading the complete implementation rather than only the public function;
- any code directly accessing the old `$messageBuffer`;
- how your script handles PowerShell output and error streams.

The function still has the same name and, for the common use case, still behaves pretty much as you would expect.

There is just considerably more going on underneath now — which is usually what happens to every “simple little helper function” once you've been using it in production for long enough.
