@echo off
REM ========================================
REM Dashboard Consular - Detener Servicio
REM ========================================

echo Deteniendo Dashboard Consular (puerto 8501)...

REM Buscar y matar el proceso de Streamlit en puerto 8501
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do (
    echo Deteniendo proceso %%a
    taskkill /PID %%a /F
)

echo.
echo Dashboard detenido correctamente
pause
