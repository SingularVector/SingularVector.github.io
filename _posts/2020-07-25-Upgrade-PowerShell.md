---
title: "Upgrade PowerShell 7 version"
excerpt: "In this post we will explore how to easily and effectively upgrade PowerShell 7 when a new version is released"
categories:
  - PowerShell
tags:
  - PowerShell
  - PowerShell 7
  - HowTo

toc: false
last_modified_at: 2026-11-02
---

PowerShell 7 updates depend on how you installed it. On Windows clients, [Microsoft documents WinGet as the recommended installation method](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows). Start by checking what is installed:

```powershell
$PSVersionTable.PSVersion
winget list --id Microsoft.PowerShell --exact
```

If WinGet lists your stable PowerShell installation, update that package:

```powershell
winget upgrade --id Microsoft.PowerShell --exact --source winget
```

Follow any installer prompts, then open a **new** `pwsh` session and run `$PSVersionTable.PSVersion` again. An already running session continues using the version it started with. If WinGet reports no applicable update, check the installed version and package source before trying another installer.

For Windows Server or managed deployments, use the appropriate MSI from the [official installation guide](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows#install-the-msi-package) and follow your deployment process. Store, ZIP and .NET tool installations have different update paths; use the instructions for your installation rather than mixing methods.

On macOS and Linux, follow the update procedure for the package manager or installation method you originally used; see Microsoft's [installation overview](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell).

PowerShell 7 runs alongside Windows PowerShell 5.1. Updating `pwsh` does not replace `powershell.exe`. Test the modules and scripts you depend on before rolling an update out to automation hosts.

The original 2020 example downloaded and immediately executed an installer script with `Invoke-Expression`. The package-based workflow above makes that shortcut unnecessary.
