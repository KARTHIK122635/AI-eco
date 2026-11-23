<#
.SYNOPSIS
    Daily AI Ecosystem Rolling Pipeline - Windows Scheduled Task Setup & Verification
.DESCRIPTION
    Validates and configures the automated daily Windows Scheduled Task:
    - Target schedule: 06:00 UTC daily.
    - Local time conversion: 06:00 UTC -> 11:30 local (+05:30 IST).
    - Invocation command: python -m core.scheduler --run-once (routine run, run_pilot=False).
    - Task Settings:
        * StartWhenAvailable: Catches up missed runs if system was sleeping or powered off.
        * MultipleInstances: IgnoreNew (prevents overlapping concurrent runs).
        * ExecutionTimeLimit: 2 hours (kills hung processes).
    - By default, runs in -DryRun mode to prevent unauthorized registration.
    - Requires human authorization before registering.
#>

param(
    [string]$ScheduleTime = "06:00", # Daily trigger time in UTC (HH:mm)
    [string]$TaskName = "AIEcosystemDailyUpdate",
    [switch]$DryRun = $true # Default: Dry-run verification only. Pass -DryRun:$false to register after approval.
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AI ECOSYSTEM PIPELINE: TASK SCHEDULER VERIFICATION     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$PythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source

if (-not $PythonExe) {
    Write-Error "python.exe was not found in PATH. Please verify your Python installation."
}

# Convert UTC time to local system time
$UtcTime = [DateTime]::ParseExact($ScheduleTime, "HH:mm", [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeUniversal)
$LocalTime = $UtcTime.ToLocalTime().ToString("HH:mm")
$TzOffset = [System.TimeZoneInfo]::Local.GetUtcOffset([DateTime]::UtcNow)

Write-Host "[1] Project Root           : $WorkspaceRoot"
Write-Host "[2] Python Executable      : $PythonExe"
Write-Host "[3] UTC Schedule Time      : $ScheduleTime UTC daily"
Write-Host "[4] Local System Time Zone : $([System.TimeZoneInfo]::Local.DisplayName) (UTC$([string]::Format('{0:+00;-00}:{1:D2}', $TzOffset.Hours, [Math]::Abs($TzOffset.Minutes))))"
Write-Host "[5] Local Trigger Time     : $LocalTime local ($ScheduleTime UTC)"
Write-Host "[6] Executed Command       : $PythonExe -m core.scheduler --run-once"
Write-Host "[7] Phase III Pilot Status : DISABLED by default (run_pilot=False)"
Write-Host "[8] Task Settings Config   :"
Write-Host "    - StartWhenAvailable   : Enabled (triggers run if system was sleeping/powered off)"
Write-Host "    - MultipleInstances    : IgnoreNew (prevents overlapping execution)"
Write-Host "    - ExecutionTimeLimit   : 2 Hours (enforces safety watchdog timeout)"
Write-Host "    - Battery Behavior     : AllowStartIfOnBatteries, DontStopIfGoingOnBatteries"

Write-Host "`n----------------------------------------------------------" -ForegroundColor Yellow
Write-Host " LAPTOP POWER & EXECUTION BEHAVIOR SPECIFICATION:          " -ForegroundColor Yellow
Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
Write-Host "* Scheduled execution requires the host machine to be powered on."
Write-Host "* If the machine is asleep or powered off at $LocalTime local,"
Write-Host "  the 'StartWhenAvailable' policy instructs Windows Task Scheduler"
Write-Host "  to immediately launch the pipeline as soon as the machine resumes."
Write-Host "* If a run is interrupted by power loss or sleep during execution,"
Write-Host "  the scheduler recovery subsystem detects the interrupted run"
Write-Host "  in collection_logs and safely catches up with stage-level resumption."
Write-Host "----------------------------------------------------------`n" -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "==========================================================" -ForegroundColor Magenta
    Write-Host " [DRY-RUN MODE] Configuration verified successfully!      " -ForegroundColor Magenta
    Write-Host " Scheduled task '$TaskName' has NOT been registered.       " -ForegroundColor Magenta
    Write-Host " Awaiting explicit human authorization.                   " -ForegroundColor Magenta
    Write-Host ""
    Write-Host " To register and activate the task after approval, execute:"
    Write-Host "   powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" -DryRun:`$false"
    Write-Host "==========================================================" -ForegroundColor Magenta
    return
}

# Live Registration (Only executed if -DryRun:$false is explicitly passed)
Write-Host "[9] Human authorization granted. Registering Scheduled Task '$TaskName'..." -ForegroundColor Cyan

$Existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "    Found existing task. Unregistering old version..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

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

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Automated Daily 6-Month Rolling AI Ecosystem Intelligence Ingestion Pipeline (06:00 UTC / $LocalTime Local)"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Scheduled Task '$TaskName' Registered Successfully!" -ForegroundColor Green
Write-Host "           Next Trigger: $LocalTime local ($ScheduleTime UTC)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
