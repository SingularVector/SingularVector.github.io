---
title: "PowerShell Restore Default Gallery Repository"
excerpt: "Restore default PowerShell Gallery repository in PowerShell and PowerShell Core"
categories:

  - PowerShell
  - Tips
tags:
  - PowerShell
  - PowerShell Core
  - Tips
last_modified_at: 2026-11-02
---

While installing the Az module on my Mac, I once hit a “No match was found” error. `Get-PSRepository` revealed the actual problem: no module repositories were registered.

For **PowerShellGet** commands such as `Install-Module`, check first:

```powershell
Get-PSRepository
```

If `PSGallery` is missing, restore its built-in registration:

```powershell
Register-PSRepository -Default
Get-PSRepository -Name PSGallery
```

Use `-Default` rather than trying to register a custom repository named `PSGallery`. Registration is user-specific, so run these commands as the account that needs to install modules. Leaving the installation policy as `Untrusted` is normal: it enables the repository trust prompt rather than preventing registration.

If PSGallery is already listed, a missing-module error can have another cause: verify the module name, requested version and network/proxy access before changing repository configuration.

`Get-PSResourceRepository` belongs to **Microsoft.PowerShell.PSResourceGet**, which maintains separate repository settings. If your workflow uses `Install-PSResource`, inspect that repository list instead; restoring PowerShellGet's registration does not repair it.

References: [Register-PSRepository](https://learn.microsoft.com/en-us/powershell/module/powershellget/register-psrepository) and [Get-PSResourceRepository](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.psresourceget/get-psresourcerepository).
