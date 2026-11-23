<#
.SYNOPSIS
    Registers a Windows Scheduled Task for Daily AI Ecosystem Rolling Updates.
.DESCRIPTION
    Creates or updates a scheduled task named 'AIEcosystemDailyUpdate' that triggers
    every day at 06:00 UTC (converted to local system time).
    Executes 'python -m core.scheduler --run-once'.
#>

param(
    [string]$ScheduleTime = "06:00", # Daily trigger time (UTC)
    [string]$TaskName = "AIEcosystemDailyUpdate"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AI ECOSYSTEM PIPELINE: WINDOWS TASK SCHEDULER SETUP    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$PythonExe = (Get-Command python.exe).Source

if (-not $PythonExe) {
    Write-Error "python.exe was not found in PATH. Please verify your Python installation."
}

Write-Host "[1] Project Root : $WorkspaceRoot"
Write-Host "[2] Python Binary: $PythonExe"
Write-Host "[3] Schedule Time: $ScheduleTime UTC daily"

# Convert UTC time to local time for Windows Task Scheduler
$UtcTime = [DateTime]::ParseExact($ScheduleTime, "HH:mm", [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeUniversal)
$LocalTime = $UtcTime.ToLocalTime().ToString("HH:mm")

Write-Host "[4] Local System Trigger Time: $LocalTime"

$Action = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "-m core.scheduler --run-once" `
    -WorkingDirectory $WorkspaceRoot

$Trigger = New-ScheduledTaskTrigger -Daily -At $LocalTime

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Write-Host "[5] Registering Scheduled Task '$TaskName'..."

# Unregister previous if exists
$Existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "    Found existing task. Unregistering old version..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Automated Daily 6-Month Rolling AI Ecosystem Intelligence Ingestion Pipeline"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Scheduled Task '$TaskName' Registered Successfully!" -ForegroundColor Green
Write-Host "           Next Run: Today/Tomorrow at $LocalTime local ($ScheduleTime UTC)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
