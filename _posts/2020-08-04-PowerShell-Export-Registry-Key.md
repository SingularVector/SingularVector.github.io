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
---

Window registry has been for many years the joy and pain of every Windows Systems Administrator and if memory does not fail me it was even part of some of the old NT4 exams (the sweet sting of nostalgia!).

![MCSE Windows NT](/assets/images/export-registry-key/WindowsNTBook.jpg)

Anyhow as I said at some point or another we all had to deal with the import/export/modification of a registry key on a Windows machine hence this post.

I am developing an automation solution to *maintain* an internal Windows CA Server and part of the requirement is exporting some registry keys.

## Method 1 - Regexport

Windows has a built-in utility called **[regexport](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/reg-export)** which was designed for the purpose of exporting registry key and can easily be called from within PowerShell with something like this

```powershell
Invoke-Command  {reg export 'HKLM\SOFTWARE\Microsoft\Office\ClickToRun\Configuration' C:\Temp\MyKeyNackup.reg
```

While this works generally speaking I am not a big fan of calling external executables from within PowerShell for a number of reasons, chief among all the pain to handle return values from the external exe.

## Method 2 - Export-Registry PowerShell function

Being confronted with this specific requirement/challenge I decided to come up with something *native*. Result is the *Export-Registry* function which allows export of key both in **XML** and **CSV** format. I've added the latter as I find it handy for reporting purposes.

You can find the full function code in my [GitHub function repository](https://github.com/SingularVector/PowerShell-Functions) but here's couple of examples.

```powershell
# Define registry keys to export
[array]$registryKey = @('HKCU:\SOFTWARE\Ditto\',
    'HKCU:\SOFTWARE\GOG.com\Galaxy'
)

# Export keys and remove any binary data
Export-Registry -KeyPath $registryKey -ExportFormat xml -ExportPath 'C:\Temp\TestExport.xml' -NoBinaryData
```

The above will check if the specified key exist via the **[Test-IsRegistryKey](https://github.com/SingularVector/PowerShell-Functions/blob/master/Test-IsRegistryKey.ps1)** helper function and once validated export the key in *XML* format.

Here's the sample export

```xml
Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCustomObject</T>
      <T>System.Object</T>
    </TN>
    <MS>
      <Obj N="Path" RefId="1">
        <TN RefId="1">
          <T>Microsoft.Win32.RegistryKey</T>
          <T>System.MarshalByRefObject</T>
          <T>System.Object</T>
        </TN>
        <ToString>HKEY_CURRENT_USER\SOFTWARE\GOG.com\Galaxy</ToString>
        <Props>
          <I32 N="SubKeyCount">1</I32>
          <Obj N="View" RefId="2">
            <TN RefId="2">
              <T>Microsoft.Win32.RegistryView</T>
              <T>System.Enum</T>
              <T>System.ValueType</T>
              <T>System.Object</T>
            </TN>
            <ToString>Default</ToString>
            <I32>0</I32>
          </Obj>
````

I have truncated the output for brevity but all the data in the registry will be converted and written to the specified XML file.

Here is an example of the same command just using the *CSV* export format

```csv
"Path","Name","Value","Type","Computername"
"HKEY_CURRENT_USER\SOFTWARE\GOG.com\Galaxy","refreshToken","0_LOM-vC5qCXAivsQ658dYGEmGRFVyZG-QGXB5BOWCXMvtIY4HYxhljzVjnp8y0D","String","WKS2K10"
```

**Note:** In order to for the **Export-Registry** function to work you will also need to import/download the **Test-IsRegistryKey** one as well.
{: .notice--danger}

While format is not the native *.reg* of regexport with this approach we can have a much easier and better error and exception handling.

Hopefully you will find this functions as useful as they've been for me!

## Final thoughts

If you're wondering yes, I am that old to own and have used that book to prepare for the NT4 MCSE Exam. I even have somewhere a book completely dedicated to NT4 registry.

Relics of an era when you could not simply *google* for an answer.
