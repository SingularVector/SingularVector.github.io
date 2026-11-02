---
title: "PowerShell - Get day of weekday"
excerpt: "In this short post we will see how we can use PowerShell to get an integer representing the number associated with the day of the week for the current date."
categories:
  - PowerShell
  - Howto

tags:
  - PowerShell
  - Tips
  - HowTo

toc: true
header:

last_modified_at: 2026-11-02
---

`Get-Date` returns a `DateTime`. Its `DayOfWeek` property is a .NET enum, displayed as a name such as `Monday`; it is not a string.

```powershell
$date = Get-Date -Year 2022 -Month 2 -Day 21
$date.DayOfWeek
# Monday

[int]$date.DayOfWeek
# 1
```

The numeric mapping is **Sunday = 0 through Saturday = 6**, not 1 through 7. Cast to `[int]` rather than accessing the enum's underlying `value__` field.

If a database or report requires Monday = 1 through Sunday = 7, map that explicitly:

```powershell
$isoWeekday = (([int]$date.DayOfWeek + 6) % 7) + 1
```

Document which convention you store: the values fit in a SQL `tinyint`, but the column's type alone does not tell readers what Sunday means.

See [.NET DayOfWeek](https://learn.microsoft.com/en-us/dotnet/api/system.dayofweek).
