---
title: "PowerShell convert string to title case"
excerpt: "In this article we will explore how to convert a string in mixed case into a Title Case String."
categories:
  - PowerShell
tags:
  - PowerShell
  - String Conversion
  - PowerShell Title Case

toc: true
last_modified_at: 2026-11-02
---

Python's `str.title()` is a convenient starting point for experimenting with case conversion. In PowerShell, .NET's `TextInfo.ToTitleCase()` provides a similar operation, but neither method knows how a particular person wants their name written.

## Comparison does not change the text

PowerShell's usual string comparison operators are case-insensitive by default. That does not mean strings lose their case:

```powershell
$first = 'A String'
$second = 'a strinG'
$first -eq $second
# True
$first -ceq $second
# False
```

`-ceq` requests a case-sensitive comparison. Neither comparison rewrites the input. Case conversion is a separate operation.

## Pick the culture deliberately

For display text intended to follow the current user's culture:

```powershell
$textInfo = (Get-Culture).TextInfo
$textInfo.ToTitleCase('STRing WIth Mixed CaSe')
```

For a workflow whose output should follow a known language regardless of the host's locale:

```powershell
$culture = [Globalization.CultureInfo]::GetCultureInfo('en-US')
$text = 'STRing WITH Mixed CaSe'
$culture.TextInfo.ToTitleCase($text)
# String WITH Mixed Case
```

All-uppercase words can be preserved as acronyms. That is why `WITH` remains uppercase. Lowercasing first changes the policy:

```powershell
$culture.TextInfo.ToTitleCase($text.ToLower($culture))
# String With Mixed Case
```

This also changes real acronyms, so use it only if normalising every word is intended. The same culture is used for both stages to avoid an accidental mixture of casing rules.

## Display names need a policy

Title casing is a mechanical transformation, not a spelling validator or an editorial title-style guide. It cannot reliably infer name particles, preferred capitalisation, acronyms or the correct treatment of every apostrophe and hyphen across languages.

When generating a directory display name, preserve an authoritative name when one exists. If the organisation requires automatic formatting, define the language, exceptions and review process before applying it to every user. Keep that policy separate from the mechanics of calling `ToTitleCase()`.

Reference: [TextInfo.ToTitleCase](https://learn.microsoft.com/en-us/dotnet/api/system.globalization.textinfo.totitlecase).
