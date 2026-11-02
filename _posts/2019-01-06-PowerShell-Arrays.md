---
title: "PowerShell Arrays"
excerpt: "Everything you always wanted to know about PowerShell Arrays and never dared to ask"
categories:

  - PowerShell
tags:
  - PowerShell
  - Hash
  - PowerShell Core
  - Hashtables
  - PowerShell Arrays
  - Lists
last_modified_at: 2026-11-02
---

PowerShell frequently gives you several objects from one command. An array is an ordered collection of values; understanding its shape avoids the familiar “it worked until the query returned only one user” problem.

## Create and index an array

```powershell
$numbers = @(100..110)
$numbers.Count
# 11
$numbers[0]
# 100
$numbers[5]
# 105
$numbers[6]
# 106
$numbers[-1]
# 110
```

Both ends of `100..110` are included. Indices start at zero, so the sixth element is at index 5. The earlier example incorrectly showed 105 as the result of index 6.

Use `foreach` to visit the values in order:

```powershell
foreach ($number in $numbers) {
    $number * 2
}
```

The loop variable contains the **value**, not its index. If the position matters, use a `for` loop with an index variable.

## Preserve zero, one and many results

A command assigned directly to a variable can produce `$null`, a single object or an array, depending on its output. Wrap the command in an array subexpression when the calling code needs an array in every case:

```powershell
$logs = @(Get-ChildItem -LiteralPath '.' -Filter '*.log' -File -ErrorAction Stop)
$logs.Count
```

The wrapper controls result shape, not error handling. `-ErrorAction Stop` prevents a failed directory read from looking like a successful empty result.

## Typed arrays and updates

```powershell
[int[]]$numbers = @(100..110)
$numbers[0] = 200
$numbers.SetValue(201, 1)
$numbers[0..2]
# 200, 201, 102
```

`[int[]]` constrains the element type. Values must be convertible to integers; incompatible assignments fail. An array's length remains fixed, but its elements can be replaced.

For additions, removals and mutable lists, see [add or remove elements]({% post_url 2018-12-24-Add-Remove-Items-From-Array %}). In particular, array `+=` performance differs between older PowerShell releases and the optimisation introduced in 7.5.

## Removing the last item safely

A range such as `0..($array.Count - 2)` is not a safe general slice: for an empty or one-item array it creates a descending range, rather than no indices. One approach that handles all three cases is:

```powershell
$items = @('first', 'second', 'third')
$withoutLast = @(
    for ($index = 0; $index -lt ($items.Count - 1); $index++) {
        $items[$index]
    }
)
# first, second
```

This produces an empty array when `$items` has zero or one element. It leaves the original array unchanged.

## Empty, null and missing are different

```powershell
$items = @()            # An empty array
$items.Count           # 0
$items = $null         # The variable now holds null, not an empty array
Remove-Variable items  # Remove the variable from this scope
```

Assigning `$null` releases that variable's reference; it does not empty an array object still referenced elsewhere. The original advice to use `Remove-Item` was also misleading: that command acts on a provider path, not directly on an array value.

Reference: Microsoft's [array guide](https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-arrays).
