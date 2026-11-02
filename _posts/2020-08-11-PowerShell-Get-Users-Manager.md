---
title: "PowerShell - Get Active Directory reports"
excerpt: "In this article I'm sharing a function that will gets you all users directly or indirectly reporting to a specific manager"
categories:
  - PowerShell
  - HowTo
  - Identity Management
tags:
  - PowerShell
  - Active Directory
  - Identity Management

toc: false
header:
    teaser: "/assets/images/shared/AD_Logo.png"
last_modified_at: 2026-11-02
---

In [Get users reporting to a manager]({% post_url 2020-08-05-Active-Directory-Get-Report-Chain %}), I compared ways to follow AD's `manager` links. I use this often enough that resolving the manager and building the query belong in a reusable function.

The function below uses the ActiveDirectory module and the server-side matching rule `1.2.840.113556.1.4.1941`. It returns users directly or indirectly reporting to the chosen manager, as recorded in AD, not an HR-authoritative organisation chart.

## Load and use the function

Download [Get-ReportChain.ps1]({{ '/assets/code/active-directory/Get-ReportChain.ps1' | relative_url }}), review it and dot-source the saved file in a session with the ActiveDirectory module available:

```powershell
. .\Get-ReportChain.ps1

Get-ReportChain -SamAccountName 'manager01'
Get-ReportChain -UserPrincipalName 'manager01@example.com'
Get-ReportChain -UserDN 'CN=Manager One,OU=Users,DC=example,DC=com'
```

Choose one identity form per invocation. A UPN is looked up as a directory attribute; it is not validated with an email regex. A DN is resolved by AD rather than by the old `Test-IsValidDN` helper.

To select a domain controller and output properties:

```powershell
Get-ReportChain -SamAccountName 'manager01' -DomainController 'dc01.example.com' -Properties SamAccountName, Mail, Manager
```

The same server is used for manager resolution and the report query. With no `-DomainController`, normal AD cmdlet server selection applies. The function searches that server's default naming context; it does not walk every domain in the forest.

## Results and errors

By default each result contains `SamAccountName`, `UserPrincipalName`, `Mail`, `Manager` and `DirectReports`. Supply `-Properties` for a different selection; `'*'` requests all available user properties and can be substantially more expensive.

No matching reports is a valid empty result. A missing or ambiguous manager lookup and directory access failures raise errors instead of being presented as “no reports.” Handle them separately in a scheduled workflow:

```powershell
try {
    $reports = @(Get-ReportChain -SamAccountName 'manager01' -ErrorAction Stop)
    Write-Host "Found $($reports.Count) reports."
}
catch {
    Write-Error "Reporting-chain query failed: $($_.Exception.Message)"
    throw
}
```

The downloadable implementation escapes both UPN and DN values for their LDAP filter context and has no dependency on the older email/DN validation helpers. It outputs selected objects rather than buffering the full result set inside the function.

This remains a directory query: stale or missing manager attributes change the result, and query time depends on directory size, scope and DC load. The earlier article's timing was an observation from that environment, not a guarantee for this function.

The revised lookup, escaping and error paths have been checked with synthetic directory responses; a live AD environment is still required to validate permissions, server selection and the resulting hierarchy before production use.

References: [Get-ADUser](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduser) and [LDAP search filters](https://learn.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax).
