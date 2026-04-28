#!/usr/bin/env powershell
# PowerShell script to start the Stock Analysis System

param(
    [switch]$ClearCache
)

Write-Host "Starting Stock Analysis System" -ForegroundColor Green
Write-Host "=" * 50

function Clear-AllCache {
    Write-Host "Clearing ALL cache and temporary files..." -ForegroundColor Yellow
    Write-Host "=" * 60

    $filesRemoved = 0
    $dirsRemoved = 0

    # Clear main cache directory
    $cacheDir = "data/cache"
    if (Test-Path $cacheDir) {
        Write-Host "Clearing $cacheDir..." -ForegroundColor Cyan
        Get-ChildItem $cacheDir -File | ForEach-Object {
            try {
                Remove-Item $_.FullName -Force
                $filesRemoved++
                Write-Host "  ✓ Removed: $($_.Name)" -ForegroundColor Green
            } catch {
                Write-Host "  ✗ Failed to remove $($_.Name): $_" -ForegroundColor Red
            }
        }
        Write-Host "  Cleared $cacheDir" -ForegroundColor Green
    } else {
        Write-Host "Cache directory $cacheDir not found, creating..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    }

    # Clear processed data
    $processedDir = "data/processed_data"
    if (Test-Path $processedDir) {
        Write-Host "`nClearing $processedDir..." -ForegroundColor Cyan
        Get-ChildItem $processedDir -File | ForEach-Object {
            try {
                Remove-Item $_.FullName -Force
                $filesRemoved++
                Write-Host "  ✓ Removed: $($_.Name)" -ForegroundColor Green
            } catch {
                Write-Host "  ✗ Failed to remove $($_.Name): $_" -ForegroundColor Red
            }
        }
        Write-Host "  Cleared $processedDir" -ForegroundColor Green
    }

    # Clear Python cache directories
    Write-Host "`nClearing Python cache directories..." -ForegroundColor Cyan
    Get-ChildItem -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            Remove-Item $_ -Recurse -Force
            $dirsRemoved++
            Write-Host "  ✓ Removed: $_" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Failed to remove $_: $_" -ForegroundColor Red
        }
    }

    # Clear .pyc files
    Write-Host "`nClearing .pyc files..." -ForegroundColor Cyan
    Get-ChildItem -Recurse -File -Name "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            Remove-Item $_ -Force
            $filesRemoved++
        } catch {
            Write-Host "  ✗ Failed to remove $_: $_" -ForegroundColor Red
        }
    }

    # Clear temporary files
    Write-Host "`nClearing temporary files..." -ForegroundColor Cyan
    $tempPatterns = @("*.tmp", "*.temp")
    foreach ($pattern in $tempPatterns) {
        Get-ChildItem -File -Name $pattern -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                Remove-Item $_ -Force
                $filesRemoved++
                Write-Host "  ✓ Removed: $_" -ForegroundColor Green
            } catch {
                Write-Host "  ✗ Failed to remove $_: $_" -ForegroundColor Red
            }
        }
    }

    Write-Host "`n" + "=" * 60
    Write-Host "CACHE CLEARING COMPLETED" -ForegroundColor Green
    Write-Host "Files removed: $filesRemoved" -ForegroundColor Green
    Write-Host "Directories removed: $dirsRemoved" -ForegroundColor Green
    Write-Host "=" * 60
}

function Stop-ExistingStreamlit {
    Write-Host "Checking for existing Streamlit processes..." -ForegroundColor Cyan

    $streamlitProcesses = Get-Process | Where-Object { $_.ProcessName -like "python*" -and $_.MainWindowTitle -like "*streamlit*" }

    if ($streamlitProcesses) {
        Write-Host "Found running Streamlit instance, closing it..." -ForegroundColor Yellow
        $streamlitProcesses | Stop-Process -Force
        Start-Sleep -Seconds 2
        Write-Host "Closed old instance" -ForegroundColor Green
    } else {
        Write-Host "No running Streamlit instance found" -ForegroundColor Green
    }
}

# Main execution
if ($ClearCache) {
    Clear-AllCache
    Write-Host
}

# Kill existing Streamlit processes
Stop-ExistingStreamlit
Write-Host

# Start the application
Write-Host "Starting application..." -ForegroundColor Blue
Write-Host "Please open browser at: http://localhost:8501" -ForegroundColor Blue
Write-Host "Press Ctrl+C to stop application" -ForegroundColor Blue
Write-Host

try {
    streamlit run src/app_new.py
} catch {
    Write-Host "Error starting application: $_" -ForegroundColor Red
}