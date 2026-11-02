---
title: "Get current user UPN"
excerpt: "In this post we will explore how to easily retrieve currently logged in user UPN via PowerShell"
categories:
  - PowerShell
  - Tips
  - HowTo

tags:
  - PowerShell
  - Tips

toc: false
header:

last_modified_at: 2026-11-02
---

A few days ago while developing a cmdlet for an internal module in support to a larger automation workflow I found myself in need to easily derive *UserPrincipalName* of the currently logged on user running the command.


The important distinction is the **process identity** versus the person at the desktop. In a scheduled task, service or remoting session those may be different accounts. A username such as `CONTOSO\daniele` is not the same value as a UPN such as `daniele@example.com`; do not construct a UPN by appending a guessed domain.

On Windows, start with the built-in command:

```powershell
whoami /upn
```

For an account whose UPN Windows can resolve, this returns the UPN for the current security context. It can fail for local accounts or contexts without a resolvable domain UPN; check `$LASTEXITCODE` before using the output in automation.

For the original **Windows / Active Directory Domain Services** scenario, the SID-based LDAP lookup is another option when a domain controller is reachable:

```powershell
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$user = [ADSI]"LDAP://<SID=$sid>"
$upn = [string]$user.Properties['userPrincipalName'].Value
if ([string]::IsNullOrWhiteSpace($upn)) {
    throw 'The current AD account has no userPrincipalName value.'
}
$upn
```

This queries the directory attribute rather than assuming an email address or logon name is the UPN. It relies on Windows ADSI and AD DS; it is not a cross-platform or Microsoft Entra-only identity lookup. Handle directory lookup failures in the calling script.

`$env:USERNAME` and `[Environment]::UserName` provide a short username; `WindowsIdentity.GetCurrent().Name` normally includes the Windows domain. Querying `Win32_ComputerSystem.UserName` instead targets the interactive desktop user and is not equivalent to querying the current process identity.

See [whoami](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami) and [WindowsIdentity.GetCurrent](https://learn.microsoft.com/en-us/dotnet/api/system.security.principal.windowsidentity.getcurrent).
