---
title: "The underlying connection was closed - An unexpected error occurred"
excerpt: "When using PowerShell Invoke-RestMethod you get the Invoke-RestMethod : The underlying connection was closed: An unexpected error occurred Error message"
last_modified_at: 2026-11-02
categories:
  - PowerShell
  - HowTo
tags:
  - PowerShell
  - TLS
  - Invoke-RestMethod
  - PowerShell TLS 1.0
  - PowerShell TLS 1.2
---

## Diagnose the connection failure first

`Invoke-RestMethod : The underlying connection was closed: An unexpected error occurred on a send` does not uniquely identify a TLS version problem. Check the inner exception, endpoint availability, certificate chain, proxy and the PowerShell/.NET version before changing protocol settings.

The original workaround addressed older **Windows PowerShell / .NET Framework** clients negotiating a protocol the server no longer accepted. The claim that PowerShell always defaults to TLS 1.0 is not correct for modern environments.

## Windows PowerShell 5.1

For a confirmed TLS 1.2 negotiation issue, a scoped workaround is:

```powershell
$previousProtocol = [Net.ServicePointManager]::SecurityProtocol
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-RestMethod -Uri 'https://api.example.com/resource' -ErrorAction Stop
}
finally {
    [Net.ServicePointManager]::SecurityProtocol = $previousProtocol
}
```

Replace the placeholder URI with your endpoint. The setting affects applicable .NET Framework requests in the process, not just one command. Restoring it limits the duration of the change, but concurrent requests can still be affected. Prefer correcting the supported OS/.NET configuration for a lasting fix.

## PowerShell 7

Normally allow the operating system to negotiate secure protocols. For a targeted TLS 1.2 test, PowerShell 7 web cmdlets expose a request option:

```powershell
Invoke-RestMethod -Uri 'https://api.example.com/resource' -SslProtocol Tls12
```

Do not add TLS 1.1 as a fallback or disable certificate validation to silence the error. A failed request after selecting TLS 1.2 needs further diagnosis; it does not prove the endpoint needs a weaker protocol.

References: [.NET Framework TLS best practices](https://learn.microsoft.com/en-us/dotnet/framework/network-programming/tls) and [Invoke-RestMethod](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod).
