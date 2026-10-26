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
description: "Rebuild a real PowerShell cleanup solution around explicit retention rules, protected folders and an HTML report you can review before deleting anything."
---

In [From a Script to a Tool]({% post_url 2026-11-07-from-a-script-to-a-tool %}), we looked at making a script dependable enough for someone else to use. Now let’s put those ideas against a solution I actually used.

Back in [2018 (time flies...), I wrote about deleting old files with PowerShell]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %}). That grew into [Remove-OldFiles](https://github.com/SingularVector/Remove-Old-Files), used at a previous company to manage logs from different automations and support other teams with similar cleanup needs.

Different locations had different retention rules. A central CSV described them, with ignore markers and exception notifications around execution.

The files were not the difficult part. The rules were.

I had considered moving the configuration into a database. Revisiting the project, I still see value in that—but first I want to answer a simpler question: **can we explain exactly why a file qualifies for cleanup?**

This rebuild follows that question in two parts: first selection and reporting, then migration and controlled execution. There are a few old assumptions for me to revisit along the way :)

---

## Keep the Useful Design, Question the Assumptions

Putting policy outside the code was worth keeping. One row could retain logs for 90 days; another could keep exported files for seven. Supporting another team did not require another copy of the script with another hard-coded path.

The CSV held the path, extension, retention days and recursion setting. A file named `ignore` provided a local exception.

Reading the current source also exposed mismatches. The documented recursion value `0` was treated as enabled because it was nonempty. Ignore handling compared exact parent directories, leaving deeper descendants insufficiently protected. Deletion counters could advance after nonterminating errors. Descriptions referred to creation time while selection used last-write time.

There is also a mismatch between logging call sites and the embedded helper’s parameters. These are findings against the checked-in source, not a reconstruction of every historical deployment or local adjustment. Rewriting those assumptions in cleaner code would not be much of an improvement.

So the first rebuilt capability is deliberately limited: **inspect one policy and report its decisions without deleting files**. The legacy script stays alongside the new module.

---

## A Policy You Can Read

The `RetentionEngine` module requires PowerShell 7.4 or later. From the repository directory:

```powershell
Import-Module ./src/RetentionEngine/RetentionEngine.psd1 -Force

$policy = [pscustomobject](
    @{
        PolicyId = 'automation-logs'
        RootPath = 'C:\RetentionLab'
        FilePattern = '*.log'
        RetentionDays = 30
        Recurse = $true
        Enabled = $true
    }
)

$report = Get-RetentionReport -Policy $policy
$report | Select-Object Status, CandidateCount, CandidateBytes, ErrorCount
$report.Candidates
$report.Errors
```

Replace the root with an existing disposable directory for your platform. The engine requires actual Booleans and an integer retention period; invalid input fails before traversal. It does not helpfully turn an empty pattern into “everything.” Cleanup software should be careful about that particular kind of helpfulness.

Age means `LastWriteTimeUtc`, strictly earlier than one cutoff calculated for the run. Exactly at the cutoff does not qualify. Tests can supply a fixed `-EvaluationTimeUtc` to check that boundary reliably.

An old timestamp establishes eligibility under a policy. It does not prove the file is unused or safe for its application to lose.

---

## Protect the Subtree Before Entering It

The walker visits one directory at a time. A regular `ignore` file protects its containing directory and every descendant. We do not enter that subtree just to count how many files we skipped.

That is different from collecting everything recursively and filtering parent paths afterwards. It also avoids confusing neighbours such as `Archive` and `ArchiveOld`.

Links and reparse points are skipped, and linked roots or ancestors are rejected. On macOS, that means a physical path such as `/private/tmp/...` rather than the `/tmp` alias. Hidden files are included unless another exclusion protects them.

Those choices have tradeoffs. Both need to be documented and tested; neither should be discovered during a cleanup run. Trust me, you do not want to deal with that :)

The [behaviour specification](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/retention-engine-specification.md) records the details. These are ordinary traversal boundaries, not a guarantee against hostile concurrent directory replacement.

---

## An Empty Report Needs an Explanation

The result distinguishes four outcomes:

| Status | Meaning |
| --- | --- |
| Completed | Inspection finished without errors; zero candidates is valid. |
| Partial | Some intended inspection failed; the available inventory is incomplete. |
| Failed | Invalid policy or initial root access prevented scanning. |
| Disabled | A valid disabled policy was not scanned. |

If checking an ignore marker fails, that directory is skipped with an error. We must not turn “could not check” into “nothing is protected.” Accessible siblings can still contribute to a partial report.

The scanner returns objects, keeping candidates, exclusions and errors separate. Logging belongs alongside that result: my [New-LogEntry article]({% post_url 2026-10-24-PowerShell-New-LogEntry-Revised %}) covers the current logging function. A wrapper can record the run identifier, policy and failures without mixing diagnostic strings into the candidate stream. Automatic integration is not implemented yet.

---

## Make It Reviewable by Another Team

Objects work well for automation. Asking another team to inspect them in a terminal is a different proposition.

```powershell
Export-RetentionReportHtml -Report $report -LiteralPath ./retention-report.html
```

Choose an existing output directory outside the scanned root. Existing files require `-Force`; `-WhatIf` previews the export without writing.

The standalone HTML embeds its CSS and puts the outcome first, then counts, potential space, policy, cutoff, errors and file details. A partial scan should not be a footnote underneath an encouraging storage figure.

![A synthetic retention report highlights an incomplete scan, two candidates, 82 MiB of observed file data and one error.]({{ '/assets/images/retention-rebuild/html-report-preview.png' | relative_url }})

*Invented sample data, not production savings. The incomplete status matters as much as the candidate total.*

[Open the full sample]({{ '/assets/reports/retention-rebuild/sample-retention-report.html' | relative_url }}). It works offline, escapes paths and diagnostics, and explicitly states that no files were deleted. Potential bytes describe observed file lengths, not guaranteed free space.

That gives someone a useful way to review the selection without my being there to translate it. Which was rather the point of turning a script into a tool.

---

## Evidence Before Action

At this reporting milestone, **61 local checks passed and three were skipped**, using macOS, PowerShell 7.6.7 and Pester 5.7.1. They covered age boundaries, recursion, protected descendants, symbolic links, failure reporting, unchanged fixture files and HTML export. Controlled mocks exercised permission and metadata failures; they do not establish real network-share behaviour.

Windows path rules, junctions and a provisioned UNC share remain outside that local evidence. The repository documentation records the limitations and how to run the tests.

Next we can bring the CSV policies across and add an explicit execution path. Finding the files is useful. Being able to explain the selection is what makes that next step worth attempting.

### Further Reading

- [Original cleanup article]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %})
- [Behaviour specification](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/retention-engine-specification.md)
- [Reporting usage and tests](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/report-only-usage.md)
