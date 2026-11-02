---
title: "Exchange Online Management Module - Could not use the certificate for signing"
excerpt: "When trying to establish a connection to Exchange Online Could not use the certificate for signing error message is displayed."
categories:
  - PowerShell
  - Exchange
  - Office 365

tags:
  - PowerShell
  - Office365
  - Exchange

toc: true
last_modified_at: 2026-11-02
---

## The original failure

While updating mailbox automation in 2022, I deployed a new certificate to a test environment. Connecting to Exchange Online failed with:

```text
Could not use the certificate for signing. See inner exception for details.
Invalid provider type specified.
```

The same certificate worked in my PowerShell 7 test. That was a useful diagnostic observation, but it does not mean changing PowerShell versions fixes every certificate-provider problem.

## CNG and RSA describe different things

The original article described this as converting “CNG to RSA.” That was inaccurate: **RSA is a key algorithm; CNG and CSP refer to Windows cryptographic provider models**. An RSA key can be associated with a CNG provider.

Microsoft's current [Exchange Online app-only procedure](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2) specifies that CNG certificates are unsupported for that flow and describes CSP certificate creation. Follow those requirements along with the documented module and PowerShell prerequisites.

## Diagnose before exporting a private key

Check the full inner exception, then verify:

- The certificate meets the target authentication flow's key/provider requirements.
- The execution identity can access its private key. A certificate in an administrator's personal store is not automatically available to a scheduled task or service account.
- The app registration contains the matching public certificate and it is within its validity period.
- The connection method matches the host. `-CertificateThumbprint` is Windows-only; certificate-object and file options have their own requirements.

For an unsupported provider, request or create a certificate using the documented provider and your organisation's certificate policy, then deploy it to the actual automation identity. Test the new credential before removing the old registration or key material, so that you have a controlled rollback path.

## Why the old OpenSSL commands were removed

Re-encoding or exporting an RSA private key does not itself guarantee a compatible Windows provider association on import. The previous sequence also wrote an unencrypted intermediate private key with `openssl rsa`, despite describing the local workflow as safe.

I have removed that sequence rather than presenting it as a current deployment recipe. If a migration genuinely requires private-key export, use an approved, encrypted handling process and validate the resulting provider on the destination host. Do not export keys simply to work around an error that could instead be an account-permission or certificate-selection problem.

This preserves the lesson from the original incident: inspect the key provider and execution context, not just whether a PFX can be opened on your own machine.
