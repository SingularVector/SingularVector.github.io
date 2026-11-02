---
title: "PowerShell break statement"
excerpt: "An introduction to break statement in PowerShell and its usage"
categories:
  - PowerShell
tags:
  - PowerShell
  - PowerShell Basics
  - PowerShell Core
  - Loops
  - Break
  - Switch
last_modified_at: 2026-11-02
---

`break` stops an enclosing loop or `switch`. It does not mean “skip this user” or “finish this function,” so its placement matters in an automation script.

## Stop a loop

```powershell
$users = @('user1', 'user2', 'user3')
foreach ($user in $users) {
    if ($user -eq 'user2') {
        break
    }
    "Processing $user"
}
'After the loop'
# Processing user1
# After the loop
```

The loop stops before processing `user2`; `user3` is never visited. Execution then reaches the statement after the loop. The earlier article defined `$usersList` but iterated `$userList`, which made the example misleading.

Use `continue` when you want to skip one iteration and still visit later users. Use `return` when you want to leave the current function or scriptblock; see [return and continue]({% post_url 2019-01-02-PowerShell-Return-Continue-Explained %}).

## Nested loops

Without a label, `break` targets the innermost supporting construct. To leave an outer loop deliberately:

```powershell
:outer foreach ($server in @('server1', 'server2')) {
    foreach ($check in @('disk', 'service')) {
        "$server/$check"
        if ($check -eq 'service') {
            break outer
        }
    }
}
# server1/disk
# server1/service
```

The label makes the intended boundary visible. Avoid using labels to jump across distant functions; structured return values usually make that flow easier to follow.

## Stop a switch

A PowerShell `switch` can execute more than one matching clause. With overlapping wildcard patterns, `break` stops the entire switch after the selected action:

```powershell
$company = 'Sample Company LLC'
switch -Wildcard ($company) {
    'Sample Company*' { 'Specific company rule'; break }
    'Sample*' { 'General sample rule'; break }
    default { 'No rule' }
}
# Specific company rule
```

Without the first `break`, both patterns match. If the switch receives an array, `break` also prevents later input elements from being processed. The [switch article]({% post_url 2020-07-30-PowerShell-Switch-Statement %}) contrasts that with `continue`, which advances to the next input element.

## A pipeline is not a foreach statement

`ForEach-Object` invokes scriptblocks; it is not the same construct as the language's `foreach` loop. Do not put `break` in its body expecting a general-purpose “skip this object.” Outside a supporting construct, PowerShell can look up the call stack and affect a caller's loop or terminate a pipeline/runspace.

Choose the construct deliberately. For per-item pipeline filtering, use `Where-Object` or a clear conditional in the process block; for early termination of an explicit loop, use `foreach` and `break`.

Reference: [about_Break](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_break).
