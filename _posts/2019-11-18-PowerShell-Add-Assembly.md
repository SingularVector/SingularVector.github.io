---
title: "PowerShell load .Net Assembly"
excerpt: "How to load external assemblies in PowerShell to extend functionality and leverage functionalities not available in PowerShell."
toc: true
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - PowerShell Assemblies
  - PowerShell Tips
  - PowerShell Core
last_modified_at: 2026-11-02
---

Loading a .NET assembly makes its public types available to a PowerShell session. I used this in my [PowerScp module](https://github.com/SingularVector/PowerScp), which wraps WinSCP's .NET API.

The first question is compatibility: Windows PowerShell 5.1 uses .NET Framework, while PowerShell 7 uses modern .NET. Choose the library build intended for your runtime and check its platform and dependency requirements. Loading a DLL successfully does not prove its network operations will work on that host.

## Load a DLL from disk

For a managed assembly shipped with a script or module, `Add-Type` is usually the most direct approach:

```powershell
$assemblyPath = 'C:\Assemblies\WinSCPnet.dll'
Add-Type -Path $assemblyPath -ErrorAction Stop
$session = [WinSCP.Session]::new()
try {
    # Configure and use the session here.
}
finally {
    $session.Dispose()
}
```

Use a path resolved relative to your module's installation directory in a distributable module, rather than assuming every host has `C:\Assemblies`. For WinSCP specifically, deploy the matching `WinSCP.exe` as well as the assembly and choose the runtime-appropriate DLL; see the [vendor's installation instructions](https://winscp.net/eng/docs/library_install) and [PowerShell examples](https://winscp.net/eng/docs/library_powershell). WinSCP's automation dependencies target Windows, even when called from PowerShell 7.

## Reflection loading

The .NET reflection API is another available loading mechanism:

```powershell
$assemblyPath = 'C:\Assemblies\WinSCPnet.dll'
$assembly = [System.Reflection.Assembly]::LoadFrom($assemblyPath)
$assembly.FullName
```

This is not a method that `Add-Type` universally replaced. The APIs have different loading and dependency-resolution details. Prefer the library's documented loading method rather than switching between them to suppress an error.

## Byte arrays and Base64

It is also possible to load a managed assembly from bytes. Base64 is a textual representation of those bytes, useful for illustrating the round trip:

```powershell
$assemblyPath = 'C:\Assemblies\WinSCPnet.dll'
[byte[]]$assemblyBytes = [System.IO.File]::ReadAllBytes($assemblyPath)
[string]$assemblyString = [Convert]::ToBase64String($assemblyBytes)

[byte[]]$decodedBytes = [Convert]::FromBase64String($assemblyString)
$assembly = [System.Reflection.Assembly]::Load($decodedBytes)
```

The array type is **`[byte[]]`**, not `[byte]`; the latter holds one byte and was an error in the original examples. The Base64 text is encoding, not encryption, and makes the payload larger.

Loading from bytes avoids asking the loader to load that assembly from its original file path. It does not package dependent DLLs, native libraries, configuration files or external executables. For example, embedding `WinSCPnet.dll` does not remove WinSCP's executable dependency. Byte loading also changes assembly-location and dependency-resolution behaviour, so test more than whether a type can be constructed.

For maintainable distribution, shipping a versioned library alongside the module is normally easier to inspect and update than pasting a large encoded DLL into the source. Keep licence and provenance information with any redistributed dependencies.

## Updating a loaded library

Do not assume that deleting, replacing or reloading a DLL replaces types already loaded into a running process. File-lock behaviour depends on the runtime and loading method. When testing a library update, a fresh PowerShell process gives a clear starting point.

References: [Add-Type](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type) and [Assembly.Load](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.load).
