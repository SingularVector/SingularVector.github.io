---
title: "PowerShell Create Folder if it does not exist"
excerpt: "Learn how PowerShell can check if a folder exists and automatically create it if not."
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - PowerShell Basics
  - HowTo

toc: true
comments: true
last_modified_at: 2026-11-02
---

Before writing a log, make sure its destination is actually a directory. A path existing is not enough: a file can occupy the name you intended to use for a folder.

## Check the type of path

```powershell
$logPath = 'C:\MyLogPath'
Test-Path -LiteralPath $logPath -PathType Container
```

For a filesystem path, `Container` asks for a directory. `-LiteralPath` treats brackets and other wildcard characters as part of the supplied name. A `$false` result is a reason to investigate or create the directory; it is not proof that the parent path is writable.

## Create the directory

For filesystem directories, .NET offers an idempotent operation:

```powershell
$logPath = 'C:\MyLogPath'
$directory = [System.IO.Directory]::CreateDirectory($logPath)
$directory.FullName
```

If the directory already exists, this returns its information. It also creates missing parent directories. If a file occupies the path, or access is denied, the operation fails instead of silently turning that condition into a usable log directory.

An earlier “check then create” sequence has a race: the filesystem can change between the two commands. Calling `CreateDirectory()` handles the ordinary already-exists case without requiring that separate test. It does not guarantee that a later log write succeeds or that another process cannot change the directory afterward.

For an automation workflow, handle failure at the point where it matters:

```powershell
try {
    $directory = [System.IO.Directory]::CreateDirectory($logPath)
}
catch {
    throw "Cannot prepare log directory '$logPath': $($_.Exception.Message)"
}
```

I keep directory preparation in script templates because it is easy to forget until the first scheduled run. The important part is retaining a distinct failure path, not shaving a few microseconds off the check.

## Filesystem APIs and PowerShell providers

`Test-Path` works through PowerShell providers, including the filesystem and the Windows registry. `Directory.CreateDirectory()` is a filesystem API; it does not create registry keys or understand a PowerShell-only custom drive such as `Logs:`. Use an actual filesystem path for the .NET call.

These methods are therefore not universally interchangeable, as the original article suggested. No performance ranking is needed for this small operation; choose the semantics appropriate to the target path.

References: [Test-Path](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-path) and [Directory.CreateDirectory](https://learn.microsoft.com/en-us/dotnet/api/system.io.directory.createdirectory).
