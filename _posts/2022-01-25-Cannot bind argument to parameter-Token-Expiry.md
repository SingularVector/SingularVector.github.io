---
title: "Cannot bind argument to parameter TokenExpiryTime because it is null - Error Message"
excerpt: "When opening a PowerShell session to both on-prem and Exchange online in the same window cannot bing argument to parameter TokenExpiryTime because is null error message could be displayed. Let's explore how to solve this."
categories:
  - PowerShell
  - Exchange
  - Office 365

tags:
  - PowerShell
  - Office365
  - Exchange

toc: true
last_modified_at: 2026-11-02
---

## Exchange Online Certificate Based authentication

This is a **January 2022 troubleshooting note**, observed with ExchangeOnlineManagement 2.0.4 and 2.0.5 while migrating mailbox automation to app-only certificate authentication. Modern authentication is not synonymous with certificate authentication: interactive administrators and unattended applications use different supported flows.

For current connections, follow Microsoft's [Exchange Online PowerShell connection guide](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell) and [app-only authentication procedure](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2). This session-order workaround has not been revalidated against current modules and is not a general solution to token expiry errors.

At the time, I was updating one of our automations, responsible for the whole life-cycle of our mailboxes, to ditch old credential objects in favor of the more secure Certificate Authentication.

This is when I encountered the _cannot bind argument to parameter 'token expiry time' because it is null._ error message.

## Multiple PowerShell Exchange Sessions

When operating an hybrid environment it is pretty common to open, in the same window/session, a PowerShell connection to both Exchange on-prem and Exchange Online.

This is required as part of the configuration, usually creation of the mailbox, takes place in on-prem for example via the _New-RemoteMailbox_ cmdlet while other parts of the configuration are performed directly online for example when delegating mailbox permissions. 

While debugging my workflow I have noticed that, while trying to retreive mailbox information from the on-prem server, an exception was being thrown

```powershell
# Cmdlet I was running
Get-RemoteMailbox -Identity $userUpn

# Part of the exception message
Cannot bind argument to parameter 'token expiry time' because it is null.
```

It took me a bit to figure this out as no exception was thrown during the connection *phase* either nor there was any other obvious pointer.

When I was about to give up and open a ticket with Microsoft, I discovered that establishing a connection to Exchange Online followed by a connection to the on-prem server was yielding the desired result. In my workflow I had this the other way around, first local Exchange and then Online service, which was causing the issue.

**Note:** I have experienced/tested this with version 2.0.4 and 2.0.5 of Exchange Online PowerShell module but other versions could be affected as well.
{: .notice--warning}

I did not establish a root cause in that investigation. The observation was that reversing connection order resolved that workflow's error; it does not establish why it happened.

If you encounter it now, reproduce with supported module versions, record `$PSVersionTable` and the loaded Exchange module version, and test the on-premises and cloud commands independently. Inspect which command `Get-Command Get-RemoteMailbox` resolves to when sessions coexist. Separate processes can help distinguish a session/module interaction from an authentication failure; use your environment's supported connection procedures for each side.
