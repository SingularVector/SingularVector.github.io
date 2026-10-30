---
title: "Rebuilding Remove-OldFiles: Find First, Delete Later"
date: 2026-11-10
categories:
  - PowerShell
  - DevOps
tags:
  - automation
  - retention
  - PowerShell
  - engineering
  - Remove-OldFiles
description: "Revisit a real PowerShell cleanup solution: make retention rules explicit, protect the right folders and produce a report worth reading before deleting anything."
---

I had a lot of log files lying around. Different automations, different retention periods, and other teams asking whether the same cleanup could work for them too.

That was the practical problem behind [my 2018 cleanup article]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %}) and the [Remove-OldFiles repository](https://github.com/SingularVector/Remove-Old-Files). A CSV held the rules, and a file named `ignore` let us protect particular folders. It was useful because supporting another location did not mean writing another script.

Years later, it makes a good place to put [From a Script to a Tool]({% post_url 2026-11-07-from-a-script-to-a-tool %}) into practice. There is already a real requirement, some useful design, and code written by someone who apparently expected me to remember all his assumptions.

Unfortunately, that someone was me :)

## Keep the Idea, Make the Rules Clear

I wanted to keep configuration outside the code and eventually replace the CSV with a SQL table. Before changing where the rules lived, though, I needed to be clear about what they meant.

“Delete logs older than 30 days” sounds precise until you ask which timestamp counts. Creation time? Last write? What about a file exactly on the boundary?

The rebuilt module uses `LastWriteTimeUtc`, strictly earlier than the run's cutoff. A file exactly on that cutoff stays. This describes eligibility; it does not tell us whether an application still needs the file. Choosing the retention policy remains our responsibility.

Recursion needed the same attention. The old code could treat a nonempty `0` as enabled. A perfectly reasonable-looking CSV could therefore mean something different to PowerShell than it meant to the person editing it. That is the sort of detail I want to find in a review, rather than through an enthusiastic cleanup job.

## Look Before Removing Anything

The module separates inspection from execution. Here is a local policy for a disposable Windows folder, using PowerShell 7.4 or later:

```powershell
Import-Module ./src/RetentionEngine/RetentionEngine.psd1 -Force

$policy = [pscustomobject](
    @{
        PolicyId      = 'automation-logs'
        RootPath      = 'C:\RetentionLab'
        FilePattern   = '*.log'
        RetentionDays = 30
        Recurse       = $true
        Enabled       = $true
    }
)

$report = Get-RetentionReport -Policy $policy

$report | Select-Object Status, CandidateCount, CandidateBytes, ErrorCount
```

The folder must already exist. This command reports candidates; it removes nothing.

A regular `ignore` file protects its containing directory and everything below it. The walker stops at that boundary instead of visiting all the descendants and filtering them afterwards. Links and reparse points are skipped, linked roots or ancestors are rejected, and hidden files are included unless otherwise excluded.

Those are deliberate choices. The important thing is being able to explain them before someone points the module at a folder they care about.

## A Report Someone Will Actually Read

PowerShell objects are useful for another automation. For a colleague reviewing a cleanup scope, I wanted something easier to open and discuss.

```powershell
Export-RetentionReportHtml -Report $report -LiteralPath C:\Reports\retention.html
```

Use an existing output directory outside the cleanup scope. The [synthetic sample report]({{ '/assets/reports/retention-rebuild/sample-retention-report.html' | relative_url }}) shows the result without using production data. It is a standalone HTML file with embedded CSS, so nobody needs access to a dashboard just to read it.

The first thing to check is the outcome. Zero candidates can mean there was nothing to remove; it can also accompany an incomplete scan. Errors deserve attention before an attractive storage figure does. Candidate bytes are observed file lengths, not a promise about reclaimed disk space.

I also do not need thousands of rows telling me that today's logs are too young or that a text file did not match `*.log`. The HTML leaves those routine exclusions out of the detail list, while keeping aggregate counts and the full structured result. Protected folders and skipped links remain visible. Detail sections collapse, and errors open automatically when present.

A report should help me find the problem, not give me another one to read through.

## Then Earn the Delete Switch

Actual cleanup requires `Invoke-RetentionCleanup -Execute`; without that switch, it plans. `-Execute -WhatIf` previews the execution path without deleting files.

Execution scans again rather than trusting yesterday's report. An incomplete scan blocks deletion for that rule. Each candidate is rechecked before and after confirmation, including its scope, protection markers, timestamp and length. A prompt can sit open while someone gets coffee. The filesystem rarely agrees to wait with them.

These checks reduce ordinary surprises; they do not lock the filesystem or make deletion reversible. The test suite uses disposable files and fixed timestamps to check selection boundaries, protection and failure paths. Real Windows permissions, locks and SQL access still need acceptance testing in the intended environment.

That gives us a useful foundation: explain the selection, inspect the result, and require an explicit decision to remove anything. In [the second part]({% post_url 2026-11-12-remove-oldfiles-when-a-report-becomes-a-delete %}), the rules move into SQL Server—with a little less architecture than I briefly thought we needed.

### Further Reading

- [Original cleanup article]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %})
- [Implementation and operations guide](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/implementation-guide.md)
