---
title: "PowerShell - Get all members of a group recursively"
excerpt: "Query nested AD group membership with LDAP matching rules, with explicit object types, filter escaping and directory scope limits."
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

In the earlier [Get-ADGroupMember timeout article]({% post_url 2019-09-12-Get-AdGroupMember-Timeout %}), a reader asked how to include nested membership. Active Directory's matching rule `1.2.840.113556.1.4.1941` can follow the `memberOf` links on the server, without a client-side recursive loop.

## Retrieve users through nested groups

This requires the ActiveDirectory module, directory read access and a reachable domain controller. Resolve the group first, then escape its DN as an **LDAP filter value**:

```powershell
$group = Get-ADGroup -Identity 'TestGroup' -ErrorAction Stop
$escapedDn = $group.DistinguishedName.Replace('\', '\5c').Replace('*', '\2a').Replace('(', '\28').Replace(')', '\29').Replace([string][char]0, '\00')
$ldapFilter = "(memberOf:1.2.840.113556.1.4.1941:=$escapedDn)"

Get-ADUser -LDAPFilter $ldapFilter -Properties mail -ErrorAction Stop |
    Select-Object SamAccountName, UserPrincipalName, mail
```

DN escaping and filter escaping are different layers. Even a DN returned by AD can contain characters, such as a literal backslash or parentheses, that need escaping when embedded in a filter. The original example also defined `$ldapFilter` but passed `$filter`; the commands above use the same variable throughout.

`Get-ADUser` returns users, not every object class. If you also need nested groups and computers, query objects instead:

```powershell
Get-ADObject -LDAPFilter $ldapFilter -Properties mail -ErrorAction Stop |
    Select-Object Name, ObjectClass, DistinguishedName, mail
```

## Understand the result's boundary

The query follows directory links within the search scope; it does not produce a Windows access token or a complete cross-forest access assessment. Primary-group membership is not represented by the ordinary `memberOf` backlink. Cross-domain groups and foreign security principals need additional handling for a complete membership report.

If you need only one domain, use the same `-Server` for group resolution and the membership query and set an appropriate `-SearchBase` when the result set must be restricted. An empty result can be legitimate, for example when a group contains no users within that scope. A directory error is a different outcome and should fail the calling workflow.

This can reduce client-side round trips, but its cost still depends on nesting, scope, directory size and DC load. Measure it in your environment rather than treating it as a guaranteed timeout workaround.

References: Microsoft's [LDAP search filter syntax and matching rules](https://learn.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax) and [Get-ADGroupMember](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroupmember).
