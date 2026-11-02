function Get-ReportChain {
    [CmdletBinding(DefaultParameterSetName = 'DistinguishedName')]
    [OutputType([psobject])]
    param (
        [Parameter(Mandatory, ParameterSetName = 'SamAccountName')]
        [ValidateNotNullOrEmpty()]
        [Alias('UserSam', 'SAM')]
        [string]$SamAccountName,

        [Parameter(Mandatory, ParameterSetName = 'UserPrincipalName')]
        [ValidateNotNullOrEmpty()]
        [Alias('UPN', 'UserUPN')]
        [string]$UserPrincipalName,

        [Parameter(Mandatory, ParameterSetName = 'DistinguishedName')]
        [ValidateNotNullOrEmpty()]
        [Alias('DN', 'DistinguishedName')]
        [string]$UserDN,

        [ValidateNotNullOrEmpty()]
        [string]$DomainController,

        [ValidateNotNullOrEmpty()]
        [string[]]$Properties = @(
            'SamAccountName', 'UserPrincipalName', 'Mail', 'Manager', 'DirectReports'
        )
    )

    function ConvertTo-ReportChainFilterValue {
        param ([Parameter(Mandatory)][string]$Value)
        $Value.Replace('\', '\5c').Replace('*', '\2a').Replace('(', '\28').Replace(')', '\29').Replace([string][char]0, '\00')
    }

    $query = @{ ErrorAction = 'Stop' }
    if ($PSBoundParameters.ContainsKey('DomainController')) {
        $query.Server = $DomainController
    }

    $manager = switch ($PSCmdlet.ParameterSetName) {
        'SamAccountName' {
            Get-ADUser @query -Identity $SamAccountName
        }
        'DistinguishedName' {
            Get-ADUser @query -Identity $UserDN
        }
        'UserPrincipalName' {
            $escapedUpn = ConvertTo-ReportChainFilterValue $UserPrincipalName
            $matches = @(Get-ADUser @query -LDAPFilter "(userPrincipalName=$escapedUpn)")
            if ($matches.Count -ne 1) {
                throw "Expected one user for UPN '$UserPrincipalName'; found $($matches.Count)."
            }
            $matches[0]
        }
    }

    if ($null -eq $manager -or [string]::IsNullOrWhiteSpace($manager.DistinguishedName)) {
        throw 'The manager lookup did not return a distinguished name.'
    }

    $escapedDn = ConvertTo-ReportChainFilterValue $manager.DistinguishedName
    $filter = "(manager:1.2.840.113556.1.4.1941:=$escapedDn)"
    Get-ADUser @query -LDAPFilter $filter -Properties $Properties |
        Select-Object -Property $Properties
}
