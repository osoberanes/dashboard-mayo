@echo off
echo ========================================
echo   CONTROL DE VACACIONES - DETENIENDO
echo ========================================
echo.

echo 🛑 Deteniendo servidores Node.js...
taskkill /f /im node.exe >nul 2>&1

echo 🛑 Deteniendo procesos npm...
taskkill /f /im npm.exe >nul 2>&1

echo 🛑 Deteniendo Vite dev server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /f /pid %%a >nul 2>&1

echo 🛑 Deteniendo servidor backend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do taskkill /f /pid %%a >nul 2>&1

echo.
echo ✅ Todos los servidores han sido detenidos
echo.

timeout /t 2 /nobreak >nul
echo ========================================
echo 🔄 Para reiniciar, usa: start.bat
echo ========================================
pause