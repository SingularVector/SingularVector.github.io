---
title: "PowerShell check if string is a valid Guid"
excerpt: "Releasing a PowerShell function that will check if an input string is a valid Guid or not"
categories:
  - PowerShell
  - Functions
tags:
  - PowerShell
  - PowerShell Functions
last_modified_at: 2026-11-02
---

PowerShell can generate a GUID with `New-Guid` or `[guid]::NewGuid()`. To validate a string, use .NET's built-in `Guid.TryParse` instead of maintaining a GUID regular expression:

```powershell
function Test-IsGuid {
    [OutputType([bool])]
    param (
        [AllowNull()]
        [AllowEmptyString()]
        [string]$ObjectGuid
    )

    $parsed = [guid]::Empty
    [guid]::TryParse($ObjectGuid, [ref]$parsed)
}

Test-IsGuid -ObjectGuid '4a6b7fcb-f1e4-42c8-ae6f-d3862dbbcbca'
# True
Test-IsGuid -ObjectGuid '4444-23-ec-789'
# False
Test-IsGuid -ObjectGuid '(CA761232-ED42-11CE-BACD-00AA0057B223)'
# True
```

`TryParse` supports the standard GUID representations, including braces, parentheses and the compact form without hyphens. It also accepts surrounding whitespace. The earlier regex could accept mismatched delimiters and inconsistent hyphens; parsing delegates those rules to .NET.

If an input contract requires the hyphenated `D` format, use `TryParseExact`:

```powershell
$parsed = [guid]::Empty
[guid]::TryParseExact('4a6b7fcb-f1e4-42c8-ae6f-d3862dbbcbca', 'D', [ref]$parsed)
# True
```

Parsing checks representation, not whether the GUID exists in your application or directory. `[guid]::Empty` is syntactically valid; reject it separately if your application requires a nonzero identifier.

References: [Guid.TryParse](https://learn.microsoft.com/en-us/dotnet/api/system.guid.tryparse) and [Guid.TryParseExact](https://learn.microsoft.com/en-us/dotnet/api/system.guid.tryparseexact).
