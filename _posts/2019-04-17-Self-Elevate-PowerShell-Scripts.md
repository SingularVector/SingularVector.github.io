---
title: "PowerShell run script as administrator"
excerpt: "How to write a PowerShell script that will self elevate the session if it is not being run
as administrator"
categories:

  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Tips
  - Tutorials
  - PowerShell elevate script
  - PowerShell elevation
last_modified_at: 2026-11-02
---

Some Windows administration scripts need an elevated token. Check that requirement explicitly instead of waiting for a registry or service operation to fail halfway through.

## Require elevation at the start

If the entire script needs administrator privileges, put this directive near its beginning:

```powershell
#Requires -RunAsAdministrator
```

It stops execution when the session is not elevated. It does not display a UAC prompt or relaunch the script. That is often the clearest behaviour for a scheduled or managed deployment, where the execution account should be configured before the job starts.

For a conditional check on Windows:

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isElevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

Membership of the local Administrators group alone is not the same as running with an elevated token under UAC.

## Open an elevated session interactively

For Windows PowerShell 5.1:

```powershell
Start-Process -FilePath powershell.exe -Verb RunAs
```

For PowerShell 7, when `pwsh.exe` is installed and on PATH:

```powershell
Start-Process -FilePath pwsh.exe -Verb RunAs
```

Accepting the UAC prompt opens a **new process**. It does not elevate the current process or automatically continue the script that launched it. Variables, imported modules and the working directory are not a shared session.

The earlier article called opening a new console “self elevation.” A real relaunch must pass the script path, arguments and working directory deliberately, quote them correctly and end the original execution path to avoid doing the work twice. For a managed job, prefer an explicitly configured elevated task over adding an interactive relaunch mechanism.

## A different account is a separate requirement

`Start-Process -Credential` and `-Verb RunAs` use different parameter sets. Do not treat entering another account's password as proof of an elevated token, and do not use nested shell commands to hide the distinction. Start the intended account in a supported way, obtain elevation where authorised, then verify the resulting identity and token before running the operation.

These examples target Windows. They are not Linux/macOS privilege checks or a mechanism for bypassing UAC.

References: [about_Requires](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires) and [Start-Process](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process).
