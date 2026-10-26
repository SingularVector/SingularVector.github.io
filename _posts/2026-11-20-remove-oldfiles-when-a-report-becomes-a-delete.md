---
title: "Rebuilding Remove-OldFiles: When a Report Becomes a Delete"
date: 2026-11-20
categories:
  - PowerShell
  - DevOps
tags:
  - automation
  - retention
  - PowerShell
  - testing
  - Remove-OldFiles
description: "Add deliberate cleanup execution with a read-only default, PowerShell confirmation and fresh checks for changed files and protected directories."
---

The report looks right. You have checked the paths, the ages and the exclusions. Time to delete the files?

Perhaps. But the report tells you what was there when you scanned. It cannot promise that nothing changed while you were reading it.

A file might have been written again. Someone might have added an `ignore` marker. And a confirmation prompt can sit open for considerably longer than the person who wrote the script expected. There is always a coffee somewhere in this process :)

After [migrating the CSV policies]({% post_url 2026-11-16-remove-oldfiles-keeping-policies-fixing-assumptions %}), the next step is controlled execution. The interesting part is what must happen before we call `Remove-Item`.

---

## Keep the Default Boring

The new command takes one policy, using the same model as the reporting engine:

```powershell
$result = Invoke-RetentionCleanup -Policy $policy
$result.Actions
```

That produces a plan. It deletes nothing.

To enter the execution path, you must explicitly request it. Preview it first:

```powershell
$preview = Invoke-RetentionCleanup -Policy $policy -Execute -WhatIf
$preview.Actions
```

The command uses PowerShell’s `ShouldProcess`. `-WhatIf` describes the proposed removals without invoking them; normal execution has a high confirmation impact, so the default preferences ask before each file.

On a deliberately disposable test scope, actual execution is:

```powershell
$execution = Invoke-RetentionCleanup -Policy $policy -Execute
```

An unattended job can intentionally suppress prompts with `-Confirm:$false`, but it still needs `-Execute`. Preview and execution are separate choices, and the default should not surprise someone trying the command for the first time.

---

## Start with a Fresh Scan

The command does not accept a saved report as a deletion list. It scans the policy again.

If inspection is incomplete or fails, execution is blocked for the entire policy. We can keep a partial report for investigation without pretending it is a complete basis for cleanup.

This first execution milestone also handles one policy at a time. Automatic CSV batch deletion is not implemented. The [CSV overlap rules]({% post_url 2026-11-16-remove-oldfiles-keeping-policies-fixing-assumptions %}) still matter; iterating accepted rows from an invalid import would simply work around the question we deliberately stopped to ask.

---

## Check Again After the Prompt

For each candidate, the command checks its scope and directory ancestors, looks for new ignore markers, and confirms that the entry is still a regular file with the same length and last-write timestamp. It must still be older than the scan’s cutoff.

Then comes confirmation.

And then the checks run again, immediately before removal. Checking only before the prompt would leave the time spent answering it outside the protection we were trying to provide.

Changed or newly protected files are skipped with a reason. Failed checks and removal errors are recorded as failures. A directory substituted for a candidate file does not become a new directory-removal instruction.

This does not lock the filesystem. A replacement with identical metadata can escape detection, and something can still change after the final check. It reduces ordinary operational surprises; it is not an atomic or hostile-environment deletion guarantee. The [execution documentation](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/controlled-cleanup.md) makes those limits explicit.

---

## Count What Happened

The result records planned, deleted, skipped and failed actions. The deletion count increases only after the removal command succeeds. Observed file lengths are useful evidence, but still not a measurement of disk space actually freed.

There is also a small reporting trap. Our HTML exporter says “no files deleted,” which is correct for a reporting scan. Reusing that wording after execution would be misleading.

For now, an execution snapshot is explicitly marked, and the report-only HTML exporter refuses it. Export the plan before running; keep the execution result as structured evidence afterwards. A dedicated HTML execution receipt can come when we define what it should communicate.

## Leave a Useful Trail

Once this runs unattended, the returned object is only useful if something keeps it. Tomorrow’s question will be “what happened to that file?”, and terminal history is unlikely to have a convincing answer.

This is where my [New-LogEntry]({% post_url 2026-10-24-PowerShell-New-LogEntry-Revised %}) function belongs in the surrounding automation: recording the run identifier, policy, final status and individual outcomes. Log a deletion after it succeeds, not when we merely intend to try it. Keep failures and skipped files visible too; a healthy-looking total can hide a rather unhealthy run.

The rebuilt engine currently returns structured results; it does not call `New-LogEntry` automatically. A scheduled wrapper can consume those results and persist them without mixing log messages into the data stream. Logging failures also need to be surfaced—a missing log must not make a failed cleanup appear successful.

---

## What We Actually Exercised

The combined local suite passed **99 checks, with three platform-dependent skips**, on macOS with PowerShell 7.6.7 and Pester 5.7.1. Real deletions targeted disposable fixtures only.

The new checks cover the read-only default, preview, explicit removal, incomplete scans, failure accounting, changed metadata, new ignore markers and directory substitution. Controlled mocks also verify the second check around confirmation. Windows locks, ACLs and a network share still need their own environment-specific checks.

We now have a path from policy to observed candidates to an explicit action, with a result that says what happened. Before centralising that across more machines, I want to keep that chain understandable. A central database will not make an unexplained deletion any easier to defend.

### Further Reading

- [Controlled cleanup contract](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/controlled-cleanup.md)
- [Find First, Delete Later]({% post_url 2026-11-14-find-first-delete-later-retention-engine %})
- [PowerShell Logging: New-LogEntry Revisited]({% post_url 2026-10-24-PowerShell-New-LogEntry-Revised %})
