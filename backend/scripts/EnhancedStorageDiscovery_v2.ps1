# ===================================================================
# ENHANCED STORAGE DISCOVERY SCRIPT v2.0
# Collects comprehensive file, server, and performance metrics
# Author: Storage Assessment Team
# Version: 2.0
# Date: January 2026
# 
# NEW FEATURES:
# - 25 additional data points beyond v1.0
# - Server metadata collection
# - Drive-level statistics
# - Pre-calculated age buckets and tier recommendations
# - File attribute analysis (hidden, system, compressed)
# - Duplicate detection helpers
# - Security/ownership tracking
# - Performance indicators
# ===================================================================

function Log-Error {
    param ([string]$errorMessage)
    
    try {
        $hostname = $env:COMPUTERNAME
        $dateTimeString = (Get-Date).ToString('yyyyMMdd-HHmm')
        $logFilePath = "C:\$hostname-$dateTimeString-EnhancedDiscoveryErrorLog.txt"
        $logEntry = "$dateTimeString - ERROR: $errorMessage"
        Add-Content -Path $logFilePath -Value $logEntry -ErrorAction SilentlyContinue
        Write-Host "❌ Error logged: $errorMessage" -ForegroundColor Red
    } catch {
        Write-Host "Failed to log error: $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}

function Get-FileOwner {
    param ([string]$FilePath)
    
    try {
        $acl = Get-Acl -Path $FilePath -ErrorAction SilentlyContinue
        return $acl.Owner
    } catch {
        return "Unknown"
    }
}

function Get-DriveDetails {
    param ([string]$DriveLetter)
    
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='$DriveLetter'"
        
        $totalSize = if ($disk.Size) { $disk.Size } else { 0 }
        $freeSpace = if ($disk.FreeSpace) { $disk.FreeSpace } else { 0 }
        $usedSpace = $totalSize - $freeSpace
        $usedPercentage = if ($totalSize -gt 0) { ($usedSpace / $totalSize) * 100 } else { 0 }
        
        return @{
            TotalSizeGB     = [math]::Round($totalSize / 1GB, 2)
            FreeSpaceGB     = [math]::Round($freeSpace / 1GB, 2)
            UsedSpaceGB     = [math]::Round($usedSpace / 1GB, 2)
            UsedPercentage  = [math]::Round($usedPercentage, 2)
            FileSystem      = if ($disk.FileSystem) { $disk.FileSystem } else { "Unknown" }
            VolumeLabel     = if ($disk.VolumeName) { $disk.VolumeName } else { "Unlabeled" }
            DriveType       = switch ($disk.DriveType) {
                2 { "Removable" }
                3 { "Local Fixed Disk" }
                4 { "Network Drive" }
                5 { "CD-ROM" }
                default { "Unknown" }
            }
        }
    } catch {
        Log-Error "Failed to get drive details for $DriveLetter : $($_.Exception.Message)"
        return @{
            TotalSizeGB = 0; FreeSpaceGB = 0; UsedSpaceGB = 0
            UsedPercentage = 0; FileSystem = "Unknown"
            VolumeLabel = "Unknown"; DriveType = "Unknown"
        }
    }
}

function Get-ServerMetadata {
    try {
        $os = Get-WmiObject -Class Win32_OperatingSystem
        $cs = Get-WmiObject -Class Win32_ComputerSystem
        
        $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | 
                      Where-Object { $_.InterfaceAlias -notlike '*Loopback*' } | 
                      Select-Object -First 1).IPAddress
        
        if (-not $ipAddress) {
            $ipAddress = "Unknown"
        }
        
        return @{
            Hostname        = $env:COMPUTERNAME
            Domain          = if ($cs.Domain) { $cs.Domain } else { "WORKGROUP" }
            OSName          = $os.Caption
            OSVersion       = $os.Version
            TotalMemoryGB   = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
            CPUCores        = $cs.NumberOfLogicalProcessors
            IPAddress       = $ipAddress
        }
    } catch {
        Log-Error "Failed to retrieve server metadata: $($_.Exception.Message)"
        return @{
            Hostname = $env:COMPUTERNAME
            Domain = "Unknown"
            OSName = "Unknown"
            OSVersion = "Unknown"
            TotalMemoryGB = 0
            CPUCores = 0
            IPAddress = "Unknown"
        }
    }
}

function Export-EnhancedDriveFileDetails {
    param ([string]$outputFilePath)

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   ENHANCED STORAGE DISCOVERY v2.0                          ║" -ForegroundColor Cyan
    Write-Host "║   Comprehensive File & Server Metadata Collection         ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Get server metadata once (reuse for all files)
    Write-Host "📡 Collecting server information..." -ForegroundColor Yellow
    $serverInfo = Get-ServerMetadata
    $scanStartTime = Get-Date
    
    Write-Host "   Server: $($serverInfo.Hostname)" -ForegroundColor Gray
    Write-Host "   OS: $($serverInfo.OSName)" -ForegroundColor Gray
    Write-Host "   IP: $($serverInfo.IPAddress)" -ForegroundColor Gray
    Write-Host ""
    
    # Get drives (exclude C: and Z: by default - modify as needed)
    $driveDetails = Get-WmiObject Win32_LogicalDisk | 
                    Where-Object { $_.DeviceID -notin 'C:', 'Z:' }
    
    if ($driveDetails.Count -eq 0) {
        Write-Host " No drives found to scan (excluding C: and Z:)" -ForegroundColor Yellow
        Write-Host "   Modify the script to include other drives if needed." -ForegroundColor Gray
        return
    }
    
    $totalFiles = 0
    $totalSize = 0
    $totalDrives = $driveDetails.Count
    $currentDrive = 0
    
    foreach ($drive in $driveDetails) {
        $currentDrive++
        $driveLetter = $drive.DeviceID
        
        Write-Host "[$currentDrive/$totalDrives] Scanning drive $driveLetter..." -ForegroundColor Cyan
        
        # Get drive-level details
        $driveInfo = Get-DriveDetails -DriveLetter $driveLetter
        Write-Host "   Capacity: $($driveInfo.TotalSizeGB) GB | Used: $($driveInfo.UsedPercentage)% | Type: $($driveInfo.DriveType)" -ForegroundColor Gray
        
        try {
            # Get all files recursively
            $files = Get-ChildItem -Path $driveLetter -File -Recurse -ErrorAction SilentlyContinue
            
            $fileCount = 0
            foreach ($file in $files) {
                $fileCount++
                $totalFiles++
                $totalSize += $file.Length
                
                # Show progress every 1000 files
                if ($fileCount % 1000 -eq 0) {
                    Write-Host "   Processing... $fileCount files (Total: $totalFiles)" -ForegroundColor DarkGray
                }
                
                # ==================== AGE CALCULATION ====================
                $ageInDays = [int]((Get-Date) - $file.LastWriteTime).TotalDays
                $ageBucket = switch ($ageInDays) {
                    { $_ -lt 180 }  { "<6m" }
                    { $_ -lt 365 }  { "6m-1Y" }
                    { $_ -lt 1095 } { "1-3Y" }
                    { $_ -lt 1825 } { "3-5Y" }
                    default         { ">5Y" }
                }
                
                # ==================== TIER RECOMMENDATION ====================
                $daysSinceAccess = [int]((Get-Date) - $file.LastAccessTime).TotalDays
                $daysSinceModified = [int]((Get-Date) - $file.LastWriteTime).TotalDays
                
                $recommendedTier = switch ($daysSinceModified) {
                    { $_ -lt 30 }   { "Hot" }
                    { $_ -lt 180 }  { "Cool" }
                    { $_ -lt 1095 } { "Archive" }
                    default         { "Archive/Delete" }
                }
                
                # ==================== DUPLICATE DETECTION ====================
                $isDuplicateCandidate = $file.Name -match '(copy|backup|old|temp|\(\d+\)|\s-\sCopy)' -or
                                        $file.Name -match '~\$|\.tmp$|\.bak$|\.old$'
                
                # ==================== FILE ATTRIBUTES ====================
                $isReadOnly   = $file.IsReadOnly
                $isHidden     = ($file.Attributes -band [System.IO.FileAttributes]::Hidden) -ne 0
                $isSystem     = ($file.Attributes -band [System.IO.FileAttributes]::System) -ne 0
                $isCompressed = ($file.Attributes -band [System.IO.FileAttributes]::Compressed) -ne 0
                $isArchive    = ($file.Attributes -band [System.IO.FileAttributes]::Archive) -ne 0
                
                # ==================== CATEGORIZATION ====================
                $directoryPath = $file.DirectoryName
                $directoryDepth = ($directoryPath.Split('\').Count)
                
                $isLargeFile  = $file.Length -gt 100MB
                $isZombieFile = $daysSinceAccess -gt 730  # Not accessed in 2 years
                $isTempFile   = $directoryPath -match '(temp|tmp|cache)' -or $file.Name -match '\.(tmp|temp)$'
                $isBackupFile = $file.Name -match '\.(bak|backup)$' -or $file.Name -match '(backup|old)'
                
                # ==================== SECURITY (Expensive - Only for large files) ====================
                $fileOwner = if ($file.Length -gt 10MB) { 
                    Get-FileOwner -FilePath $file.FullName 
                } else { 
                    "NotCollected" 
                }
                
                # ==================== BUILD OUTPUT OBJECT ====================
                [PSCustomObject]@{
                    # --- SERVER METADATA ---
                    'ServerHostname'        = $serverInfo.Hostname
                    'ServerDomain'          = $serverInfo.Domain
                    'ServerOS'              = $serverInfo.OSName
                    'ServerIPAddress'       = $serverInfo.IPAddress
                    'ScanTimestamp'         = $scanStartTime.ToString('yyyy-MM-dd HH:mm:ss')
                    
                    # --- DRIVE METADATA ---
                    'DriveLetter'           = $driveLetter
                    'DriveType'             = $driveInfo.DriveType
                    'DriveTotalSizeGB'      = $driveInfo.TotalSizeGB
                    'DriveFreeSpaceGB'      = $driveInfo.FreeSpaceGB
                    'DriveUsedPercentage'   = $driveInfo.UsedPercentage
                    'DriveFileSystem'       = $driveInfo.FileSystem
                    'DriveVolumeLabel'      = $driveInfo.VolumeLabel
                    
                    # --- FILE IDENTIFICATION ---
                    'FileName'              = $file.Name
                    'FilePath'              = $file.FullName
                    'DirectoryPath'         = $directoryPath
                    'DirectoryDepth'        = $directoryDepth
                    'FileExtension'         = $file.Extension
                    
                    # --- FILE SIZE (Multiple Units) ---
                    'FileSizeBytes'         = $file.Length
                    'FileSizeKB'            = [math]::Round($file.Length / 1KB, 2)
                    'FileSizeMB'            = [math]::Round($file.Length / 1MB, 2)
                    'FileSizeGB'            = [math]::Round($file.Length / 1GB, 4)
                    
                    # --- FILE DATES ---
                    'CreatedTime'           = $file.CreationTime.ToString('MM/dd/yyyy hh:mm:ss tt')
                    'LastModified'          = $file.LastWriteTime.ToString('MM/dd/yyyy hh:mm:ss tt')
                    'LastAccessed'          = $file.LastAccessTime.ToString('MM/dd/yyyy hh:mm:ss tt')
                    
                    # --- ANALYSIS HELPERS (Pre-calculated for faster backend processing) ---
                    'AgeInDays'             = $ageInDays
                    'AgeBucket'             = $ageBucket
                    'DaysSinceLastAccess'   = $daysSinceAccess
                    'DaysSinceModified'     = $daysSinceModified
                    'RecommendedTier'       = $recommendedTier
                    
                    # --- FILE ATTRIBUTES ---
                    'IsReadOnly'            = $isReadOnly
                    'IsHidden'              = $isHidden
                    'IsSystem'              = $isSystem
                    'IsCompressed'          = $isCompressed
                    'IsArchive'             = $isArchive
                    
                    # --- DUPLICATE DETECTION ---
                    'IsDuplicateCandidate'  = $isDuplicateCandidate
                    
                    # --- SECURITY ---
                    'FileOwner'             = $fileOwner
                    
                    # --- CATEGORIZATION (Quick Filters) ---
                    'IsLargeFile'           = $isLargeFile
                    'IsZombieFile'          = $isZombieFile
                    'IsTempFile'            = $isTempFile
                    'IsBackupFile'          = $isBackupFile
                    
                } | Export-Csv -Path $outputFilePath -NoTypeInformation -Append -Force
            }
            
            Write-Host "    Completed $driveLetter - $fileCount files scanned" -ForegroundColor Green
            
        } catch {
            $errorMessage = "Error scanning drive $driveLetter : $($_.Exception.Message)"
            Log-Error -errorMessage $errorMessage
            Write-Host "    $errorMessage" -ForegroundColor Red
        }
    }
    
    # ==================== SUMMARY ====================
    $scanEndTime = Get-Date
    $duration = $scanEndTime - $scanStartTime
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   SCAN COMPLETED SUCCESSFULLY                              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host " Summary:" -ForegroundColor Cyan
    Write-Host "   Total Files Scanned: $totalFiles" -ForegroundColor White
    Write-Host "   Total Size: $([math]::Round($totalSize / 1GB, 2)) GB" -ForegroundColor White
    Write-Host "   Drives Scanned: $totalDrives" -ForegroundColor White
    Write-Host "   Duration: $($duration.Hours)h $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor White
    Write-Host ""
    Write-Host " Output File: $outputFilePath" -ForegroundColor Cyan
    Write-Host ""
}

# ===================================================================
# MAIN EXECUTION
# ===================================================================

try {
    $hostname = $env:COMPUTERNAME
    $ipv4Address = (Get-NetIPAddress -AddressFamily IPv4 | 
                    Where-Object { $_.InterfaceAlias -notlike '*Loopback*' } | 
                    Select-Object -First 1).IPAddress
    
    if (-not $ipv4Address) {
        $ipv4Address = "Unknown"
    }
    
    $timestamp = (Get-Date).ToString('yyyyMMdd-HHmm')
    $outputFilePath = "C:\$hostname-$($ipv4Address.Replace('.', '_'))-$timestamp-EnhancedStorageDiscovery.csv"
    
    # Display header
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " Enhanced Storage Discovery Script v2.0" -ForegroundColor White
    Write-Host " Copyright © 2026 - Storage Assessment Team" -ForegroundColor Gray
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    # Run discovery
    Export-EnhancedDriveFileDetails -outputFilePath $outputFilePath
    
    Write-Host " SUCCESS: Enhanced storage discovery completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Upload the CSV file to your Storage Assessment application" -ForegroundColor White
    Write-Host "2. Click 'Analyze' to process the enhanced data" -ForegroundColor White
    Write-Host "3. Review the comprehensive analysis dashboard" -ForegroundColor White
    Write-Host ""
    
} catch {
    $errorMsg = $_.Exception.Message
    Log-Error -errorMessage $errorMsg
    Write-Host ""
    Write-Host " FATAL ERROR: $errorMsg" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ===================================================================
# END OF SCRIPT
# ===================================================================
