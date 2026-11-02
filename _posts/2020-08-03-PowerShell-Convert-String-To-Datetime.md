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
---

## Fun with time in PowerShell

PowerShell makes it very easy to *have fun* with dates and time which is really handy, for example, when creating logs timestamps or generating users expiration date in an AD environment.

```powershell
# Get current date and add 30 days
[datetime]$expirationDate = (Get-Date).AddDays(30)

# Output
Wednesday, September 2, 2020 4:45:19 PMM
```

As you can guess from the [strong typed variable](https://singularvector.github.io/powershell/coding%20habits/powershell%20best%20practice/PowerShell-Strongly-Typed-Variables/) *expirationDate* is a [datetime](https://docs.microsoft.com/en-us/dotnet/api/system.datetime?view=netframework-4.8) object and such it supports properties and methods one of which is *.ToString()* which will convert object to a string.

```powershell
# Get String from datetime
$expirationDate.ToString('MM/dd/yyyy')

09/02/2020

# Get date string in other formats
$expirationDate.ToString('dd.MM.yyyy')

# Swiss format
02.09.2020

$expirationDate.ToString('dd/MM/yyyy')

# Italian format
02/09/2020
```

## From date to string and back

Converting from *datetime* to a string is easy but what if we have a date in string format, for example coming from a SQL query or an AD attribute, and we need to convert it back to a datetime object to, say, perform comparison or calculations?

This is easily accomplished via the **ParseExact** method of the datetime object. Building from the previous example let's assume our date string is **02/09/2020**

```powershell
# Parse and convert string
$testConversion = [datetime]::ParseExact('02/09/2020', 'dd/MM/yyyy', $null)

$testConversion

Wednesday, September 2, 2020 12:00:00 AM

# Get type
PS C:\Users\dc.sys> $testConversion.GetType()

IsPublic IsSerial Name                                     BaseType
-------- -------- ----                                     --------
True     True     DateTime                                 System.ValueType
```

Note how the object has been converted to **DateTime** as expected. A common pitfall in the process is the *second* argument to the **ParseExact** method as the specified *date format* must match that of the input string.

**Note:** Both arguments can of course be variables as long as they're in the correct format and not **$null**
{: .notice--primary}

A neat feature of the **ParseExact** method is that you can even output another string with a different date format.

```powershell
# Parse input and output string in the desired format
[datetime]::parseexact($invoice, 'dd-MMM-yy', $null).ToString('yyyy-MM-dd')

# Output
2020-09-02
```
