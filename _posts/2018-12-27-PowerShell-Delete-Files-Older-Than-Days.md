---
title: "PowerShell delete old files"
excerpt: "Learn how you can use PowerShell to automatically delete files and folders older than a number of days"
categories:
  - PowerShell
  - HowTo
  - Scripts
tags:
  - PowerShell
  - PowerShell Basics
  - HowTo
  - Delete Files
  - PowerShell Core
last_modified_at: 2026-11-02
---

Log files are useful until keeping every log forever becomes a disk-space problem. This example selects `.log` files whose **last write time** is more than 90 days ago, including subfolders, then previews their removal.

That is a retention policy based on modification time, not creation time. Confirm that it matches how your application writes and rotates logs before scheduling a cleanup.

## Select and inspect the files

```powershell
[string]$filePath = 'C:\TestCleanup'
[string]$fileExtension = '*.log'
[int]$retentionDays = 90

if ($retentionDays -le 0) {
    throw 'Retention must be a positive number of days.'
}

$cutoff = (Get-Date).AddDays(-$retentionDays)
$filesToPurge = @(
    Get-ChildItem -LiteralPath $filePath -Filter $fileExtension -File -Recurse -ErrorAction Stop |
        Where-Object { $_.LastWriteTime -lt $cutoff }
)

$filesToPurge | Select-Object FullName, LastWriteTime, Length
```

`-Recurse` includes subfolders; remove it to restrict selection to the top folder. `-File` excludes directories, so this does not remove empty folders. `-LiteralPath` treats brackets in the root path as characters rather than wildcard syntax. Hidden files are not included by default.

The cutoff is calculated once. The strict `-lt` comparison keeps files exactly on that boundary. Wrapping the results in `@(...)` provides an array even when zero or one file matches. An empty selection is normal; a missing or unreadable path is an error, and `-ErrorAction Stop` stops this selection rather than silently proceeding with an incomplete scan.

## Preview, then delete

Run this after reviewing the selected paths:

```powershell
if ($filesToPurge.Count -eq 0) {
    Write-Host 'No files to purge.'
}
else {
    foreach ($file in $filesToPurge) {
        Remove-Item -LiteralPath $file.FullName -WhatIf -ErrorAction Stop
    }
}
```

`-WhatIf` reports the intended operations without deleting files. Remove that switch only when the selection is correct and you are ready to delete them. `-LiteralPath` also matters here: a filename such as `service[1].log` must be treated literally.

The deletion loop stops at the first error, for example a locked file or denied access. Earlier successful deletions are not rolled back. Previewing does not prove that later deletion will succeed, and files can change between selection and removal. Use this on rotated logs that the application no longer writes; coordinate cleanup with the application's retention mechanism when files remain active.

For a scheduled job, add logging and failure reporting appropriate to your environment. See Microsoft's [Get-ChildItem](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem) and [Remove-Item](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/remove-item) documentation for parameter behavior.

## Earlier complete script

The [Remove-Old-Files repository](https://github.com/SingularVector/Remove-Old-Files) linked in the January 2019 update contains the earlier configurable solution. Treat it as separate code to review and test; the example above does not validate that repository or the older gist. The retired TechNet Gallery link has been removed.
