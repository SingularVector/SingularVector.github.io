---
title: "PowerShell Create Credential Object"
toc: false
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - PowerShell Basics
  - PowerShell Core
  - PowerShell create credential
  - new-object system.management.automation.pscredential
last_modified_at: 2026-11-02
---

A `PSCredential` holds a username and a `SecureString` password. Use it when a cmdlet explicitly accepts credentials; it does not make password authentication available to every service or handle MFA for you.

## Interactive scripts

The simplest way to obtain the object is to prompt:

```powershell
$credential = Get-Credential -Message 'Enter the account required by the target service'
```

Pass `$credential` to the parameter documented by the target cmdlet, often `-Credential`. Check the command's help: the parameter is not universally named `-PSCredential`, and accepting the object does not necessarily mean that the whole command runs as that user.

If you already have a username and need to prompt only for its password, construct the object directly:

```powershell
$userName = 'CONTOSO\service-account'
$password = Read-Host -Prompt 'Password' -AsSecureString
$credential = [System.Management.Automation.PSCredential]::new($userName, $password)
```

Both approaches require a person at the prompt. Converting a hard-coded password with `ConvertTo-SecureString -AsPlainText` would still leave the password in the source file and its history.

## Unattended scripts

First check the service's supported automation authentication: managed identity, workload identity federation or certificate-based application authentication may remove the need for a user password. The appropriate choice depends on the service and hosting environment.

For a legacy endpoint that requires a password, retrieve it from a secret store accessible to the automation identity. If the store returns a `PSCredential`, use that object directly; if it returns a `SecureString`, construct the object as above without prompting. The job must be able to authenticate to the store without human intervention.

`SecureString` is a compatibility type, not a secret store; its contents are not encrypted in memory on non-Windows systems. See [Get-Credential](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-credential) and the [SecureString platform note](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/convertfrom-securestring).

For storage options and their limitations, see [Store Credentials in PowerShell Script]({% post_url 2019-02-26-Store-Credentials-in-PowerShell-Script %}).
