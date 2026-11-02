---
title: "PowerShell Strongly Typed Variables"
excerpt: "PowerShell Strongly Typed Variables, what they are, why you should care and why you should use them in your code to avoid pitfalls and potential issues with data types"
categories:

  - PowerShell
  - Coding Habits
  - PowerShell Best Practice
tags:
  - PowerShell
  - PowerShell Core
  - Variables
  - PowerShell Variables
last_modified_at: 2026-11-02
---

PowerShell lets a variable hold an integer now and a string later. That flexibility is useful, but an automation workflow often has a narrower contract: a retry count should remain an integer even if it came from a text configuration file.

## Values have types

```powershell
$value = 1000
$value.GetType().Name
# Int32
$value = 'Now this is text'
$value.GetType().Name
# String
```

The integer object did not change into a string. The variable was assigned a different object. “Dynamically typed” describes this variable behaviour; it does not mean PowerShell values have no type.

## Constrain the variable

```powershell
[int]$retryCount = 3
$retryCount = '5'
$retryCount.GetType().Name
# Int32
```

A type constraint attempts conversion on later assignments. The text `'5'` is convertible; arbitrary text such as `'many'` is not. A failed conversion leaves the previous value in place, so handle the error rather than continuing as though the new value was accepted.

A typed string illustrates a different trade-off:

```powershell
[string]$message = 'Waiting'
$message = Get-Date
$message.GetType().Name
# String
```

The date is converted to text. That preserves the declared type but loses the original date object and introduces formatting considerations. A type constraint is not proof that the value has the business meaning you intended.

## Casting one expression is different

```powershell
$source = '12'
$converted = [int]$source
$source.GetType().Name
# String
$converted.GetType().Name
# Int32
```

`[int]$source` converts that expression. `[int]$source = ...` applies a constraint to the variable. The distinction matters when checking which later assignments are allowed.

You can replace a constraint deliberately with another typed assignment; it is not necessary to invent a new variable name:

```powershell
[int]$value = 10
[string]$value = 'A deliberate change of contract'
```

For clarity, avoid changing a variable's role partway through a long function, even though the language permits it.

## Parameters also need validation

A type describes representation; validation describes accepted values:

```powershell
function Get-RetryDelay {
    param (
        [ValidateRange(1, 10)]
        [int]$Attempt
    )
    [Math]::Min(60, $Attempt * 5)
}
Get-RetryDelay -Attempt 3
# 15
```

A negative integer is still an integer, but this function rejects it because it violates the contract. Use explicit parsing for external data when culture and formatting matter; see [string-to-date conversion]({% post_url 2020-08-03-PowerShell-Convert-String-To-Datetime %}).

I use explicit types where they make a script's intent easier to see during review. They are especially useful at input boundaries and for typed collections. They do not replace clear names, validation or error handling, and do not automatically make every local variable safer.

References: [about_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_variables) and [about_Type_Conversion](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_type_conversion).
