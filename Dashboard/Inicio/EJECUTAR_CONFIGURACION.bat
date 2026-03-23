@echo off
REM ========================================
REM Este script ejecuta la configuración
REM como Administrador automáticamente
REM ========================================

echo.
echo ========================================
echo Configuracion Dashboard Consular
echo ========================================
echo.
echo Este script necesita permisos de administrador
echo para crear la tarea programada.
echo.
echo Se abrira una ventana de PowerShell pidiendo
echo permisos de administrador.
echo.
pause

REM Ejecutar PowerShell como administrador
powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0setup_autostart.ps1\"' -Verb RunAs"

echo.
echo La configuracion se esta ejecutando en otra ventana...
echo.
pause
