---
title: "Find First, Delete Later: Building the Retention Engine"
date: 2026-11-14
categories:
  - PowerShell
  - DevOps
tags:
  - automation
  - retention
  - PowerShell
  - testing
  - Remove-OldFiles
description: "Build a report-only PowerShell retention engine with strict policies, protected subtrees, explicit partial results and tests before adding deletion."
---

A file appeared in the report. Before asking whether we can delete it, I want to know why it appeared there.

Was it old enough? Did recursion include that directory deliberately? Was there an ignore marker higher up? And did the scan finish, or are we looking at the accessible half of the filesystem?

The first milestone in rebuilding [Remove-OldFiles](https://github.com/SingularVector/Remove-Old-Files) is designed to answer those questions. The scanner returns one report and changes no files. Deletion is not an option hidden behind a switch; it is not implemented yet.

---

## A Policy You Can Read

The development module requires PowerShell 7.4 or later. From the repository directory, its interface looks like this:

```powershell
Import-Module ./src/RetentionEngine/RetentionEngine.psd1 -Force

$policy = [pscustomobject]@{
    PolicyId = 'automation-logs'
    RootPath = 'C:\RetentionLab'
    FilePattern = '*.log'
    RetentionDays = 30
    Recurse = $true
    Enabled = $true
}

$report = Get-RetentionReport -Policy $policy
$report | Select-Object Status, CandidateCount, CandidateBytes, ErrorCount
$report.Candidates
$report.Errors
```

Replace the root with an existing disposable directory appropriate to your platform. CSV import is not part of this version; one policy object keeps the first interface small.

Validation requires actual Boolean values and an integer retention period. Invalid input produces a failed report before traversal. The engine does not helpfully turn an empty pattern into “everything.” Cleanup software should be very careful about that particular kind of helpfulness.

---

## One Cutoff, One Meaning

The engine captures one UTC evaluation time, subtracts the retention period, and compares `LastWriteTimeUtc` against that cutoff. Files must be strictly older; equality does not qualify.

For repeatable checks, the evaluation time is injectable:

```powershell
$report = Get-RetentionReport -Policy $policy -EvaluationTimeUtc ([datetimeoffset]'2026-10-26T12:00:00Z')
```

A fixed clock lets the test put a file exactly on the boundary. “Old enough when I ran it yesterday” is not a particularly dependable assertion.

An old timestamp does not prove a file is unused or safe for its application to lose. It establishes eligibility under this policy, which is a narrower claim.

---

## Stop Before Entering Protected Directories

The walker visits one directory at a time. Before classifying its files or queuing child directories, it checks for a regular `ignore` file. A marker excludes the whole subtree.

That is different from recursively collecting every file and filtering out selected parent paths afterwards. We also avoid pretending to know how many files sit inside a subtree we deliberately did not inspect.

Links and reparse points are skipped. Roots and ancestors that are links are rejected, as are `..` segments that could hide such ancestry during path normalisation. On macOS, that means using a physical path such as `/private/tmp/...` rather than the `/tmp` alias.

These checks define ordinary traversal boundaries, not protection against hostile concurrent replacement of directories. The scan is not a filesystem transaction; adding deletion will require fresh checks and an honest description of the remaining race limitations.

---

## Partial Is a Result Worth Reporting

The result contains candidates, exclusions and errors, plus one status:

| Status | What happened |
| --- | --- |
| Completed | Intended inspection finished without errors; zero candidates is valid. |
| Partial | Some intended inspection failed; the available candidates are incomplete. |
| Failed | Invalid policy or initial root access prevented scanning. |
| Disabled | A valid disabled policy was not scanned. |

A marker-check failure stops inspection of that directory. It must not become permission to assume no marker exists. Accessible siblings can still be inspected, with the overall result marked partial.

The report returns objects, not preformatted tables or log strings. Callers decide how to present or persist them. `DeletedCount` is always zero in this milestone, regardless of how promising the candidate list looks.

---

## Give the Report to Someone Who Does Not Live in PowerShell

Objects are useful for automation. Asking another team to read them in a terminal is a different proposition.

A separate exporter turns the same result into a standalone HTML file with embedded CSS:

```powershell
Export-RetentionReportHtml -Report $report -LiteralPath ./retention-report.html
```

Choose an output directory outside the scanned root. Existing files require `-Force`; `-WhatIf` previews the export without writing it. The scan itself remains independent of presentation.

The report puts the outcome first, followed by candidate counts and potential space, the policy and exact cutoff, errors, candidate details and exclusions. A partial scan should be the first thing someone notices, not a footnote underneath an encouraging storage figure.

![A synthetic HTML retention report prominently marks an incomplete scan, two candidates, 82 MiB of observed candidate data and one error. No files were deleted.]({{ '/assets/images/retention-rebuild/html-report-preview.png' | relative_url }})

*Invented sample data, not a production result. The incomplete status matters as much as the candidate total.*

[Open the complete sample report]({{ '/assets/reports/retention-rebuild/sample-retention-report.html' | relative_url }}). It works offline, without external fonts, scripts or libraries. Paths and error text are HTML-escaped, and the file makes clear that no files were deleted. Potential bytes describe observed file lengths, not guaranteed free space.

That gives another team something they can review without my being there to translate the output. Which was rather the point of turning a script into a tool.

---

## What We Actually Tested

The local run used PowerShell 7.6.7 and Pester 5.7.1 on macOS: **61 checks passed, three were skipped**.

The checks cover cutoff boundaries, recursion, protected descendants, hidden files, invalid policies, real symbolic links, repeatable output and unchanged fixture contents. Directory and metadata failures are injected at small filesystem boundaries, so we can verify partial-result behaviour without depending on an account that may bypass permission restrictions.

Exporter checks also cover escaping, all four outcomes, output boundaries, overwrite protection and `-WhatIf`.

The skipped checks concern Windows path rules, Windows junctions and a provisioned UNC share. A Windows/Linux/macOS workflow is prepared, but those hosted runs have not happened for this development milestone. Passing local tests is useful evidence, not a substitute for testing the environments we intend to support.

The [usage notes](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/report-only-usage.md) explain how to run the module and acceptance suite. Do not turn its candidates into a deletion pipeline; this is a reporting milestone, not the finished cleanup job.

Next comes importing the original CSV policies without carrying their ambiguous conversions into the new engine. That is where compatibility gets interesting: keeping the useful inputs while being explicit about the behaviour we are correcting.

### Further Reading

- [Report-only module](https://github.com/SingularVector/Remove-Old-Files/tree/main/src/RetentionEngine)
- [Acceptance tests](https://github.com/SingularVector/Remove-Old-Files/blob/main/tests/RetentionEngine.Tests.ps1)
- [From a Script to a Tool]({% post_url 2026-11-07-from-a-script-to-a-tool %})
