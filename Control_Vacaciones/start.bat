@echo off
echo ========================================
echo    CONTROL DE VACACIONES - INICIO
echo ========================================
echo.

echo 🔍 Verificando dependencias...
if not exist "node_modules" (
    echo ❌ Dependencias no encontradas. Instalando...
    call npm install
    echo.
)

if not exist "client\node_modules" (
    echo ❌ Dependencias del frontend no encontradas. Instalando...
    cd client
    call npm install
    cd ..
    echo.
)

echo ✅ Dependencias verificadas
echo.

echo 🚀 Iniciando servidores...
echo.

echo 📡 Iniciando servidor backend (Puerto 5001)...
start "Backend Server" cmd /k "node debug_login.js"

echo ⏳ Esperando que el backend esté listo...
timeout /t 3 /nobreak >nul

echo 🌐 Iniciando servidor frontend (Puerto 5173)...
cd client
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo ✅ SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:5173
echo 📡 Backend:  http://localhost:5001
echo 👤 Admin:    admin@empresa.com / admin123
echo.
echo 📝 Para detener todos los servidores, usa: stop.bat
echo ========================================

pause