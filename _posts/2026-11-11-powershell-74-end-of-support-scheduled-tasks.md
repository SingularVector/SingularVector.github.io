---
title: "PowerShell 7.4 Is Out of Support. What Is Actually Running Your Scripts?"
date: 2026-11-11
categories:
  - PowerShell
tags:
  - PowerShell 7
  - automation
  - scheduled-tasks
  - troubleshooting
description: "PowerShell 7.4 support has ended. Check which executable runs your scheduled scripts, capture runtime details and test the move to PowerShell 7.6 LTS."
toc: true
---

You update PowerShell, open a terminal, check the version and see 7.6.

Excellent. The overnight report should be using it too.

Except the scheduled task still launches `powershell.exe`. Or a copy of `pwsh.exe` extracted into a folder two years ago. The report has not read the release announcement, and nobody changed its action.

**Updating your interactive shell does not establish which PowerShell runs your automation.**

With PowerShell 7.4 reaching the end of support on November 10, 2026, this is a useful time to check what actually starts those scripts.

## What Reached the End of Support?

As of November 11, 2026, Microsoft's [PowerShell lifecycle table](https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle#powershell-end-of-support-dates) lists:

| Release | End of support |
| --- | --- |
| PowerShell 7.4 LTS | November 10, 2026 |
| PowerShell 7.5 | November 10, 2026 |
| PowerShell 7.6 LTS | November 14, 2028 |

The scripts do not suddenly stop working at midnight. The affected releases stop receiving updates, including security fixes. Use the latest servicing update of a supported release, on a supported operating system.

**Windows PowerShell 5.1 has a separate lifecycle tied to Windows.** The dates above do not declare every `powershell.exe` installation unsupported. A job that still needs 5.1 deserves a compatibility assessment, rather than a hurried executable rename.

## First, Identify the Shell You Opened

Run this inside the session you are checking:

```powershell
$PSVersionTable | Select-Object PSVersion, PSEdition
$PSHOME
(Get-Process -Id $PID).Path
```

That gives you the version, edition, installation directory and current executable path. Windows PowerShell 5.1 reports the `Desktop` edition; PowerShell 7 reports `Core`.

On Windows, also inspect the application paths your current session can discover:

```powershell
Get-Command powershell.exe, pwsh.exe -CommandType Application -All |
    Select-Object Name, Path
```

An error for a missing executable simply means it was not found through this lookup. This is not a complete inventory of installed copies, and another account can have a different search path.

PowerShell 7 [installs alongside Windows PowerShell 5.1](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows). Windows Terminal is the application hosting the tab; its profile chooses the shell. A tab that looks exactly like yesterday's can be running a different executable.

## Then Look at the Scheduled Task

These examples target **Windows Task Scheduler**. Replace the task name and folder with your own. You may need an elevated session to inspect tasks owned by other accounts.

```powershell
$task = Get-ScheduledTask -TaskName 'DailyReport' -TaskPath '\'

$task.Actions |
    Select-Object Execute, Arguments, WorkingDirectory

$task.Principal |
    Select-Object UserId, LogonType, RunLevel
```

[`Get-ScheduledTask`](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtask) reads the registered definition. Look at every action: a task can have several.

Does `Execute` point at `powershell.exe`, the intended `pwsh.exe`, or a wrapper such as a batch file? If it starts a wrapper, follow that file to the command that actually launches PowerShell.

Also check the script arguments, working directory and account. Testing with your own administrator account does not tell you whether the scheduled account can read the input folder, load the modules or authenticate to the destination.

“It works when I run it” is useful information. We still need to know how you ran it :)

## Ask the Scheduled Process to Identify Itself

The task definition describes what should start. A small diagnostic script can record what did start.

Save the following as `Get-AutomationRuntime.ps1`, or [download the example]({{ '/assets/code/powershell-runtime/Get-AutomationRuntime.ps1' | relative_url }}):

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

try {
    $process = Get-Process -Id $PID
    $runtime = [pscustomobject]@{
        TimestampUtc      = [DateTime]::UtcNow.ToString('o')
        PSVersion         = $PSVersionTable.PSVersion.ToString()
        PSEdition         = $PSVersionTable.PSEdition
        Executable        = $process.Path
        PSHome            = $PSHOME
        Is64BitProcess    = [Environment]::Is64BitProcess
        Account           = [Environment]::UserName
        PowerShellLocation = (Get-Location).Path
        ProcessDirectory  = [Environment]::CurrentDirectory
        ModuleSearchPath  = $env:PSModulePath
    }

    $runtime | ConvertTo-Json -Depth 3 |
        Set-Content -LiteralPath $OutputPath -Encoding UTF8
}
catch {
    Write-Error -ErrorRecord $_ -ErrorAction Continue
    exit 1
}
```

Use an **absolute output path**, with an existing parent directory writable by the scheduled account. The script replaces that output file and exits with `1` if collecting or writing the record fails. Its JSON includes account and filesystem details; review it before sharing.

For a diagnostic run, duplicate the task, keep the copy disabled for scheduled triggers, and replace only its action arguments with those needed to run this probe. Preserve the executable, account and working directory you are investigating. Run the copy manually through Task Scheduler.

This avoids invoking the production script just to discover its runtime. Compare the result with a probe run from your interactive session, using a different output filename.

The probe identifies the starting environment. A production script that launches another PowerShell process needs that child process checked too.

## Test the Job Under the Intended Runtime

Update through your existing installation method and deployment process. My [PowerShell upgrade article]({% post_url 2020-07-25-Upgrade-PowerShell %}) covers the installation side; here, the important part is verifying the job afterwards.

For a standard Windows MSI installation, a task action might look like this:

| Task Scheduler field | Example value |
| --- | --- |
| Program/script | `C:\Program Files\PowerShell\7\pwsh.exe` |
| Add arguments | `-NoLogo -NoProfile -NonInteractive -File "C:\Automation\DailyReport.ps1"` |
| Start in | `C:\Automation` |

Confirm that executable exists and check its version before using it. ZIP and other installations can use different paths. An explicit path selects an installation; the `7` directory name does not pin a particular minor or patch version.

[`-NoProfile` and `-NonInteractive`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pwsh) make the startup assumptions clearer: profiles are not loaded, and attempts to request interactive input fail rather than waiting for someone to answer. The script must load its own dependencies and handle unattended authentication.

Check the modules it actually needs in the target runtime and account. For example, if the report uses Microsoft Graph:

```powershell
Get-Module -ListAvailable -Name Microsoft.Graph.Authentication |
    Select-Object Name, Version, Path
```

[`-ListAvailable`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-module) discovers modules on that session's module search path; it does not import or validate them. Follow it with an import and a representative test using non-production inputs. Moving a 5.1 job also requires checking [Windows PowerShell compatibility differences](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell).

For scripts you have deliberately migrated and tested with a minimum requirement of 7.6, you can declare it at the top:

```powershell
#Requires -Version 7.6
```

[`#Requires`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires) rejects an older runtime. It does not install PowerShell or persuade Task Scheduler to choose another executable. Only raise the requirement when it reflects your tested support policy.

## Verify the Result, Including the Report

After updating the production task through your normal change process, inspect its next run:

```powershell
Get-ScheduledTaskInfo -TaskName 'DailyReport' -TaskPath '\' |
    Select-Object LastRunTime, LastTaskResult, NextRunTime
```

[`Get-ScheduledTaskInfo`](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtaskinfo) supplies the last run information. Check it alongside the script's logs and expected output. A zero result is encouraging; it cannot establish that the report contains the right data. The script must also propagate failures through a meaningful exit status.

The useful finish is a fresh scheduled execution, under the intended account and supported runtime, producing the expected result.

That is a little more work than checking the version in a new terminal tab. It also tells you whether the overnight report got the upgrade.
