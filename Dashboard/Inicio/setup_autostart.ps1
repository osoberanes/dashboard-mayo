# ========================================
# Script PowerShell para configurar inicio automático
# Dashboard Consular en Windows Task Scheduler
# ========================================

# Requiere ejecutarse como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "Haz clic derecho en PowerShell y selecciona 'Ejecutar como administrador'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurando Dashboard Consular" -ForegroundColor Cyan
Write-Host "Inicio Automático con Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$taskName = "Dashboard-Consular-AutoStart"
$scriptPath = "C:\Users\consuladscrito\claudecode\Dashboard\Inicio\start_dashboard_service.bat"
$description = "Inicia automáticamente el Dashboard Consular en el puerto 8501"

# Verificar que el script existe
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: No se encontró el script en: $scriptPath" -ForegroundColor Red
    pause
    exit 1
}

# Eliminar tarea existente si existe
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Eliminando tarea existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Crear la acción (ejecutar el script)
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""

# Crear el trigger (al iniciar sesión)
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Configuración adicional
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Crear el principal (usuario actual)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Registrar la tarea
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description $description `
        -Force

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "¡Configuración completada exitosamente!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "El Dashboard se iniciará automáticamente cuando inicies sesión en Windows" -ForegroundColor White
    Write-Host "URL: http://localhost:8501" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Comandos útiles:" -ForegroundColor Yellow
    Write-Host "  - Iniciar manualmente: .\start_dashboard_service.bat" -ForegroundColor White
    Write-Host "  - Detener servicio: .\stop_dashboard_service.bat" -ForegroundColor White
    Write-Host "  - Ver tareas programadas: taskschd.msc" -ForegroundColor White
    Write-Host ""
    Write-Host "¿Deseas iniciar el dashboard ahora? (S/N)" -ForegroundColor Yellow
    $response = Read-Host

    if ($response -eq "S" -or $response -eq "s") {
        Write-Host "Iniciando dashboard..." -ForegroundColor Green
        Start-Process "cmd.exe" -ArgumentList "/c `"$scriptPath`""
        Start-Sleep -Seconds 3
        Write-Host "Dashboard iniciado. Abriendo navegador..." -ForegroundColor Green
        Start-Process "http://localhost:8501"
    }

} catch {
    Write-Host ""
    Write-Host "ERROR al crear la tarea programada:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Presiona cualquier tecla para salir..."
pause
