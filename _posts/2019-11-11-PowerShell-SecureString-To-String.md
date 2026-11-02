---
title: "Convert a secure string to plain text"
toc: false
categories:
  - PowerShell
  - Functions
tags:
  - PowerShell
  - PowerShell Functions
last_modified_at: 2026-11-02
---

Some APIs still require a plain text password even when the calling script holds a `SecureString`. Convert it only at that boundary, and avoid printing or logging the result.

## PowerShell 7

```powershell
$securePassword = Read-Host -Prompt 'Password' -AsSecureString
$plainPassword = ConvertFrom-SecureString -SecureString $securePassword -AsPlainText

# Pass $plainPassword to the API that requires it.
# Do not write it to output or logs.
$plainPassword = $null
```

`-AsPlainText` was added in PowerShell 7. Without that switch, `ConvertFrom-SecureString` produces a serialized representation intended for storage, not the plain text password. Its protection depends on the platform and key options; do not assume the default output is encrypted on non-Windows systems.

## Windows PowerShell 5.1

For compatibility with 5.1, a credential object exposes the password without manual unmanaged-memory allocation:

```powershell
$securePassword = Read-Host -Prompt 'Password' -AsSecureString
$credential = [System.Management.Automation.PSCredential]::new('unused', $securePassword)
$plainPassword = $credential.GetNetworkCredential().Password

# Pass $plainPassword to the API here.
$plainPassword = $null
$credential = $null
```

The temporary username is not used to authenticate; the object is only a bridge to the password string. Clearing a variable does not guarantee that all copies of an immutable .NET string have been erased from memory. Likewise, passing a password as an external program's command-line argument can expose it through process inspection; prefer the program's supported secret-input mechanism.

The earlier version of this post allocated a BSTR without freeing it. These examples avoid that allocation. See [ConvertFrom-SecureString](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/convertfrom-securestring) and [NetworkCredential.Password](https://learn.microsoft.com/en-us/dotnet/api/system.net.networkcredential.password).

Related: [Create a credential object]({% post_url 2019-11-07-PowerShell-Create-Credential-Object %}) and [store credentials safely]({% post_url 2019-02-26-Store-Credentials-in-PowerShell-Script %}).
