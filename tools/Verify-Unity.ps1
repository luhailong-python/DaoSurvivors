param([string]$EditorPath, [switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $EditorPath) {
    $candidates = @((Join-Path $projectRoot '.local\Unity\Editor\Unity.exe'), 'E:\u3d\6000.4.5f1\Editor\Unity.exe')
    $EditorPath = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $EditorPath -or -not (Test-Path -LiteralPath $EditorPath)) {
    throw 'Unity.exe was not found. Pass -EditorPath with an installed Unity 6 Editor.'
}
$logDir = Join-Path $projectRoot '.local\logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$method = if ($PrepareOnly) { 'DaoSurvivor.Editor.BuildTools.PrepareProject' } else { 'DaoSurvivor.Editor.BuildTools.VerifyAndBuild' }
$logPath = Join-Path $logDir 'unity-verify.log'
$argumentList = @('-batchmode', '-nographics', '-quit', '-projectPath', ('"' + $projectRoot + '"'), '-executeMethod', $method, '-logFile', ('"' + $logPath + '"'))
$process = Start-Process -FilePath $EditorPath -ArgumentList $argumentList -WorkingDirectory $projectRoot -WindowStyle Hidden -Wait -PassThru
Write-Output "Unity exit code: $($process.ExitCode)"
Write-Output "Unity log: $logPath"
if ($process.ExitCode -ne 0) { Get-Content -LiteralPath $logPath -Tail 70; exit $process.ExitCode }
