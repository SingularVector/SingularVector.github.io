---
title: "Get User Primary SMTP Address without Exchange module"
excerpt: "How to get user primary SMTP Address when you don't have the Exchange module installed on your machine"

categories:
  - PowerShell Tips
tags:
  - PowerShell
  - Exchange
  - Tips

toc: false
last_modified_at: 2026-11-02
---

When the Exchange module is unavailable, an on-premises Active Directory lookup can read the primary SMTP entry stored in `proxyAddresses`. This requires the **ActiveDirectory** module and permission to read the user; it is not an Exchange Online query.

The primary entry uses uppercase `SMTP:`; lowercase `smtp:` marks an alias. Use a case-sensitive comparison and remove the prefix for the resulting email address:

```powershell
$user = Get-ADUser -Identity 'Test.User' -Properties proxyAddresses
$primary = @($user.proxyAddresses | Where-Object { $_ -clike 'SMTP:*' })
if ($primary.Count -ne 1) {
    throw "Expected one primary SMTP entry for $($user.SamAccountName); found $($primary.Count)."
}
$primaryAddress = $primary[0].Substring(5)
```

For a report, keep the result associated with each user and flag missing or inconsistent data:

```powershell
Get-ADUser -Filter * -Properties proxyAddresses | ForEach-Object {
    $primary = @($_.proxyAddresses | Where-Object { $_ -clike 'SMTP:*' })
    [pscustomobject]@{
        SamAccountName = $_.SamAccountName
        PrimarySmtpAddress = if ($primary.Count -eq 1) { $primary[0].Substring(5) } else { $null }
        PrimaryEntryCount = $primary.Count
    }
}
```

Scope `-Filter` or add `-SearchBase` for large directories. This fixes the original loop, which accidentally reused `$testUser` instead of reading each user in turn.

The result reflects the directory attribute you read. In hybrid environments, synchronization and recipient configuration can affect the cloud address; use Exchange's recipient properties when you need to establish the mailbox's actual current primary address. Do not substitute `mail` or the UPN without checking the recipient configuration.

See Microsoft's explanation of [primary and secondary SMTP prefixes](https://techcommunity.microsoft.com/blog/exchange/fun-with-changing-e-mail-addresses/609781).
