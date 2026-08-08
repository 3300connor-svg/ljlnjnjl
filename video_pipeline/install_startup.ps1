# install_startup.ps1 — Register the pipeline to launch on Windows login.
# Run once as Administrator (or allow Task Scheduler to run as current user).

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartupBat = Join-Path $ScriptDir "start.bat"
$TaskName   = "WaveSpeedVideoPipeline"

# Remove existing task if present
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$StartupBat`"" -WorkingDirectory $ScriptDir
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Run only when user is logged in, in hidden window
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Force

Write-Host "Registered: '$TaskName' — will start automatically on next login."
Write-Host "To remove:  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
