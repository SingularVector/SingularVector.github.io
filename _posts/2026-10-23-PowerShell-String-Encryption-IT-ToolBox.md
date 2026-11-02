---
title: "PowerShell String Encryption in IT-ToolBox 3.0"
excerpt: "Using New-StringEncryption and New-StringDecryption in IT-ToolBox 3.0, with explicit passphrases, authenticated encryption and a migration path for older data."
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - IT-ToolBox
  - Encryption
  - Automation
toc: true
---

## Same function names, different behaviour

In my earlier article on [storing credentials in PowerShell]({% post_url 2019-02-26-Store-Credentials-in-PowerShell-Script %}), I used two functions from my **IT-ToolBox** module: `New-StringEncryption` and `New-StringDecryption`.

Those functions are still part of the module, but version 3.0 changes how they work. The names remain the same. The parameters, encryption format and handling of older data do not.

In this post I will go through the current implementation, show a couple of examples and explain what needs attention if you already have encrypted strings created with the older functions.

The examples target **IT-ToolBox 3.0.0**, which requires **PowerShell 7.4 or later** and a platform with .NET AES-GCM support. They do not apply to Windows PowerShell 5.1 or the legacy functions.

## What changed

The older functions used `RijndaelManaged`, with optional passphrase and salt parameters that defaulted to the computer name. They also accepted a caller-supplied vector, with a fixed value used when it was omitted.

That computer-name default could make an encrypted value appear tied to a particular machine. It was not a machine access restriction, though. The name was an input to the key derivation: reproducing the same inputs elsewhere could reproduce the key.

Version 3.0 removes those defaults. A passphrase is required, and the function generates the salt and nonce internally for each encryption operation.

The implementation uses **AES-256-GCM**, with a key derived through **PBKDF2-HMAC-SHA256 at 600,000 iterations**. Decryption verifies an authentication tag before returning the string. An incorrect passphrase or a modified authenticated payload causes an exception.

This matters because recovering some text is not enough to establish that encrypted data has not changed. The new format includes that check.

## Encrypting and decrypting a string

First, obtain the module using the [repository setup instructions](https://github.com/SingularVector/IT-ToolBox), then import the version used in this article:

```powershell
Import-Module IT-ToolBox -RequiredVersion 3.0.0
```

For this interactive example I use `Get-Credential` to enter the encryption passphrase without putting it directly in the command history. The username is only a label here; it is not used for encryption.

```powershell
$passphraseInput = Get-Credential -UserName 'string-encryption' `
    -Message 'Enter the encryption passphrase in the password field'

$encryptionPassphrase = $passphraseInput.GetNetworkCredential().Password
```

The functions accept ordinary strings. Calling `GetNetworkCredential().Password` therefore creates a plaintext string in memory. The prompt avoids a hard-coded passphrase; it does not change the function's memory-handling limits.

Now we can encrypt a value:

```powershell
# Demonstration data, not a real password.
$valueToProtect = 'Example configuration value'

$encryptedValue = New-StringEncryption -StringToEncrypt $valueToProtect `
    -EncryptPassPhrase $encryptionPassphrase

$encryptedValue
```

The result starts with `ITTB1.` followed by a Base64-encoded payload. Your output will differ each time, even when the input string and passphrase are unchanged.

To recover the original value, pass the complete result back to the companion function:

```powershell
$decryptedValue = New-StringDecryption -EncryptedString $encryptedValue `
    -EncryptPassPhrase $encryptionPassphrase

$decryptedValue -ceq $valueToProtect
# True
```

The ciphertext can be stored separately and loaded by another script. The passphrase must be supplied through a separate, appropriate secret-handling mechanism. Saving both together in the same script would defeat the reason for separating them.

This prompt is for an interactive demonstration. An unattended job needs a way to obtain its passphrase without waiting for a person.

## What is in the encrypted value

The `ITTB1.` prefix identifies the format. The decoded payload contains:

| Component | Size |
| --- | --- |
| Salt | 16 bytes |
| Nonce | 12 bytes |
| Ciphertext | Same byte length as the UTF-8 plaintext |
| Authentication tag | 16 bytes |

The salt and nonce are stored with the ciphertext so that decryption has the inputs it needs. The passphrase is not included.

The format also fixes the derivation settings. Callers no longer supply `EncryptSalt` or `IntersectingVector`, and the decoder does not try different historical formats until one happens to produce output.

The implementation limits plaintext to **1 MiB of UTF-8 data** and the passphrase to **4,096 characters**. These functions handle strings; they are not a file-encryption interface.

## Checking the failure path

A successful round trip is useful, but I also want to know what happens when decryption should fail.

Using the value created above, try a different passphrase:

```powershell
try
{
    $null = New-StringDecryption -EncryptedString $encryptedValue `
        -EncryptPassPhrase ($encryptionPassphrase + '-different')
}
catch [System.Security.Cryptography.CryptographicException]
{
    Write-Output 'Decryption rejected the incorrect passphrase.'
}
```

For this example, use a passphrase comfortably below the maximum length so that the altered value remains within the parameter limit.

The module's [string-encryption tests](https://github.com/SingularVector/IT-ToolBox/blob/5ea85e41a0672847e70716342651af52179ac649/Tests/StringEncryption.Tests.ps1) cover more than this: Unicode and multiline strings, empty input, fresh salts and nonces, incorrect passphrases, and changes to the salt, nonce, ciphertext and tag. They also check malformed input and size limits.

There is an independent fixture generated with Python's cryptography library. That gives the tests a value produced outside these two functions, rather than relying entirely on an encrypt/decrypt pair that could share the same mistake.

## Migrating existing encrypted strings

An old encrypted value cannot be passed directly to the version 3.0 decoder. The new function rejects historical ciphertext rather than silently falling back to the old implementation.

The original functions remain in the repository's **Legacy** directory for recovering existing data. They are not imported by the current module.

The migration sequence is:

1. Preserve the original ciphertext and identify the inputs used to create it.
2. In a separate session, use the original decoder with the original passphrase, salt and vector. If the call used computer-name defaults, you need the original computer name.
3. Verify the recovered value against a trusted reference or its intended use. The legacy format does not authenticate its contents, so successful decryption alone does not establish integrity.
4. Encrypt the recovered value with the modern function and a strong, separately protected passphrase.
5. Verify the new value before replacing the original data or changing the consuming script.

Do not load the legacy and modern functions into the same session and assume the function name tells you which implementation is running. They deliberately retain the same names. The [module's migration notes](https://github.com/SingularVector/IT-ToolBox#legacy-migration) describe the compatibility boundary.

## Where I would use this

These functions provide a way to encrypt and authenticate a string when the application already has an appropriate way to manage the passphrase.

They do not decide who should be allowed to decrypt it. Anyone with the ciphertext and the correct passphrase can use a compatible implementation to recover the value. There is no Windows user or originating-machine restriction in the modern format.

The code clears temporary plaintext and key byte arrays, but managed strings cannot be reliably erased. The input value, passphrase and returned plaintext remain subject to that limitation. Converting the returned value to `SecureString` does not undo the plaintext exposure that has already occurred.

For service authentication, I would first check whether the service supports a workload identity, managed identity or certificate-based application authentication. When a password is required, a secret store may be the better place to manage access, rotation and retrieval. String encryption is useful, but the script still needs an answer to the question: where does its decryption passphrase come from?

The implementation, tests and version-specific documentation are available in my **[IT-ToolBox repository](https://github.com/SingularVector/IT-ToolBox)**. If you already use the older functions, check the migration notes before updating the module.
