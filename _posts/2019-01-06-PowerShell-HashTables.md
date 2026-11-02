---
title: "PowerShell Hashtables"
excerpt: "Everything you always wanted to know about PowerShell Hashtables  and never dared to ask"
categories:

  - PowerShell
tags:
  - PowerShell
  - Hash
  - PowerShell Core
  - Hashtables
  - PowerShell Arrays
  - Dictionaries
last_modified_at: 2026-11-02
---

Hashtables played a large part in the first substantial automation script I wrote. They remain useful when a value has a meaningful lookup key, rather than just a position in a list.

## Create, read and update

```powershell
$ages = @{
    John = 31
    Jim = 42
    Jane = 35
}
$ages['Jane']
# 35
$ages['Jane'] = 36
$ages.Add('Jo', 28)
```

Each key must be unique. `.Add()` fails if it already exists; indexed assignment creates a key or replaces its existing value. PowerShell's ordinary hashtable literals use case-insensitive string keys, so `Jane` and `jane` refer to the same entry in this example.

Use `.ContainsKey()` to distinguish a missing entry from a present entry whose value is `$null`:

```powershell
$settings = @{ Proxy = $null }
$settings.ContainsKey('Proxy')
# True
$settings.ContainsKey('Timeout')
# False
```

An ordinary hashtable does not promise an insertion order. Use `[ordered]@{...}` when presentation order matters, and do not cast it back to `[hashtable]` if you need to retain that behaviour.

## A lookup table in an AD workflow

In one customer automation, a Help Desk operator selected a city in a web interface and a back-end script moved the user to the appropriate OU. The lookup was the useful part: city names mapped to configured destination DNs.

```powershell
$ouByCity = @{
    'New York' = 'OU=New York,DC=example,DC=com'
    'Los Angeles' = 'OU=Los Angeles,DC=example,DC=com'
    'Chicago' = 'OU=Chicago,DC=example,DC=com'
}
$userCity = 'New York'
$userIdentity = 'Test.User'

if (-not $ouByCity.ContainsKey($userCity)) {
    throw "No destination OU is configured for '$userCity'."
}

$user = Get-ADUser -Identity $userIdentity -ErrorAction Stop
Move-ADObject -Identity $user.DistinguishedName -TargetPath $ouByCity[$userCity] -WhatIf -ErrorAction Stop
```

This requires the ActiveDirectory module, a reachable DC and appropriate rights. `-WhatIf` previews the move; it does not verify that a later move will succeed. Review the destination before removing it. The original `Move-ADUser -DestinationPath` command was incorrect: moving the directory object uses `Move-ADObject -TargetPath`.

## Nested data

```powershell
$location = @{
    City = 'New York'
    Details = @{
        CountryCode = 840
        IsoCode = 'US'
    }
}
$location['Details']['IsoCode']
# US
```

Bracket notation is explicit about key access, especially when a key has spaces or shares a name with a dictionary member such as `Keys` or `Count`.

## Choose the CSV shape

For one row whose columns are the keys, convert the map to an object:

```powershell
$record = [ordered]@{ City = 'New York'; CountryCode = 840 }
[pscustomobject]$record | Export-Csv -LiteralPath './location.csv' -NoTypeInformation
```

For one row per key/value pair, enumerate the entries instead:

```powershell
$ages.GetEnumerator() |
    Sort-Object Key |
    Select-Object @{Name='Name'; Expression={$_.Key}}, @{Name='Age'; Expression={$_.Value}} |
    Export-Csv -LiteralPath './ages.csv' -NoTypeInformation
```

A nested hashtable is not automatically flattened into relational CSV columns. Choose an explicit schema for nested data; `ConvertTo-Json -Depth` can be more suitable when the receiving system expects a hierarchy.

`Out-String` produces human-readable formatting, not a stable interchange format. Use it for diagnostics only when that is the intended output, and avoid logging secret values from a configuration map.

References: [about_Hash_Tables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_hash_tables) and [Move-ADObject](https://learn.microsoft.com/en-us/powershell/module/activedirectory/move-adobject).
