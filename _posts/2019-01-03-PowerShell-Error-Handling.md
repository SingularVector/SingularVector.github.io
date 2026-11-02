---
title: "PowerShell Exception Handling"
excerpt: "An introduction to PowerShell error handling. In this post we will explore what error handling is and how to implement it in PowerShell scripts"
categories:

  - PowerShell
tags:
  - PowerShell
  - PowerShell Basics
  - PowerShell Core
  - Error Handling
  - Exception Handling
last_modified_at: 2026-11-02
---

A scheduled cleanup can print “complete” even after failing to read its target folder. The script reached the last line; that does not mean the work succeeded. Error handling should make those two outcomes distinguishable to the person or scheduler running the job.

## Terminating and non-terminating errors

PowerShell cmdlets can report an error for one item and continue processing others. A missing file or access-denied error may be non-terminating; that classification describes control flow, not how serious the problem is for your workflow.

`catch` handles terminating errors. To make a cmdlet's non-terminating errors enter that path, use `-ErrorAction Stop`:

```powershell
$folder = 'C:\MyApp\Temp'
try {
    $files = @(Get-ChildItem -LiteralPath $folder -File -ErrorAction Stop)
    Write-Host "Successfully enumerated $($files.Count) files."
}
catch {
    Write-Warning "Could not enumerate '$folder': $($_.Exception.Message)"
    throw
}
```

An empty array means the folder was successfully enumerated without matching files. An unreadable or missing folder fails instead of being reported as an empty directory. The bare `throw` rethrows the current error so the caller can detect failure.

The original article's final cleanup example omitted `-ErrorAction Stop`, so several failures would bypass its `catch` blocks. For an actual deletion workflow with preview and retention rules, see [delete old files]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %}).

## Choose the error policy deliberately

`-ErrorAction` applies to that command's non-terminating errors. Common choices are `Continue` (report and continue), `Stop` (make the error terminating), `SilentlyContinue` (suppress its display while retaining error information) and `Ignore` (also omit it from `$Error`). Suppressing output is not the same as handling the failure.

Prefer a command-level setting when only that operation needs it. If you change `$ErrorActionPreference` around a larger block, preserve the incoming value:

```powershell
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Stop'
    Get-Item -LiteralPath 'C:\MyApp\settings.json'
}
finally {
    $ErrorActionPreference = $previousPreference
}
```

Restoring `'Continue'` unconditionally, as the earlier example did, could overwrite the caller's policy. Neither setting catches a parse error in the same script before that script can run.

## Inspect the current error

Inside `catch`, `$_` is the current `ErrorRecord`:

```powershell
try {
    Get-Item -LiteralPath 'C:\MyApp\settings.json' -ErrorAction Stop
}
catch {
    Write-Warning "Category: $($_.CategoryInfo.Category); error: $($_.Exception.Message)"
    throw
}
```

Use typed catches only when you know the exception type and need different handling for it. Catching an undefined type such as the original `[GetWMICOMException]` is not a reliable general pattern.

`$Error` contains recent error records, newest first, subject to its retention behaviour. `$Error[0]` can help in an interactive investigation, but inside a handler `$_` ties the diagnostic to the failure being handled. Avoid dumping full request bodies or credentials into logs just because an exception exposes them.

## Use finally for cleanup

A `finally` block is where you release resources or restore state after a `try`/`catch` path. It is not a success notification: it also runs after failures. Abrupt process termination or host failure can prevent cleanup, so it is not a substitute for durable job state or recovery logic.

Log success after the operation has actually completed. If a handler reports an error and then returns normally, the caller may still treat that invocation as successful; decide whether to rethrow or return an explicit result according to the function's contract.

## Native programs need their own result check

An external executable's nonzero exit code is a separate signal. Check `$LASTEXITCODE` immediately after the process, and use the tool's documented meaning for each code; some programs use nonzero values for successful outcomes with differences.

For a simple Git check, with Git installed and on PATH:

```powershell
Get-Command git -ErrorAction Stop | Out-Null
& {
    # Use an explicit exit-code policy in this local scope.
    $PSNativeCommandUseErrorActionPreference = $false
    & git --version
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Git failed with exit code $exitCode."
    }
}
```

PowerShell 7.3 and later provide `$PSNativeCommandUseErrorActionPreference` to integrate native exit codes with PowerShell's error preferences. The block above disables that integration locally and handles the exit code explicitly; Windows PowerShell 5.1 does not have that automatic integration. Do not assume a native failure will behave like a cmdlet error under every PowerShell version and preference setting.

References: [about_Try_Catch_Finally](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_try_catch_finally), [about_Preference_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables) and [about_Automatic_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables).
