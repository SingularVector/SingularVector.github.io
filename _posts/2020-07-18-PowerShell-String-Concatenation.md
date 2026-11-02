---
title: "PowerShell string concatenation"
excerpt: "Concatenating strings in PowerShell is a common task in this short post I will give some tips to avoid the performance penalty associated with the task"
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Performance Tips
last_modified_at: 2026-11-02
---

Building an HTML notification often starts with a few strings and ends with a loop appending hundreds of rows. The operation is the same, but the amount of work changes which approach makes sense.

## Use interpolation for small messages

```powershell
$userName = 'Daniele'
$count = 3
$message = "Found $count items for $userName."
```

There is no need for a builder just to join a few known pieces. When the pieces already form a collection, `-join` expresses that directly:

```powershell
$lines = @('First line', 'Second line', 'Third line')
$text = $lines -join [Environment]::NewLine
```

Use the separator required by the receiving format. For example, a network protocol may specify CRLF rather than the platform's default newline.

## Repeated appends

.NET strings are immutable. Appending with `+=` assigns a new string value; a large loop can spend substantial time allocating and copying text. `StringBuilder` supports a buffer that can grow while you append:

```powershell
$builder = [System.Text.StringBuilder]::new()
[void]$builder.Append('Text1')
[void]$builder.Append('Text2')
$result = $builder.ToString()
# Text1Text2
```

`Append()` returns the builder itself. Suppress that method result when it is not intended as output from your script or function. `AppendLine()` also adds a newline, so it is not an identical replacement for `Append()`.

## Compare equivalent work

The original 2020 run measured about **15.2 seconds** for repeated `+=` and **239 milliseconds** for the builder. Those were observations from that environment, not a promised ratio on current PowerShell or another machine.

A smaller comparison you can run locally is:

```powershell
$iterations = 5000
$piece = 'Some text'

$appendTime = Measure-Command {
    $concatenated = ''
    for ($index = 0; $index -lt $iterations; $index++) {
        $concatenated += $piece
    }
}

$builderTime = Measure-Command {
    $builder = [System.Text.StringBuilder]::new()
    for ($index = 0; $index -lt $iterations; $index++) {
        [void]$builder.Append($piece)
    }
    $built = $builder.ToString()
}

if ($concatenated -cne $built) {
    throw 'The benchmark results differ.'
}
[pscustomobject]@{
    Iterations = $iterations
    Characters = $built.Length
    AppendMilliseconds = $appendTime.TotalMilliseconds
    BuilderMilliseconds = $builderTime.TotalMilliseconds
}
```

The comparison checks identical output and includes the final `ToString()` conversion. Timings still vary with runtime, warm-up, input size and the surrounding workload. Measure representative work before complicating a small string expression for performance alone.

For HTML notifications, joining or buffering text also does not encode inserted values. Escape dynamic content for the HTML context before adding it; that concern is separate from the concatenation method.

References: [StringBuilder](https://learn.microsoft.com/en-us/dotnet/api/system.text.stringbuilder) and [PowerShell performance considerations](https://learn.microsoft.com/en-us/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations).
