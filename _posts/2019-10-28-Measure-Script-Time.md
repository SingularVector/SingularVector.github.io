---
title: "PowerShell Measure Script execution time"
excerpt: "Learn how to measure execution time of PowerShell scripts and commands using different techniques and approaches"
last_modified_at: 2026-11-02
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Measure-Command
  - PowerShell Timer
  - PowerShell StopWatch
  - StopWatch how-to
  - PowerShell Execution Time
---

Measuring a script can help decide how often to schedule it or identify which phase deserves investigation. The important part is measuring the whole interval, not subtracting the millisecond component of two clock readings.

## Measure one block

```powershell
$executionTime = Measure-Command {
    $sum = 0
    foreach ($number in 1..10000) {
        $sum += $number
    }
}
$executionTime.TotalMilliseconds
```

`Measure-Command` executes the block and returns a `TimeSpan`. Its success-stream output is normally suppressed; the timing does not prove that the operation succeeded. Check failures and validate the result according to the workflow you are measuring.

The earlier `[timespam]` type name was a typo; the .NET type is `[TimeSpan]`.

## Components are not totals

```powershell
$example = [TimeSpan]::FromMilliseconds(1250)
$example.Milliseconds
# 250
$example.TotalMilliseconds
# 1250
```

The same distinction applies to `Seconds` versus `TotalSeconds`: a duration of 74 seconds has a seconds component of 14. Use totals when reporting elapsed time across component boundaries.

Subtracting `(Get-Date).Millisecond` values cannot measure a multi-second interval; that property ranges only from 0 to 999. The old example also subtracted end from start. Subtracting full `DateTime` values is a different operation, but the system clock can be adjusted, so a stopwatch is the better tool for elapsed intervals.

## Time a longer workflow

I tend to use .NET's stopwatch when I need control over where timing begins and ends:

```powershell
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    # Run the operation being measured here.
    $sum = 0
    foreach ($number in 1..10000) {
        $sum += $number
    }
}
finally {
    $stopwatch.Stop()
}

[pscustomobject]@{
    Result = $sum
    ElapsedMilliseconds = $stopwatch.Elapsed.TotalMilliseconds
}
```

Stopping it in `finally` also covers an error path; it does not handle or suppress that error. A stopwatch accumulates elapsed time until stopped. `Start()` resumes the accumulated measurement, `Reset()` clears and stops it, and `Restart()` clears it and starts a new interval.

## Make comparisons meaningful

Use the same inputs, check equivalent results and include setup or final conversion when that is part of the work being compared. A single run is a sample, not a stable performance guarantee. Warm-up, caching, network latency and host load can all matter.

Avoid repeatedly running a command with external side effects just to collect timings. Measure a representative lab operation or use an existing run's timing before repeating production work.

My [IT-ToolBox](https://github.com/SingularVector/IT-ToolBox) and [PowerShell Functions](https://github.com/SingularVector/PowerShell-Functions) repositories contain helpers I use around automation, but no extra function is needed for the timing examples here.

References: [Measure-Command](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-command), [Stopwatch](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.stopwatch) and [TimeSpan.TotalMilliseconds](https://learn.microsoft.com/en-us/dotnet/api/system.timespan.totalmilliseconds).
