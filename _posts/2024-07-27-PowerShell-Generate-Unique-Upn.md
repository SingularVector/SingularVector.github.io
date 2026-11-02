---
title: "PowerShell - Generate Unique UPN"
excerpt: "Generate UPN candidates with configurable name formats, LDAP filter escaping and explicit limits on directory scope and concurrent provisioning."
categories:
  - PowerShell
  - Howto

tags:
  - PowerShell
  - Tips
  - HowTo

toc: true
last_modified_at: 2026-11-02
---

## Scope and corrections

These Windows ADSI examples **propose a candidate UPN** by checking directory data at query time. They do not reserve the value: two concurrent provisioning jobs can select the same candidate, and replication delay can affect the result. Handle conflicts when creating the account rather than treating a successful lookup as an atomic uniqueness guarantee.

With no `-AdServer`, the lookup uses a Global Catalog. Supplying `-AdServer` uses the original `LDAP://` path and can restrict the query to that server's domain context; it must not be described as a guaranteed forest-wide search. Validate scope and access in the intended forest before deployment. A lookup failure propagates as an error and must not be converted into “UPN is free.”

The examples below correct the first-name default, independent surname formatting, the `-AdServer` call and LDAP filter escaping. They retain the original name-composition rules; organisation-specific rules for punctuation, accents and allowed suffixes belong in the provisioning policy.

## Generating Unique User Principal Names (UPNs) in PowerShell

When managing Active Directory (AD) environments, creating unique User Principal Names (UPNs) is a common, and challenging!, task.

This blog post covers two PowerShell functions that help find an unused UPN candidate: **Test-UPNExist** and **Get-UniqueUPN**. These functions can be particularly useful for automating user creation processes and can be integrated into your automation projects and solutions.

**Note** Both cmdlets are still under active development so do expect some changes, as I progress with development I will update the post. Feel free to report any issue, idea or suggestion so that I can integrate it into the final cmdlet version.

### Function 1: Test-UPNExist

This is a support function that is used to check if given UPN already exists in the AD environment.

```powershell
function Test-UPNExist
{
<#
    .SYNOPSIS
        Cmdlet will check if a given UPN exists in the forest.
    
    .DESCRIPTION
        Cmdlet is a diagnostic tool to check if a given UPN is already assigned to a user in the forest.
    
    .PARAMETER UPN
        A string representing the UPN to check for uniqueness.
    
    .PARAMETER AdServer
        A string representing the name of the domain controller to be used for the check, if parameter
        is not specified the closest Global Catalog is used.
    
    .EXAMPLE
        PS C:\> Test-UPNExist -UPN 'John.Doe@example.com'
#>
    
    [CmdletBinding()]
    param
    (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$UPN,
        [ValidateNotNullOrEmpty()]
        [string]$AdServer
    )
    
    if ([string]::IsNullOrEmpty($AdServer) -eq $true)
    {
        $adForest = [System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest()
        $globalCatalog = $null
        try
        {
            $globalCatalog = $adForest.FindGlobalCatalog()
            [string]$ldapPath = 'GC://{0}' -f $globalCatalog.Name
        }
        finally
        {
            if ($null -ne $globalCatalog) { $globalCatalog.Dispose() }
            $adForest.Dispose()
        }
    }
    else
    {
        [string]$ldapPath = '{0}{1}' -f 'LDAP://', $AdServer
    }
    
    # Escape an attribute value for the LDAP filter context.
    $escapedUpn = $UPN.Replace('\', '\5c').Replace('*', '\2a').Replace('(', '\28').Replace(')', '\29').Replace([string][char]0, '\00')
    $adDomain = $null
    $adSearcher = $null
    try
    {
        $adDomain = [System.DirectoryServices.DirectoryEntry]::new($ldapPath)
        $adSearcher = [System.DirectoryServices.DirectorySearcher]::new($adDomain)
        $adSearcher.SearchScope = 'Subtree'
        $adSearcher.Filter = "(&(objectCategory=person)(objectClass=user)(userPrincipalName=$escapedUpn))"
        [void]$adSearcher.PropertiesToLoad.Add('userPrincipalName')
        $searchResult = $adSearcher.FindOne()
        return $null -ne $searchResult
    }
    finally
    {
        if ($null -ne $adSearcher) { $adSearcher.Dispose() }
        if ($null -ne $adDomain) { $adDomain.Dispose() }
    }
}
```

Here's a summary explanation of the parameters:

- **Parameters**
  - *$UPN* - A string representing the UPN to check
  - *$AdServer* -  A string representing the name of the  LDAP server to query. Parameter is optional and if omitted function will automatically select the closest global catalog server
  
Here's an example usage:

```powershell
$upnExists = Test-UPNExist -UPN "john.doe@example.com"

if ($upnExists -eq $true) # Redundant I know but I like to make code redeable :-)
{
    Write-Host "The UPN exists."
} 
else 
{
    Write-Host "The UPN does not exist."
}

```

### Function 2: Get-UniqueUPN

This function generates a unique UPN based on given name components and checks the configured directory scope for an existing value.

```powershell
function Get-UniqueUPN
{
<#
    .SYNOPSIS
        Cmdlet will generate a forest wide unique UPN.
    
    .DESCRIPTION
        Cmdlet will generate a forest wide unique UPN according to generation rules
        defined by the user.
        
        Cmdlet accept different types of objects to generate the UPN to allow greater flexibility
        
        ADObject - For example and object from Get-AdUser cmdlet
        Strings - Representing First Name, Last Name etc.
        DirectoryService Objects - For example when using native .Net methods to retrieve the identity
    
    .PARAMETER ADObject
        An ADObject for example output of the Get-ADUser cmdlet
    
    .PARAMETER FirstName
        A string representing the First Name of the user
    
    .PARAMETER LastName
        A string representing the Last Name of the user
    
    .PARAMETER MiddleName
        A string representing the Middle Name of the user, parameter is optional.
    
    .PARAMETER UPNSuffix
        A string representing the UPN suffix to be used.
    
    .PARAMETER FirstNameFormat
        A string representing the format to be for the First Name part of the UPN.
    
    .PARAMETER LastNameFormat
        A string representing the format to be for the Last Name part of the UPN.
    
    .PARAMETER IncludeMiddleName
        When paramenter is specified user Middle Name, if present, will be included in the UPN generation process.
    
    .PARAMETER ADServer
        A string representing the name of the AD Domain Controller that will be used to query Active Directory.
    
        If no server is specified the closest Global Catalog will be automatically selected.
    
    .PARAMETER Separator
        A string representing the separator to be used between UPN parts, defaults to a '.'.
#>
    
    [CmdletBinding(DefaultParameterSetName = 'Strings')]
    param
    (
        [Parameter(ParameterSetName = 'ADObject',
                   Mandatory = $true)]
        [object]$ADObject,
        [Parameter(ParameterSetName = 'Strings',
                   Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$FirstName,
        [Parameter(ParameterSetName = 'Strings',
                   Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$LastName,
        [Parameter(ParameterSetName = 'Strings')]
        [ValidateNotNullOrEmpty()]
        [string]$MiddleName,
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$UPNSuffix,
        [ValidateSet('FullName', 'FirstLetter', IgnoreCase = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$FirstNameFormat = 'FullName',
        [ValidateSet('FullName', 'FirstLetter', IgnoreCase = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$LastNameFormat = 'FullName',
        [switch]$IncludeMiddleName,
        [ValidateNotNullOrEmpty()]
        [string]$ADServer,
        [ValidateNotNullOrEmpty()]
        [string]$Separator = '.'
    )
    
    if ($PSCmdlet.ParameterSetName -eq 'ADObject')
    {
        switch ($ADObject.GetType().FullName)
        {
            'Microsoft.ActiveDirectory.Management.ADUser'
            {
                [string]$firstName = $ADObject.GivenName
                [string]$lastName = $ADObject.Surname
                [string]$middleName = $ADObject.MiddleName
                
                break
            }
            'System.DirectoryServices.DirectoryEntry'
            {
                [string]$firstName = $ADObject.Properties['givenName'][0]
                [string]$lastName = $ADObject.Properties['sn'][0]
                [string]$middleName = $ADObject.Properties['middleName'][0]
                
                break
            }
            'System.DirectoryServices.SearchResult'
            {
                [string]$firstName = $ADObject.Properties['givenName'][0]
                [string]$lastName = $ADObject.Properties['sn'][0]
                [string]$middleName = $ADObject.Properties['middleName'][0]
                
                break
            }
            default
            {
                throw "Unsupported AD object type: $($ADObject.GetType().FullName)"
            }
        }
    }
    else
    {
        [string]$firstName = $FirstName
        [string]$lastName = $LastName
        [string]$middleName = $MiddleName
    }
    
    if ([string]::IsNullOrWhiteSpace($firstName) -or [string]::IsNullOrWhiteSpace($lastName))
    {
        throw 'The input must contain both a first name and a last name.'
    }

    # Format first name
    $firstName = switch ($FirstNameFormat)
    {
        'FullName'
        {
            $firstName
        }
        'FirstLetter'
        {
            $firstName.Substring(0, 1)
        }
    }
    
    # Format last name
    $LastName = switch ($LastNameFormat)
    {
        'FullName'
        {
            $LastName
        }
        'FirstLetter'
        {
            $LastName.Substring(0, 1)
        }
    }
    
    # Use middle name
    [string]$middleNamePart = if ($IncludeMiddleName -and $MiddleName)
    {
        '{0}{1}' -f $Separator, $MiddleName
    }
    
    # Setup required attributes
    [string]$baseUPN = ('{0}{1}{2}{3}@{4}' -f $FirstName, $middleNamePart, $Separator, $LastName, $UPNSuffix).ToLowerInvariant()
    [string]$uniqueUPN = $baseUPN
    [int]$counter = 1
    
    while (Test-UPNExist -UPN $uniqueUPN -AdServer $ADServer)
    {
        $uniqueUPN = '{0}{1}@{2}' -f ($baseUPN.Split('@')[0]), $counter, $UPNSuffix
        
        $counter++
    }
    
    return $uniqueUPN
}
```

Here's a summary explanation of the parameters:

- **Parameters**
  - *$ADObject* - We can pass an existing AD object to the function, for example output from the *Get-AdUser* cmdlet
  - *$FirstName* - A string representing the *First Name* of a given user
  - *$LastName* - A string representing the *Last Name* of a given user
  - *MiddleName* - A string representing the *Middle Name* of a given user (of course optional)
  - *$UPNSuffix* - A string representing the domain suffix for the UPN
  - *FirstNameFormat* - The format of the first name in the UPN (`FullName` or `FirstLetter`)
  - *IncludeMiddleName* - Switch parameter indicating to cmdlet if Middle Name should be used or not in the UPN generation
  - *$AdServer* - A string representing the name of the  LDAP server to query. Parameter is optional and if omitted function will automatically select the closest global catalog server
  - *$Separator* - The separator to use between the name parts. If not specified a '.' (dot) is used

Below you can find couple examples of functions at work

```powershell
# Using string parameters
$uniqueUPN = Get-UniqueUPN -FirstName "John" -LastName "Doe" -UPNSuffix "example.com" -FirstNameFormat "FirstLetter" -IncludeMiddleName -MiddleName "A"

Write-Host "Generated UPN: $uniqueUPN"

# Using an AD object
$adUser = Get-ADUser -Identity "johndoe"
$uniqueUPN = Get-UniqueUPN -ADObject $adUser -UPNSuffix "example.com"

Write-Host "Generated UPN: $uniqueUPN"
```

## Conclusion

By using **Test-UPNExist** and **Get-UniqueUPN**, you can automate the process of generating unique UPNs for users in your Active Directory environment.

These functions apply the selected name format and check for an existing value in the configured search scope. They are a starting point for provisioning, with creation-time conflict handling still required.

This approach minimizes the risk of conflicts and simplifies user management.

As mentioned both functions are still under development and I need to cleanup code and optimize some parts of it but the core functionality is there.

As usual all the code is available on my [GitHub repository](https://github.com/SingularVector/PowerShell-Functions).

I would love to receive feedback, ideas or implementation ideas for them!
