param(
    [string]$Steps = "download,basic_cleaning",
    [string]$HydraOptions = ""
)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$env:Path = (Join-Path $PSScriptRoot ".venv\Scripts") + ";" + $env:Path
$env:WANDB_MODE = "online"
$env:MPLCONFIGDIR = Join-Path $PSScriptRoot "artifacts\matplotlib-cache"
New-Item -ItemType Directory -Force -Path $env:MPLCONFIGDIR | Out-Null
$pipelineOptions = ("main.env_manager=local " + $HydraOptions).Trim()
& (Join-Path $PSScriptRoot ".venv\Scripts\python.exe") windows_run.py --steps $Steps --hydra-options $pipelineOptions
exit $LASTEXITCODE
