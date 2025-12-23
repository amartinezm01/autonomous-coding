# Instalación Global del Agente Autónomo

## Método 1: Agregar al PATH del Sistema (Recomendado)

### Windows (PowerShell Admin):
```powershell
# Agregar el directorio al PATH del usuario
$agentPath = "C:\Users\ROG\OneDrive\Documentos\SOFTWARE ALEX\PROYECTOS - DESARROLLO\CREARDOR DE SKILL\Skill Plus\autonomous-coding"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$agentPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$agentPath", "User")
    Write-Host "Agregado al PATH. Reinicia la terminal."
}
```

### Uso después de agregar al PATH:
```powershell
# Desde cualquier directorio de proyecto
run-agent.bat                     # Usa directorio actual, 5 iteraciones
run-agent.bat . 10               # Directorio actual, 10 iteraciones
run-agent.bat "C:\mi\proyecto"   # Proyecto específico

# O con PowerShell
.\run-agent.ps1 -MaxIterations 10
.\run-agent.ps1 -ProjectDir "C:\mi\proyecto" -MaxIterations 20
```

---

## Método 2: Alias en PowerShell Profile

### Crear alias permanente:
```powershell
# Abrir profile
notepad $PROFILE

# Agregar estas líneas:
function Start-Agent {
    param(
        [string]$ProjectDir = $PWD.Path,
        [int]$Iterations = 5
    )
    $agentPath = "C:\Users\ROG\OneDrive\Documentos\SOFTWARE ALEX\PROYECTOS - DESARROLLO\CREARDOR DE SKILL\Skill Plus\autonomous-coding"
    Push-Location $agentPath
    python autonomous_agent_demo.py --project-dir $ProjectDir --max-iterations $Iterations
    Pop-Location
}
Set-Alias agent Start-Agent
```

### Uso:
```powershell
# Desde cualquier directorio
agent                    # Directorio actual
agent -Iterations 10     # Con 10 iteraciones
agent -ProjectDir "C:\otro\proyecto"
```

---

## Método 3: Crear un Comando Global

### Crear `agent.cmd` en un directorio del PATH:
```batch
@echo off
python "C:\Users\ROG\OneDrive\Documentos\SOFTWARE ALEX\PROYECTOS - DESARROLLO\CREARDOR DE SKILL\Skill Plus\autonomous-coding\autonomous_agent_demo.py" --project-dir %CD% %*
```

Guardar en `C:\Windows\System32\agent.cmd` o cualquier directorio del PATH.

---

## Notas Importantes

1. **Primera ejecución en un proyecto nuevo**: El agente crea `feature_list.json` con tests. Esto toma 10-20 minutos.

2. **Ejecuciones posteriores**: El agente continúa donde quedó, implementando features.

3. **Especificación personalizada**: Para cada proyecto, crea un archivo `app_spec.txt` en la raíz del proyecto describiendo la aplicación.

4. **Credenciales**: El agente usa las credenciales de Claude Code guardadas en `~/.claude/.credentials.json`.

---

## Ejemplo: Iniciar en un Nuevo Proyecto

```powershell
# 1. Ir al nuevo proyecto
cd "C:\mi\nuevo\proyecto"

# 2. Crear app_spec.txt (opcional, si no existe usará uno genérico)
# Describe tu aplicación, tecnologías, features, etc.

# 3. Ejecutar agente
agent -Iterations 10

# O directamente
python "C:\...\autonomous-coding\autonomous_agent_demo.py" --project-dir . --max-iterations 10
```
