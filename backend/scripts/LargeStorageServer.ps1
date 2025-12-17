function Log-Error {
    param (
        [string]$errorMessage
    )
 
    try {
        $hostname = $env:COMPUTERNAME
        $dateTimeString = (Get-Date).ToString('yyyyMMdd-HHmm')
        $logFilePath = "C:\$hostname-$dateTimeString-DatadiscoveryerrorLog.txt"
        Write-Output "pathis: $logFilePath"
        $logEntry = "$dateTimeString - ERROR: $errorMessage"
        Add-Content -Path $logFilePath -Value $logEntry -ErrorAction Stop
        Write-Host "Error logged successfully: $errorMessage"
    } catch {
        Write-Host "Failed to log error: $($_.Exception.Message)"
    }
}

function Export-DriveFileDetails {
    [CmdletBinding()]
    param (
        [string]$outputFilePath
    )

    try {
        # Get drive details once
        $driveDetails = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DeviceID -notin 'C:','Z:' }

        foreach ($drive in $driveDetails) {
            $driveLetter = $drive.DeviceID
            $files = Get-ChildItem -Path $driveLetter -File -Recurse

            $files | ForEach-Object {
                [PSCustomObject]@{
                    'DriveLetter'  = $driveLetter
                    'FileName'     = $_.Name
                    'Path'         = $_.FullName
                    'FileType'     = $_.Extension
                    'FileSizeMB'   = '{0:N2} MB' -f ($_.Length / 1MB)
                    'CreatedTime'  = $_.CreationTime
                    'LastAccessed' = $_.LastAccessTime
                    'LastModified' = $_.LastWriteTime
                }
            } | Export-Csv -Path $outputFilePath -NoTypeInformation -Append -Force
        }
    } catch {
        $errorMessage = "Error retrieving drive details: $($_.Exception.Message)"
        Log-Error -errorMessage $errorMessage
        throw $errorMessage
    }
}

# Upload the drive file to blob
$ipv4Address = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like 'Ethernet*' }).IPAddress

try {
    $outputFilePath = "C:\$($env:COMPUTERNAME)-$($ipv4Address.Replace('.', '_'))-$((Get-Date).ToString('yyyyMMdd-HHmm'))-DriveFileDetails.csv"
    Export-DriveFileDetails -outputFilePath $outputFilePath
    Write-Host "Successfully retrieved details and saved results to CSV: $outputFilePath."
} catch {
    Log-Error -errorMessage $($_.Exception.Message)
}
