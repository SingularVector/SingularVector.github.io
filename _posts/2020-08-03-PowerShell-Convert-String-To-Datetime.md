---
title: "PowerShell convert string to datetime"
excerpt: "In this post we will see how we can easily convert a string into a datetime object."
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Performance Tips

header:
    teaser: "/assets/images/string-to-datetime/BackToTheFuture.png"
last_modified_at: 2026-11-02
---

Dates become troublesome when an automation receives a string such as `02/09/2020`. Is that 2 September or 9 February? The date itself is not ambiguous; the string's format contract is.

## Keep dates as dates while calculating

```powershell
$expirationDate = (Get-Date).AddDays(30)
$expirationDate.GetType().Name
# DateTime
```

Format a string when you need to display or export it. Do not convert to text early and then rely on a later machine to guess the format back.

## Parse a known format and culture

```powershell
$culture = [Globalization.CultureInfo]::InvariantCulture
$date = [datetime]::ParseExact('02/09/2020', "dd'/'MM'/'yyyy", $culture)
$date.ToString('yyyy-MM-dd', $culture)
# 2020-09-02
```

The quoted slashes require literal `/` characters; an unquoted `/` in a custom date pattern is the culture's date-separator placeholder. `MM` means month, while `mm` means minutes. Numeric month/day order still has to come from the input specification.

If month names are present, select their actual language rather than relying on the host's current culture:

```powershell
$english = [Globalization.CultureInfo]::GetCultureInfo('en-US')
$date = [datetime]::ParseExact('02-Sep-2020', 'dd-MMM-yyyy', $english)
$date.ToString('yyyy-MM-dd', [Globalization.CultureInfo]::InvariantCulture)
# 2020-09-02
```

A four-digit year avoids the additional rules involved in interpreting two-digit years. The original example passed `$null` as the provider, which meant current-culture behaviour rather than a portable format guarantee.

## Validate input without a parsing exception

For data that may contain invalid values, use `TryParseExact` and check its Boolean result:

```powershell
$inputDate = '31/02/2020'
$parsedDate = [datetime]::MinValue
$valid = [datetime]::TryParseExact(
    $inputDate,
    "dd'/'MM'/'yyyy",
    [Globalization.CultureInfo]::InvariantCulture,
    [Globalization.DateTimeStyles]::None,
    [ref]$parsedDate
)
if ($valid) {
    $parsedDate
}
else {
    Write-Warning "Invalid date for the expected format: '$inputDate'."
}
```

Do not use `$parsedDate` as an accepted value when `$valid` is false. A string with the right arrangement of digits can still describe an impossible date.

## Time zones are another part of the contract

A date-only value such as `2020-09-02` contains no time-zone or UTC-offset information. Parsing it does not establish that it represents a UTC instant. For timestamps with offsets, consider `DateTimeOffset` and document how the receiving system expects offsets to be retained or normalised.

Likewise, AD attributes and SQL columns have different native representations; use the documented type or conversion for the attribute/column instead of treating every date-looking value as a formatted string.

References: [DateTime.ParseExact](https://learn.microsoft.com/en-us/dotnet/api/system.datetime.parseexact), [DateTime.TryParseExact](https://learn.microsoft.com/en-us/dotnet/api/system.datetime.tryparseexact) and [custom date/time format strings](https://learn.microsoft.com/en-us/dotnet/standard/base-types/custom-date-and-time-format-strings).
