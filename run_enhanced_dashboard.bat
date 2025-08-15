@echo off
echo Iniciando Dashboard Consular Mejorado...
echo.
echo Dashboard URL: http://localhost:8503
echo Para detener: Ctrl+C
echo.

cd /d "C:\Users\consuladscrito\claudecode"
".\.venv\Scripts\streamlit.exe" run "Inicio\dashboard_enhanced.py" --server.headless=true --server.port=8503

pause