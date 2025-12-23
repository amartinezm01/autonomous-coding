# Autonomous Coding Agent - PowerShell Global Runner
# Usage: .\run-agent.ps1 [-ProjectDir <path>] [-MaxIterations <num>] [-Model <model>]

param(
    [string]$ProjectDir = $PWD.Path,
    [int]$MaxIterations = 5,
    [string]$Model = "claude-opus-4-5-20251101"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "========================================"
Write-Host "  AUTONOMOUS CODING AGENT"
Write-Host "========================================"
Write-Host "Project: $ProjectDir"
Write-Host "Iterations: $MaxIterations"
Write-Host "Model: $Model"
Write-Host ""

# Change to script directory and run
Push-Location $ScriptDir
try {
    python autonomous_agent_demo.py --project-dir $ProjectDir --max-iterations $MaxIterations --model $Model
}
finally {
    Pop-Location
}
