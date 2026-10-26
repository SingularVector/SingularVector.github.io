---
title: "Rebuilding Remove-OldFiles: From Existing Policies to Controlled Cleanup"
date: 2026-11-12
categories:
  - PowerShell
  - DevOps
tags:
  - automation
  - retention
  - PowerShell
  - migration
  - testing
  - Remove-OldFiles
description: "Bring legacy CSV retention policies into a PowerShell module, resolve ambiguous scopes, and add deliberate cleanup with fresh checks, confirmation and useful evidence."
---

The report looks right. You have checked the paths, ages and exclusions. Time to delete the files?

There are two questions left. Are these actually the policies we intended to apply? And is the filesystem still in the state the report described?

In [the first part of this rebuild]({% post_url 2026-11-10-rebuilding-remove-oldfiles-start-with-the-rules %}), we made selection visible. This part brings across the existing CSV and adds controlled execution. The interesting work happens before `Remove-Item` gets involved.

---

## Keep the CSV, Make Its Meaning Explicit

The CSV let different automations and teams have different rules without collecting almost-identical scripts. That convenience stays, with the original columns:

```text
CleanupPath,FileExtension,AgeTolerance,IncludeSubFolders
```

Inspect the import before scanning any target directories:

```powershell
Import-Module ./src/RetentionEngine/RetentionEngine.psd1 -Force
$import = Import-RetentionPolicyCsv -LiteralPath ./FilePaths.csv
$import.Policies
$import.Warnings
$import.Errors
$import.Overlaps
```

A bare `log` becomes `*.log`. Empty retention means 90 days; empty recursion means false. Applied defaults produce warnings. An empty extension becomes `*`, with a warning that extensionless files match too. “Everything in this scope” deserves to be visible.

Recursion needed a correction: the old implementation treated nonempty `0` as enabled. We now accept `0`, `1` or an empty cell and convert deliberately. Someone depending on accidental recursion should discover that during migration, not after cleanup.

`$import.IsReady` means configuration validation passed. It does not establish directory access. The original UNC examples need a Windows host; the importer does not invent Unix mount points for them.

---

## Do Not Quietly Choose Between Conflicting Rules

Invalid rows remain visible beside accepted policies, but block the whole batch. So do malformed or unknown headers and broken quoting. “Just run the good rows” can make a partly applied configuration look finished.

Two individually valid rows can also conflict. The original sample contains duplicate archive paths; nested roots raise similar questions. This version flags both, even with differing patterns or nonrecursive settings. It does not guess precedence. Similar siblings such as `logs` and `logs-archive` are fine.

The [migration contract](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/csv-migration.md) documents those conservative choices. Generated row IDs are references for this import, not permanent identities across file reordering.

Once reviewed, a reporting batch revalidates the entire file and uses one evaluation instant:

```powershell
$batch = Get-RetentionBatchReport -LiteralPath ./my-policies.csv
$batch.Reports | Select-Object PolicyId, Status, CandidateCount, ErrorCount
```

An inaccessible root can produce a partial batch while accessible siblings return useful reports. Invalid configuration prevents scanning altogether. Keep warnings and rejected rows in the operational log, or a correctly blocked job may look like one that found nothing to do.

---

## One Module, One Cleanup Entry Point

The `RetentionEngine` module exposes commands for scanning, import, batch reporting, HTML export and cleanup. Support functions live privately behind that interface. Copy or import the module as a unit; do not assemble it by loading individual helpers.

`Invoke-RetentionCleanup` takes one policy and plans by default:

```powershell
$plan = Invoke-RetentionCleanup -Policy $policy
$plan.Actions
```

To preview the execution path:

```powershell
$preview = Invoke-RetentionCleanup -Policy $policy -Execute -WhatIf
```

Actual removal requires `-Execute`. With normal confirmation preferences, its high-impact `ShouldProcess` calls ask before each file. An unattended caller can deliberately use `-Confirm:$false`, but still needs the explicit execution switch.

Execution accepts one policy, not a saved candidate list or an automatic CSV deletion batch. Do not bypass overlap validation by blindly iterating accepted rows from an invalid import.

---

## Check Again After the Coffee

Every execution invocation starts with a fresh scan. A partial or failed inspection blocks removal for that policy.

Each candidate is then rechecked: scope and ancestors, links, new ignore markers, file type, length and last-write timestamp. It must still qualify under the scan’s cutoff.

Then comes confirmation. And then the checks run again.

A prompt can sit open considerably longer than the author imagined. There is always a coffee somewhere in this process :)

Changed or newly protected files are skipped with a reason. Unavailable checks or removal errors become failed actions. A directory substituted for a file does not become permission to remove the directory.

The filesystem is not locked. An identical-metadata replacement may escape detection, and a path can still change after the last check. This reduces ordinary operational surprises; it is not an atomic deletion guarantee. Old files can also remain important to their application. The [execution documentation](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/controlled-cleanup.md) states those limits.

---

## Leave Evidence of What Happened

The result records planned, deleted, skipped and failed actions. Count a deletion after it succeeds, not when we intend to try it. Observed lengths still do not measure actual freed disk space.

Our report-only HTML says “no files deleted.” Reusing that after execution would be misleading, so the exporter refuses an execution snapshot. Export the plan beforehand and retain the structured execution result afterwards; a dedicated HTML execution receipt is not implemented yet.

Once this runs unattended, the returned object only helps if something keeps it. Tomorrow’s question will be “what happened to that file?”, and terminal history is unlikely to have a convincing answer.

My [New-LogEntry function and article]({% post_url 2026-10-24-PowerShell-New-LogEntry-Revised %}) belong at that run boundary: record identifiers, policy, status and outcomes without contaminating the result stream. The module does not call it automatically yet. Logging failures must also surface; a missing log must not make a failed cleanup look successful.

---

## What We Can Claim So Far

The combined local suite reached **104 passing checks, with three platform-dependent skips**, on macOS with PowerShell 7.6.7 and Pester 5.7.1. It covers migration, reporting, execution safeguards and package boundaries. Real removal tests used disposable files; mocks exercised failures and confirmation-time changes. A copied package also worked in a fresh PowerShell session outside the repository.

That does not establish Windows locks, ACLs or network-share behaviour. Those need their own environments and fixtures.

We now have a chain from explicit policy to inspectable selection to deliberate action. Central policy storage may come next, when ownership, workers and execution history justify it. A database will not make an unexplained deletion easier to defend; this is the behaviour it needs to build on.

### Further Reading

- [Part one: Find First, Delete Later]({% post_url 2026-11-10-rebuilding-remove-oldfiles-start-with-the-rules %})
- [Module structure and distribution](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/module-structure.md)
- [CSV migration contract](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/csv-migration.md)
- [Controlled cleanup contract](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/controlled-cleanup.md)
