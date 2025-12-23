@echo off
REM Autonomous Coding Agent - Global Runner
REM Usage: run-agent.bat [project-dir] [max-iterations]

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Default values
set "PROJECT_DIR=%~1"
set "MAX_ITER=%~2"

if "%PROJECT_DIR%"=="" set "PROJECT_DIR=%CD%"
if "%MAX_ITER%"=="" set "MAX_ITER=5"

echo.
echo ========================================
echo   AUTONOMOUS CODING AGENT
echo ========================================
echo Project: %PROJECT_DIR%
echo Iterations: %MAX_ITER%
echo.

REM Change to script directory and run
cd /d "%SCRIPT_DIR%"
python autonomous_agent_demo.py --project-dir "%PROJECT_DIR%" --max-iterations %MAX_ITER%

endlocal
