---
title: "PowerShell export registry key"
excerpt: "In this post we will explore how we can use PowerShell to check existence of a specific registry key and how to export them either in CSV or XML format"
categories:
  - PowerShell
tags:
  - PowerShell
  - Code Snippets
  - Useful functions

header:
    teaser: "/assets/images/export-registry-key/WindowsRegistry.png"
last_modified_at: 2026-11-02
---

The Windows registry featured in some of the old NT4 exams, and I still have the book to prove it. Some troubleshooting traditions are hard to retire.

![MCSE Windows NT](/assets/images/export-registry-key/WindowsNTBook.jpg)

In the original automation for maintaining an internal Windows CA, I needed to export registry data. There are two different goals: a native `.reg` export that Windows can import, and a structured report for inspection.

## Native .reg export

The built-in command is **`reg.exe export`**, not a separate executable named `regexport`. From PowerShell on Windows:

```powershell
$destination = Join-Path $env:TEMP 'Example-key.reg'
$reg = Get-Command reg.exe -ErrorAction Stop
& $reg.Source export 'HKCU\Software\Example' $destination
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "Registry export failed with exit code $exitCode."
}
```

Replace the example key with the local key you need, and run as an identity with read access. The destination directory must exist. Omit `/y` if you want the tool's overwrite prompt; add it only when replacing an existing export is intended.

The native command uses `HKCU\...`, while PowerShell's Registry provider paths use `HKCU:\...`. The original snippet also had an unclosed `Invoke-Command` scriptblock; no remoting wrapper is needed for this local export.

`reg export` returns 0 on success and 1 on failure. Do not report success just because the external process started. Under a native-command error policy that already turns a nonzero exit into an error, allow that failure to propagate as well.

## What a .reg file does not capture

A `.reg` export is not a full-system or application-consistent backup. In particular, do not treat it as a backup of registry security descriptors or assume that importing it removes values created after the export. Plan and test restoration according to the application or service being protected; a CA recovery plan needs more than selected registry values.

## XML and CSV reports

My earlier [Export-Registry helper](https://github.com/SingularVector/PowerShell-Functions) provided XML and CSV views of registry data. That can be useful for comparisons and reporting, but these are **not interchangeable with a native `.reg` backup**.

The historical helper also depended on `Test-IsRegistryKey`. Review the version and dependencies before adopting it. Omitting binary values with its `NoBinaryData` option makes the result intentionally incomplete; use that for reporting, not for a restore claim.

For a report, decide whether you need the root key, descendants, value names, value kinds and the 32-bit or 64-bit registry view. `HKCU` refers to the account running the job, which may differ from the person at the desktop. Those details matter more than whether the output filename ends in `.xml` or `.csv`.

Registry data can include application credentials or tokens. The earlier sample included a token-looking value; it has been removed rather than reproduced as example data. Protect real exports according to what they contain.

If you're wondering: yes, I used that NT4 book to prepare for the exam. I also have one dedicated to the registry—relics of an era when you could not simply Google the answer.

Reference: [reg export](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-export).
