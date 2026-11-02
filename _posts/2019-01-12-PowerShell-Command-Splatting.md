---
title: "PowerShell - Command Splatting"
excerpt: "What is command splatting, how to use it and implement dynamic parameters"
categories:
  - PowerShell Tips
tags:
  - PowerShell
  - Splatting
  - PowerShell Core
  - Command Splatting
last_modified_at: 2026-11-02
---

I often see the same administration command repeated in both branches of an `if`, with only one parameter value changed. Splatting lets us build the arguments once and keep the command itself in one place.

## Pass a parameter map

```powershell
$copyParameters = @{
    LiteralPath = './File1.txt'
    Destination = './File2.txt'
    ErrorAction = 'Stop'
}
Copy-Item @copyParameters
```

The hashtable's keys are parameter names; values are the arguments. `@copyParameters` expands that map into the call. `$copyParameters` by itself would pass the dictionary as an ordinary value.

This does not create new parameters on `Copy-Item`, or bypass its normal parameter-set checks. A misspelled or incompatible key still fails.

## Choose values before invoking the command

In the original AD example, the description depended on whether a user's city was set:

```powershell
$userIdentity = 'Test.User'
$userCity = 'New York'
$adDsServer = 'dc01.example.com'

$setUserParameters = @{
    Identity = $userIdentity
    Server = $adDsServer
    Description = if ([string]::IsNullOrWhiteSpace($userCity)) {
        'Office not defined for user'
    }
    else {
        "$userCity - Office"
    }
    WhatIf = $true
    ErrorAction = 'Stop'
}
Set-ADUser @setUserParameters
```

The example requires the ActiveDirectory module and appropriate directory access. `WhatIf` previews the update. Remove that entry only when the target and description have been reviewed for the actual operation.

The earlier rewrite changed the city suffix and used inconsistent server variable names. This version keeps the same intended description in both the direct and splatted forms.

## Rebuild maps inside a loop

A fresh map prevents a value from the previous user leaking into the next call:

```powershell
foreach ($user in $matchingUsers) {
    $parameters = @{
        Identity = $user.DistinguishedName
        Server = $adDsServer
        Description = if ([string]::IsNullOrWhiteSpace($user.City)) {
            'Office not defined for user'
        }
        else {
            "$($user.City) - Office"
        }
        WhatIf = $true
        ErrorAction = 'Stop'
    }
    Set-ADUser @parameters
}
```

Here `$matchingUsers` is a previously retrieved set of users with their `City` property included. If you deliberately reuse a map, indexed assignment such as `$parameters['Description'] = ...` replaces a value, while `.Add()` rejects an existing key. Remove an optional key when it should be absent, rather than leaving a stale value.

## Conditional arguments are not dynamic parameters

The original article called these “dynamic parameters.” More precisely, they are arguments selected at runtime. PowerShell's `dynamicparam` mechanism is a separate feature for defining parameters whose availability depends on context.

For portable scripts, avoid specifying the same parameter in both the map and the explicit command. PowerShell 7.1 added explicit-argument overrides for hashtable splatting; older versions can reject the duplicate. One clearly constructed map is easier to inspect across versions.

Related: [PSBoundParameters]({% post_url 2019-08-25-PowerShell-PsBoundParameters %}) and [about_Splatting](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_splatting).
