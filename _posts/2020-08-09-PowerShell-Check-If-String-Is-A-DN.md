---
title: "PowerShell Validate Distinguished Name"
excerpt: "Distinguish DN syntax, AD object lookup and LDAP filter escaping before validating distinguished-name input in PowerShell."
categories:
  - PowerShell
  - HowTo
  - Identity Management
tags:
  - PowerShell
  - Active Directory
  - Identity Management

header:
    teaser: "/assets/images/shared/AD_Logo.png"

toc: false
last_modified_at: 2026-11-02
---

A distinguished name (DN) identifies an entry in a directory. While building [the reporting-chain query]({% post_url 2020-08-05-Active-Directory-Get-Report-Chain %}), I needed to decide whether an input could be used as an AD object identity.

There are three different checks here: whether text has valid DN syntax, whether that object exists in the directory, and whether its value is safe to embed in an LDAP filter. One regex does not answer all three.

## Resolve an identity against AD

When the task needs an actual AD object, let the directory resolve it. This requires the ActiveDirectory module, directory access and appropriate read permissions:

```powershell
$inputDn = 'CN=Test User,OU=Users,DC=example,DC=com'
$object = Get-ADObject -Identity $inputDn -ErrorAction Stop
$object.DistinguishedName
```

Use `Get-ADUser` or `Get-ADGroup` when you specifically require that object class. A failed lookup needs diagnosis: it can mean an invalid or missing identity, insufficient access or an unavailable server. It is not automatically a DN syntax failure.

## Escape values for a search filter

If you put the resolved DN in a filter, escape it for that filter context:

```powershell
$escapedDn = $object.DistinguishedName.Replace('\', '\5c').Replace('*', '\2a').Replace('(', '\28').Replace(')', '\29').Replace([string][char]0, '\00')
$filter = "(manager:1.2.840.113556.1.4.1941:=$escapedDn)"
Get-ADUser -LDAPFilter $filter -ErrorAction Stop
```

This preserves DN escaping already present in the attribute while representing special filter characters as literals. It does not construct a DN from arbitrary name components; that has separate escaping rules.

## What happened to Test-IsValidDN?

The original post published a regex-based helper with that name. It recognized a limited subset of common `CN`/`OU`/`DC` strings, not the full LDAP DN grammar. Valid names can contain escaped separators, multivalued relative names, other attribute types and numeric OIDs. Passing that regex was also no proof that an object existed.

The old helper may still appear in earlier versions of my repositories. Treat it as a historical heuristic, not a general validator or a security boundary. For offline syntax validation, use a parser that implements the DN specification and test the exact forms your application accepts.

References: [RFC 4514: DN string representation](https://www.rfc-editor.org/rfc/rfc4514), [RFC 4515: filter string representation](https://www.rfc-editor.org/rfc/rfc4515) and Microsoft's [search filter escaping rules](https://learn.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax).
