---
title: "PowerShell add or remove elements from an Array"
excerpt: "Learn how to add and remove elements from a PowerShell array using list objects."
categories:
  - PowerShell
tags:
  - PowerShell
  - Arrays
  - PowerShell Basics
  - HowTo

toc: true
last_modified_at: 2026-11-02
---

Adding one item to a collection looks simple until `.Add()` replies “Collection was of a fixed size.” The useful distinction is between an **array**, whose length is fixed, and a mutable list.

## Add to an array

```powershell
$items = @(1, 2, 3)
$items += 4
$items.Count
# 4
```

This appends to the value held by `$items`; it does not make the underlying array support `.Add()` or `.Remove()`. For a handful of values, this is often clear enough.

The original post described every `+=` operation as allocating and copying a new array. That was the important performance consideration in older PowerShell versions, but [PowerShell 7.5 optimised array addition](https://learn.microsoft.com/en-us/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations). Keep the version and workload in mind before applying old benchmark advice.

When collecting the output of a loop, you can avoid repeated additions altogether:

```powershell
$items = @(
    foreach ($number in 1..4) {
        $number * 10
    }
)
# 10, 20, 30, 40
```

Each unassigned result inside the loop contributes to the array. Diagnostic messages belong on a separate stream, such as `Write-Verbose`, if they are not meant to become collection entries.

## Use a mutable list

For code that explicitly adds and removes items, a generic list makes that intent clear:

```powershell
$items = [System.Collections.Generic.List[int]]::new()
$items.Add(10)
$items.Add(20)
$items.Add(30)

$removed = $items.Remove(20) # Remove the first matching value; returns a Boolean
$items.RemoveAt(0)          # Remove the item at index zero
$items.ToArray()
# 30
```

`RemoveAt()` takes an index, starting at zero. `Remove()` takes a value. A missing value returns `$false`; an out-of-range index raises an error. Choose `[List[object]]` if the list deliberately contains mixed types.

## Working with an older ArrayList

Existing scripts may use `ArrayList`. Its `.Add()` returns the **index of the new item**, not the collection's length:

```powershell
$legacyItems = [System.Collections.ArrayList]::new()
$firstIndex = $legacyItems.Add('first')
# $firstIndex is 0; Count is 1
[void]$legacyItems.Add('second')
$legacyItems.Count
# 2
```

Suppress that return value when it would otherwise leak into a function's output. A generic list's `.Add()` does not return an insertion index.

## Remove items from an array

Filtering constructs a new array from the values you keep:

```powershell
$values = @(10, 20, 20, 30)
$withoutTwenty = @($values | Where-Object { $_ -ne 20 })
# 10, 30
```

That removes **all matching values**, unlike `List.Remove()`, which removes the first match. Wrapping the expression in `@(...)` preserves array shape when zero or one result remains.

I tend to use explicit types where they help communicate what a variable holds. The main decision here is the collection's behaviour: collect pipeline output into an array, or use a list when in-place additions and removals are part of the algorithm.

Related: [array indexing and empty collections]({% post_url 2019-01-06-PowerShell-Arrays %}) and Microsoft's [array guide](https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-arrays).
