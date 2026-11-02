---
title: "Store Credentials in PowerShell Script"
excerpt: "Handle PowerShell credentials without hard-coded passwords, with a Windows DPAPI example and clear limits for unattended automation."
categories:

  - PowerShell
  - HowTo
tags:
  - PowerShell
  - PowerShell Core
  - Passwords
  - new-object system.management.automation.pscredential
  - PowerShell create credential
  - PowerShell store credentials in file
last_modified_at: 2026-11-02
---

## Choose the authentication model first

For unattended automation, prefer a workload identity, managed identity or certificate-based application authentication when the target service supports it. When a password is unavoidable, retrieve it from a secret store whose access controls and unattended authentication fit the execution account.

An encrypted password is still a credential. Code running as an identity authorised to decrypt it can recover and use it. Encryption at rest does not replace file permissions, least privilege, rotation or control of the automation host.

## Get-Credential

For an interactive script, prompt rather than placing the password in source code:

```powershell
$credential = Get-Credential
# Pass $credential to a command that accepts -Credential.
```

A `PSCredential` packages a username and a `SecureString`; it does not determine how the destination service authenticates. Confirm that the target command supports this authentication method.

## Plain Text Credentials in Script

Do not put passwords in scripts, command-line arguments or source control. Converting a hard-coded string with `ConvertTo-SecureString -AsPlainText` cannot protect the original literal or remove it from repository history.

## Store Encrypted password in an external file

The following example is **Windows-only** and uses Windows Data Protection API (DPAPI) without an explicit encryption key. Create the file as the same Windows account, on the same machine, that will read it. Use an existing directory with restrictive permissions; the example path is a placeholder, not a directory created by these commands.

```powershell
# One-time interactive setup on the automation host, as its execution account.
$credentialPath = 'C:\Automation\Secrets\service-password.txt'
$credential = Get-Credential
$credential.Password |
    ConvertFrom-SecureString |
    Set-Content -LiteralPath $credentialPath
```

Read the file under that same account and machine context:

```powershell
$credentialPath = 'C:\Automation\Secrets\service-password.txt'
# Replace with the username supplied during setup.
$userName = 'CONTOSO\svc-automation'
$securePassword = (Get-Content -LiteralPath $credentialPath -Raw).Trim() |
    ConvertTo-SecureString
$credential = [System.Management.Automation.PSCredential]::new(
    $userName, $securePassword
)
```

DPAPI binds this example to a Windows user and machine context. It is not a portable deployment format. Anyone able to run code as that account may be able to decrypt the password; physical access is not required. Restrict the file and execution account, and recreate the encrypted file when changing the deployment context or rotating the password.

The protection described here must not be assumed on Linux or macOS. Microsoft documents that `SecureString` contents are not encrypted on non-Windows systems. See [ConvertTo-SecureString](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/convertto-securestring) and [ConvertFrom-SecureString](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/convertfrom-securestring) for the platform and key-handling details.

## Use an Encrypted String in Script

My **[IT-ToolBox](https://github.com/SingularVector/IT-ToolBox)** module provides `New-StringEncryption` and `New-StringDecryption`. I adapted the original helpers from code credited to the TechNet Gallery in the 2019 version of this article. The module has since evolved; the current functions retain their names but use a different interface and ciphertext format.

### IT-ToolBox 3.0: explicit passphrase and authenticated encryption

This example targets **IT-ToolBox 3.0.0**, whose manifest requires **PowerShell 7.4 or later**, on a platform with .NET AES-GCM support. Use the [module’s setup instructions and string-encryption documentation](https://github.com/SingularVector/IT-ToolBox#string-encryption) rather than assuming an older installed copy has the same behaviour.

The examples are deliberately pinned to **IT-ToolBox 3.0.0**. The repository can contain a later module version; if you need to reproduce these exact calls, obtain the [3.0 source revision](https://github.com/SingularVector/IT-ToolBox/tree/5ea85e41a0672847e70716342651af52179ac649) and install that version using its setup instructions. `-RequiredVersion 3.0.0` does not automatically download or downgrade a different checkout.

```powershell
Import-Module IT-ToolBox -RequiredVersion 3.0.0

# Supply these through your application's input and secret-handling mechanism:
# $valueToProtect       - the string being encrypted
# $encryptionPassphrase - a strong passphrase, protected separately from ciphertext
$encryptedValue = New-StringEncryption -StringToEncrypt $valueToProtect `
    -EncryptPassPhrase $encryptionPassphrase

$decryptedValue = New-StringDecryption -EncryptedString $encryptedValue `
    -EncryptPassPhrase $encryptionPassphrase
```

The current implementation uses AES-256-GCM, a fresh random salt and nonce, and PBKDF2-HMAC-SHA256 with 600,000 iterations. Its output begins with `ITTB1.`. Decryption rejects an incorrect passphrase or modified authenticated payload instead of returning plaintext. These details were checked against [the module source at commit 5ea85e4](https://github.com/SingularVector/IT-ToolBox/tree/5ea85e41a0672847e70716342651af52179ac649).

This is string encryption, not an identity-bound secret vault. Anyone with the ciphertext and correct passphrase can decrypt it on a compatible host. Do not put the passphrase alongside the ciphertext in source code. Input, passphrase and decrypted output are managed strings; they cannot be reliably erased from memory. If a destination requires `PSCredential`, converting decrypted text to `SecureString` does not undo that plaintext exposure.

### Historical calls and migration

The original article’s call without `-EncryptPassPhrase` belongs to the historical implementation, not version 3.0. The [legacy functions](https://github.com/SingularVector/IT-ToolBox/tree/5ea85e41a0672847e70716342651af52179ac649/Legacy) defaulted the passphrase and salt to the computer name and used a fixed default vector. This explains the original machine-name dependency, but it was not an enforced restriction to the originating machine: reproducing those inputs could reproduce the key elsewhere.

Version 3.0 requires an explicit passphrase and generates salt and nonce internally. Its decoder deliberately rejects historical ciphertext. Follow the module’s **Legacy migration** instructions in a separate session: recover existing data with the original implementation and original inputs, then re-encrypt it with the modern function. Preserve the original ciphertext until recovery and migration have been verified. Legacy ciphertext does not authenticate its contents.

## Closing Notes

For a secret store integration, review authentication, auditability, rotation and the capabilities of the vault provider. PowerShell [SecretManagement](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview) provides a vault abstraction; Microsoft now describes those modules as feature complete, maintained for security and critical fixes. Do not assume any particular vault configuration will work unattended.

The encryption functions discussed here are part of my **[IT-ToolBox module](https://github.com/SingularVector/IT-ToolBox)**; consult its documentation for version-specific usage and migration.

For Exchange Online automation, see the [certificate authentication guide]({% post_url 2020-09-21-Exchange-Online-Certificate-Based-Authentication %}) and its current Microsoft references.

For the implementation details, failure-path tests and migration steps, see [PowerShell String Encryption in IT-ToolBox 3.0]({% post_url 2026-10-23-PowerShell-String-Encryption-IT-ToolBox %}).
