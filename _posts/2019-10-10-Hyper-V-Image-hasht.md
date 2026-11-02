---
title: "The image hash and certificate are not allowed"
excerpt: "The image hash and certificate are not allowed error is displayed when creating a new Hyper-V machine"
last_modified_at: 2026-11-02
categories:

  - Windows
  - SysAdmin
  - PowerShell
  
tags:
  - HyperV
  - Virtualization
  - Tips
---

In my original lab setup, a generation 2 Hyper-V VM failed to boot a CentOS 7 ISO with **“The image's hash and certificate are not allowed.”** Secure Boot was enabled with the Windows template. The useful lesson is checking which boot-signing authority the VM trusts, rather than treating every failed ISO boot as a reason to disable Secure Boot.

CentOS 7 was the guest in that 2019 incident, not a current installation recommendation. Use supported installation media for the guest you plan to deploy.

## Check the VM and firmware

Run these commands on a Windows Hyper-V host with the module and permissions to inspect the VM. Replace the example name:

```powershell
$vmName = 'Linux-Lab'
Get-VM -Name $vmName -ErrorAction Stop |
    Select-Object Name, State, Generation
Get-VMFirmware -VMName $vmName -ErrorAction Stop |
    Select-Object VMName, SecureBoot, SecureBootTemplate, BootOrder
```

`Get-VMFirmware` targets generation 2 firmware. A generation 1 VM uses a different boot model, so this procedure does not apply to it.

## Select the appropriate Linux template

For supported Linux guests whose signed bootloader is trusted by the Microsoft UEFI Certificate Authority template, Microsoft's documented choice is that template instead of Microsoft Windows. Arrange a normal guest shutdown before changing firmware settings; the example checks that the VM is already off rather than turning it off for you:

```powershell
$vm = Get-VM -Name $vmName -ErrorAction Stop
if ($vm.Generation -ne 2 -or $vm.State -ne 'Off') {
    throw 'This example requires a powered-off generation 2 VM.'
}
Set-VMFirmware -VMName $vmName -EnableSecureBoot On `
    -SecureBootTemplate MicrosoftUEFICertificateAuthority -ErrorAction Stop
Get-VMFirmware -VMName $vmName -ErrorAction Stop |
    Select-Object SecureBoot, SecureBootTemplate
```

This changes firmware trust configuration; it does not start the VM. Check the distribution's current Hyper-V/Secure Boot support and keep the host updated. The template is not a guarantee that any ISO or bootloader will be accepted.

## If the image is still rejected

Verify the downloaded image against the publisher's checksum and confirm the guest architecture and generation. Review the bootloader's signing/revocation requirements and the host's Secure Boot updates; older media can remain unsuitable even with the expected template.

A later PXE attempt may simply mean the firmware tried the next boot entry after rejecting the ISO. It does not establish that a missing PXE server caused the original certificate error.

The original article ended by disabling Secure Boot if the VM still failed. That broad fallback has been removed: first establish why the image is rejected and choose a supported boot configuration for that guest.

Reference: Microsoft's [generation 2 VM security guidance](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/learn-more/Generation-2-virtual-machine-security-settings-for-Hyper-V).
