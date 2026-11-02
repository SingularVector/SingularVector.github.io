---
title: "PowerShell Switch Statement"
excerpt: "In this post we will see uses of Switch statement in PowerShell, advantages it offers over if/else construct and how to use a switch with multiple conditions"
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - Performance Tips
last_modified_at: 2026-11-02
---

A chain of `if`/`elseif` conditions can get awkward when several inputs need named actions. `switch` is another way to express that decision, with an important difference: more than one clause can match.

## Match a value

```powershell
$weekDay = 0
$dayName = switch ($weekDay) {
    0 { 'Sunday' }
    1 { 'Monday' }
    2 { 'Tuesday' }
    3 { 'Wednesday' }
    4 { 'Thursday' }
    5 { 'Friday' }
    6 { 'Saturday' }
    default { throw "Unknown weekday value: $weekDay" }
}
$dayName
# Sunday
```

`default` runs when no clause matches an input. It is a useful place to reject an unsupported value rather than continuing with a stale `$dayName` from a previous operation.

String matching is case-insensitive by default. Use `-CaseSensitive` when case is part of the input contract. Literal switch comparisons convert values to strings, so do not treat them as a strict type-validation mechanism.

## Wildcards and regular expressions are different modes

```powershell
$logMessage = '[Error] - Exception reported'
$kind = switch -Wildcard ($logMessage) {
    '[[]Error]*' { 'Error'; break }
    '[[]Warning]*' { 'Warning'; break }
    default { 'Info' }
}
$kind
# Error
```

`[[]` matches a literal opening bracket in a wildcard pattern. Bare `[Error]` would describe a character set, not the literal word in brackets. The original wildcard section incorrectly used `-Regex`; changing only the patterns would not fix that mismatch.

The equivalent regular-expression patterns use regex escaping:

```powershell
$kind = switch -Regex ($logMessage) {
    '^\[Error\]' { 'Error'; break }
    '^\[Warning\]' { 'Warning'; break }
    default { 'Info' }
}
```

I use this kind of classification with log messages, including output from my logging tools. Select the mode that matches the pattern language you actually intend.

## Multiple matches

```powershell
switch ('sample') {
    'sample' { 'First action' }
    'SAMPLE' { 'Second action' }
}
# First action
# Second action
```

Both clauses match. This is not an `if`/`elseif` chain that automatically stops after the first successful condition. Add `break` when first-match behaviour is required, or order and combine the clauses deliberately when several actions should run.

## Arrays, continue and break

With an array as input, the switch visits each element. `$_` or `$PSItem` refers to the current element:

```powershell
$messages = @('Info: starting', 'Warning: slow', 'Error: failed', 'Info: finished')
switch -Wildcard ($messages) {
    'Warning:*' { "Warning handled: $_"; continue }
    'Error:*' { "Stopping: $_"; break }
    default { "Message: $_" }
}
# Message: Info: starting
# Warning handled: Warning: slow
# Stopping: Error: failed
```

`continue` advances to the next input, skipping remaining clauses for that item. `break` leaves the entire switch, so the final message is not processed. A repeated input value is processed each time it appears.

## Use predicates when the condition is not a literal match

```powershell
$age = 37
switch ($age) {
    { $_ -lt 0 } { throw 'Age cannot be negative.' }
    { $_ -ge 0 -and $_ -lt 18 } { 'Under 18' }
    { $_ -ge 18 } { 'Adult' }
}
# Adult
```

Each scriptblock is a condition evaluated against the current input. Overlapping predicates can execute multiple actions unless you stop processing explicitly.

Choose `switch` for readable dispatch or pattern matching, not because it is guaranteed to be faster. The original claim that every switch builds a lookup table was too broad: mode, conditions and workload affect performance. For a simple key/value mapping, a [hashtable]({% post_url 2019-01-06-PowerShell-HashTables %}) may express the intention more directly.

Reference: [about_Switch](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_switch).
