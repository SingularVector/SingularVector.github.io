---
title: "Rebuilding Remove-OldFiles: Keeping the Policies, Fixing the Assumptions"
date: 2026-11-16
categories:
  - PowerShell
  - DevOps
tags:
  - automation
  - retention
  - PowerShell
  - migration
  - Remove-OldFiles
description: "Migrate legacy cleanup CSV policies with explicit defaults, strict recursion conversion and overlap detection before running multi-policy retention reports."
---

The CSV was doing useful work long before I decided to revisit the code. Different automations and teams could have different retention rules without maintaining a small family of almost-identical scripts.

I want to keep that convenience. I would rather not keep every assumption that came with it :)

In [the reporting milestone]({% post_url 2026-11-14-find-first-delete-later-retention-engine %}), we made one policy’s decisions visible. Now we can bring the old CSV into that engine—and catch a few surprises before they become cleanup instructions.

---

## Keep the Familiar Bits

The columns stay the same:

```text
CleanupPath,FileExtension,AgeTolerance,IncludeSubFolders
```

The importer translates each row into a policy object. A bare `log` becomes `*.log`, retention becomes an integer, and recursion becomes a Boolean.

Inspect it first, without scanning any target directories:

```powershell
Import-Module ./src/RetentionEngine/RetentionEngine.psd1 -Force
$import = Import-RetentionPolicyCsv -LiteralPath ./FilePaths.csv
$import.Policies
$import.Warnings
$import.Errors
$import.Overlaps
```

`$import.IsReady` means the configuration passed validation. It does not mean the directories exist or that your account can read them. The original UNC examples also need a Windows host; the importer will not invent a Unix mount point to make them work.

---

## The Small Defaults That Matter

An empty retention value still means 90 days. Empty recursion means false. Both produce warnings showing where a default was applied.

An empty extension becomes explicit `*`, with a warning that extensionless files match too. “Everything in this scope” deserves to be visible.

Recursion needed a correction. The old implementation treated every nonempty value as enabled, including `0`. The importer accepts `0`, `1` or an empty cell and converts them deliberately. Anything else is rejected.

If someone relied on accidental recursion, this changes their result. I would rather explain that during migration than let them discover it after a cleanup run. Compatibility should preserve useful policies, not require us to reproduce a bug faithfully.

---

## Do Not Lose the Bad Rows

Invalid ages, missing paths and unsupported extension syntax produce row errors. Missing, duplicate or unknown headers block the file. Quoted commas work; broken quoting does not get a creative interpretation.

Accepted policies remain available for review, with their source file and row. But **one invalid row blocks the batch**. “Just run the good ones” can leave a job looking finished when only part of its configuration was applied.

Generated IDs such as `csv-row-2` identify positions in this import. Reordering the file changes them; they are not permanent database identities.

There is another interesting case in the original sample: two entries for the same archive path. Both rows can be valid while their combined intention remains unclear.

For now, equal or nested roots are flagged as overlaps, even with different patterns or nonrecursive settings. Similar siblings such as `logs` and `logs-archive` are fine. The rule is conservative, but explicit: we have not defined precedence between conflicting policies, so the importer does not quietly choose one for us.

---

## Then Run the Intended Set

Once you have reviewed the input:

```powershell
$batch = Get-RetentionBatchReport -LiteralPath ./my-policies.csv
$batch.Status
$batch.Reports | Select-Object PolicyId, Status, CandidateCount, ErrorCount
```

The batch revalidates the complete file before scanning. Every policy shares one evaluation instant, with its own retention cutoff. A root that cannot be read can fail while a sibling produces useful results; that makes the batch partial. Invalid configuration or overlaps prevent scanning altogether.

Each result in `$batch.Reports` can use the existing HTML exporter. Keep the reports outside every configured cleanup root. We are still reporting, not deleting.

---

## What We Checked

This milestone’s local suite passed **86 checks, with three platform-dependent skips**, on macOS with PowerShell 7.6.7 and Pester 5.7.1. The 25 new checks cover conversion, defaults, malformed input, overlap handling and disposable batch scans.

Windows path rules, junctions and a provisioned share remain outside that evidence. The [migration notes](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/csv-migration.md) record the contract and limitations.

Next comes controlled deletion. Before we get there, we can explain which policies were accepted, what changed during migration, and why a whole batch did—or did not—run. That is a more useful starting point than hoping the CSV looks about right.

### Further Reading

- [Original cleanup article]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %})
- [Report-only engine and HTML output]({% post_url 2026-11-14-find-first-delete-later-retention-engine %})
- [CSV migration contract](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/csv-migration.md)
