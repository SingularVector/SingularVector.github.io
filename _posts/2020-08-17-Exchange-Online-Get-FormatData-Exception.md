---
title: "Exchange Online - Data returned by the remote Get-FormatData command is not in the expected format"
excerpt: "When opening an Exchange Online session via PowerShell error 'Data returned by the remote Get-FormatData command is not in the expected format' is returned and no connection is opened - Let's see how to solve it"
categories:
  - PowerShell
  - Office365
  - Troubleshooting
tags:
  - PowerShell
  - Office365
  - Exchange Online
  - TroubleShooting

last_modified_at: 2026-10-23
toc: false
header:
    teaser: "/assets/images/shared/ExchangeLogo.png"
---

## Historical remote PowerShell issue

**Updated 23 October 2026:** This article records a 2020 Exchange Online remote-session formatting error. The `SerializationLevel=Full` connection-URI workaround below is retained as historical context, not a current troubleshooting instruction. Start with a supported ExchangeOnlineManagement module and Microsoft’s [current connection guide](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell).
{: .notice--warning}

For an interactive connection using the current module’s modern authentication flow, the documented pattern is:

```powershell
# Replace with your administrator account; follow the authentication prompt.
Connect-ExchangeOnline -UserPrincipalName 'admin@contoso.onmicrosoft.com'
```

For unattended jobs, use [app-only certificate authentication](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2) or a [supported managed identity](https://learn.microsoft.com/en-us/powershell/exchange/connect-exo-powershell-managed-identity). Do not add a legacy endpoint URI to a current deployment solely because an error message resembles the historical report.

## Original symptom and workaround

The original workflow failed while opening a remote session with:

> Data returned by the remote Get-FormatData command is not in the expected format.

At the time, a reported workaround added `SerializationLevel=Full` to the old endpoint. Shown as text rather than an executable recommendation:

```text
Historical only:
Connect-ExchangeOnline -ConnectionUri "https://outlook.office365.com/powershell-liveid?SerializationLevel=Full"
```

The original report did not establish a universal root cause. Its feedback form and performance claim have been removed because they do not provide a current diagnostic path. Record the module version, host environment and full error when investigating a current connection failure, then follow the current documentation for that environment.
