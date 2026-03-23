@echo off
REM ========================================
REM Dashboard Consular - Inicio Automático
REM Puerto: 8501
REM ========================================

echo [%date% %time%] Iniciando Dashboard Consular...

REM Cambiar al directorio del proyecto
cd /d "C:\Users\consuladscrito\claudecode"

REM Verificar que el entorno virtual existe
if not exist ".venv\Scripts\streamlit.exe" (
    echo [ERROR] No se encontró el entorno virtual en .venv
    echo Por favor ejecuta: python -m venv .venv
    exit /b 1
)

REM Verificar que dashboard_enhanced.py existe
if not exist "Dashboard\Inicio\dashboard_enhanced.py" (
    echo [ERROR] No se encontró dashboard_enhanced.py
    exit /b 1
)

REM Iniciar Streamlit en el puerto 8501
echo [%date% %time%] Iniciando en http://localhost:8501
echo.

".\.venv\Scripts\streamlit.exe" run "Dashboard\Inicio\dashboard_enhanced.py" ^
    --server.port=8501 ^
    --server.headless=true ^
    --server.runOnSave=false ^
    --browser.gatherUsageStats=false ^
    --server.address=localhost

REM Si el proceso termina, registrar el evento
echo [%date% %time%] Dashboard detenido
