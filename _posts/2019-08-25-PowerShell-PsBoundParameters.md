---
title: "Check function parameters with PSBoundParameters"
excerpt: "Or how do I know which parameters have been passed to a function?"
categories:

  - PowerShell Best Practice
  - PowerShell
tags:
  - Tutorial
  - HowTo
  - PowerShell
last_modified_at: 2026-11-02
---

When a function receives a switch, two questions look similar but are different: did the caller supply it, and is it enabled? `$PSBoundParameters` lets us answer the first without guessing from the value.

## A bound value can be false

```powershell
function Get-ChangePlan {
    [CmdletBinding()]
    param (
        [string]$IssueName = 'General maintenance',
        [switch]$DryRun
    )
    [pscustomobject]@{
        IssueName = $IssueName
        IssueWasSupplied = $PSBoundParameters.ContainsKey('IssueName')
        DryRunWasSupplied = $PSBoundParameters.ContainsKey('DryRun')
        DryRunEnabled = [bool]$DryRun
    }
}

Get-ChangePlan -DryRun:$false
```

For that call, `DryRunWasSupplied` is `$true`, but `DryRunEnabled` is `$false`. The default `IssueName` is available as a variable, while `IssueWasSupplied` is `$false`: default parameter values are not automatically entries in `$PSBoundParameters`.

Use the presence check for requirements such as “only overwrite this setting if the caller explicitly supplied it.” Use the actual value when the question is whether an option is enabled. The original article treated those checks as equivalent.

## Common parameters belong to advanced functions

`[CmdletBinding()]` provides common parameters such as `-Verbose`; do not also declare your own parameter named `Verbose` in that advanced function. Use `Write-Verbose` for diagnostic messages and let PowerShell handle their visibility.

## Forward only compatible arguments

A wrapper can pass arguments to another command, but forwarding every key blindly can introduce unsupported parameters or unintended behaviour. Build a separate map of the arguments the target accepts:

```powershell
function Get-FileList {
    [CmdletBinding()]
    param (
        [string]$LiteralPath = '.',
        [switch]$Recurse
    )
    $forward = @{ LiteralPath = $LiteralPath; File = $true; ErrorAction = 'Stop' }
    if ($PSBoundParameters.ContainsKey('Recurse')) {
        $forward['Recurse'] = [bool]$Recurse
    }
    Get-ChildItem @forward
}
```

Here the default path is intentionally included even when it was not explicitly bound. The target receives only its own parameters. Building a new map also avoids mutating the record of what the caller supplied.

## Inspect names without leaking values

```powershell
function Get-SuppliedParameterNames {
    param ([string]$Name, [switch]$Enabled)
    $PSBoundParameters.Keys | Sort-Object
}
Get-SuppliedParameterNames -Name 'Example' -Enabled:$false
# Enabled
# Name
```

Dumping the entire dictionary can expose passwords, tokens or other sensitive arguments. For routine diagnostics, log names or selected nonsecret values rather than serialising every bound value.

`$PSBoundParameters` describes the parameter binding for the current script/function scope; it is not a list of every local variable. See [about_Automatic_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables) and [splatting](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_splatting).
