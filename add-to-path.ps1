# Add autonomous-coding to user PATH
$agentPath = "C:\Users\ROG\OneDrive\Documentos\SOFTWARE ALEX\PROYECTOS - DESARROLLO\CREARDOR DE SKILL\Skill Plus\autonomous-coding"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*autonomous-coding*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$agentPath", "User")
    Write-Host "SUCCESS: Agente agregado al PATH del usuario" -ForegroundColor Green
    Write-Host "Reinicia la terminal para usar los comandos:" -ForegroundColor Yellow
    Write-Host "  run-agent.bat"
    Write-Host "  run-agent.ps1"
} else {
    Write-Host "El agente ya estaba en el PATH" -ForegroundColor Cyan
}
