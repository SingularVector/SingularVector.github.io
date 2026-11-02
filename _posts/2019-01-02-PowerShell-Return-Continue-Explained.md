---
title: "PowerShell Return and Continue - Explained"
excerpt: "An introduction to PowerShell statements. In this post we will explore Return and Continue"
categories:
  - PowerShell
  - Post Series - Statements
tags:
  - PowerShell
  - PowerShell Basics
  - PowerShell Core
  - Loops
  - PowerShell Return
  - PowerShell Continue
last_modified_at: 2026-11-02
---

[The break article]({% post_url 2018-12-31-PowerShell-Break-Explained %}) shows how to stop a loop. `continue` and `return` cross different boundaries: an iteration and the current function, script or scriptblock.

## Continue with the next iteration

```powershell
foreach ($number in 1..5) {
    if ($number -eq 3) {
        continue
    }
    $number
}
# 1, 2, 4, 5
```

Only the rest of the current iteration is skipped. In a `while` loop, update the state that advances the loop before a `continue` can bypass it; otherwise you can accidentally repeat the same item indefinitely.

Within a `switch`, `continue` skips remaining clauses for the current input and advances to the next input. See [switch examples]({% post_url 2020-07-30-PowerShell-Switch-Statement %}).

## Return from a function

```powershell
function Find-FirstEven {
    param ([int[]]$Numbers)
    foreach ($number in $Numbers) {
        if ($number % 2 -eq 0) {
            return $number
        }
    }
}
Find-FirstEven -Numbers 1, 3, 4, 6
# 4
```

The return leaves the function, not just the loop. The final value 6 is never examined. If no even number is found, this function emits no success-stream output; the caller must decide how to represent that outcome.

## Output is not restricted to return

In ordinary PowerShell functions, any unassigned success-stream result is output. `return` does not discard values already emitted:

```powershell
function Get-DemoResult {
    'first'
    return 'second'
}
$result = @(Get-DemoResult)
$result.Count
# 2
```

An accidental debug string or an unsuppressed `.Add()` return value can therefore become part of a function's result. Use `Write-Verbose` for diagnostics, and suppress method results you do not intend to return. PowerShell class methods have different return rules; the example above describes ordinary functions.

## Returning from a pipeline process block

Here `return` ends the scriptblock invocation for the current object; it does not prevent later objects from reaching `ForEach-Object`:

```powershell
1..3 | ForEach-Object {
    if ($_ -eq 2) { return }
    $_
}
# 1, 3
```

This is a different boundary from the function in the previous example. Avoid substituting `break` or `continue` into arbitrary pipeline callbacks; they can affect an enclosing construct or runspace instead of behaving as a per-item skip.

## Exit is an entry-point decision

`exit` is intended for ending a script or session and can set a process exit code, depending on how the script is invoked. It is not a substitute for returning data from a reusable function. Let a function return a result or throw an error, then let the script entry point decide the job's exit status.

To observe an exit code without closing your current shell, start a separate PowerShell 7 process:

```powershell
pwsh -NoProfile -Command 'exit 7'
$LASTEXITCODE
# 7
```

This example requires `pwsh` on PATH. Native-exit-code error preferences in recent PowerShell versions can affect how a nonzero code is reported; see [error handling]({% post_url 2019-01-03-PowerShell-Error-Handling %}).

Reference: [about_Return](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_return) and [about_Continue](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_continue).
