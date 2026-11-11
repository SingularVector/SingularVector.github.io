[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

try {
    $process = Get-Process -Id $PID
    $runtime = [pscustomobject]@{
        TimestampUtc      = [DateTime]::UtcNow.ToString('o')
        PSVersion         = $PSVersionTable.PSVersion.ToString()
        PSEdition         = $PSVersionTable.PSEdition
        Executable        = $process.Path
        PSHome            = $PSHOME
        Is64BitProcess    = [Environment]::Is64BitProcess
        Account           = [Environment]::UserName
        PowerShellLocation = (Get-Location).Path
        ProcessDirectory  = [Environment]::CurrentDirectory
        ModuleSearchPath  = $env:PSModulePath
    }

    $runtime | ConvertTo-Json -Depth 3 |
        Set-Content -LiteralPath $OutputPath -Encoding UTF8
}
catch {
    Write-Error -ErrorRecord $_ -ErrorAction Continue
    exit 1
}
