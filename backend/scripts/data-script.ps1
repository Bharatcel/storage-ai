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

function Get-IPv4Address {
    [CmdletBinding()]
    param()

    try {
        $interfacename = (Get-NetAdapter | Where-Object { $_.Status -eq 'Up' -and $_.Name -notlike '*isatap*' } | Select-Object -First 1).name
        $ipv4Address = ((Get-NetIPAddress -AddressFamily IPv4) | where-object { $interfacename.contains($_.InterfaceAlias) }).IPAddress
        return $ipv4Address
    } catch {
        $errorMessage = "Error retrieving IPv4 address: $($_.Exception.Message)"
        Log-Error -errorMessage $errorMessage
        throw $errorMessage
    }
}

function Export-DriveFileDetails {
    [CmdletBinding()]
    param (
        [string]$outputFilePath,
        [int]$batchSize
    )

    try {
        # Get drive details once
        $driveDetails = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DeviceID -notin 'C:' -and $_.DriveType -ne 5 }
        $ipv4Address = Get-IPv4Address
        $computerName = $env:COMPUTERNAME

        foreach ($drive in $driveDetails) {
            $driveLetter = $drive.DeviceID
            $files = Get-ChildItem -LiteralPath $driveLetter -File -Recurse

            $batch = @()
            
            foreach ($file in $files) {
                try {
                    $owner = (Get-Acl $file.FullName).Owner

                    $metadata = [PSCustomObject]@{
                        'DriveLetter'  = $driveLetter
                        'FileName'     = $file.Name
                        'Path'         = $file.FullName
                        'FileType'     = $file.Extension
                        'FileSizeKB'   = '{0:N2}' -f ($file.Length / 1KB)
                        'CreatedTime'  = $file.CreationTime
                        'LastAccessed' = $file.LastAccessTime
                        'LastModified' = $file.LastWriteTime
                        'Owner'        = $owner
                        'IPV4Address'  = $ipv4Address
                        'Hostname'     = $computerName
                    }

                    $batch += $metadata

                    # Export metadata to CSV gradually when the batch size is reached
                    if ($batch.Count -ge $batchSize) {
                        $batch | Export-Csv -Path $outputFilePath -NoTypeInformation -Append -Force
                        $batch = @()  # Clear the batch to release memory
                    }
                } catch {
                    Write-Host "Error processing file: $($file.FullName) - $($_.Exception.Message)"
                }
            }

            # Export any remaining metadata in the batch to CSV
            if ($batch.Count -gt 0) {
                $batch | Export-Csv -Path $outputFilePath -NoTypeInformation -Append -Force
            }
        }

        # Perform garbage collection to release memory
        [System.GC]::Collect()
    } catch {
        $errorMessage = "Error retrieving drive details: $($_.Exception.Message)"
        Log-Error -errorMessage $errorMessage
        throw $errorMessage
    }
}

# Set the output file path
$outputFilePath = "C:\$($env:COMPUTERNAME)-$((Get-Date).ToString('yyyyMMdd-HHmm'))-DriveFileDetails.csv"

# Set the batch size
$batchSize = 1000

# Upload the drive file to blob
try {
    Export-DriveFileDetails -outputFilePath $outputFilePath -batchSize $batchSize
    Write-Host "Successfully retrieved details and saved results to CSV: $outputFilePath."
} catch {
    Log-Error -errorMessage $($_.Exception.Message)
}
