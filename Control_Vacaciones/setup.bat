@echo off
echo ========================================
echo   CONTROL DE VACACIONES - INSTALACIÓN
echo ========================================
echo.

echo 🔧 Configurando proyecto por primera vez...
echo.

echo 📦 Instalando dependencias del backend...
if exist "package.json" (
    call npm install
    if errorlevel 1 (
        echo ❌ Error instalando dependencias del backend
        pause
        exit /b 1
    )
    echo ✅ Backend configurado
) else (
    echo ❌ package.json no encontrado en el directorio raíz
    pause
    exit /b 1
)

echo.
echo 📦 Instalando dependencias del frontend...
if exist "client\package.json" (
    cd client
    call npm install
    if errorlevel 1 (
        echo ❌ Error instalando dependencias del frontend
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Frontend configurado
) else (
    echo ❌ client/package.json no encontrado
    pause
    exit /b 1
)

echo.
echo 🗄️  Inicializando base de datos...
echo ℹ️  La base de datos SQLite se creará automáticamente al primer inicio
echo.

echo ========================================
echo ✅ INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo 📋 INFORMACIÓN IMPORTANTE:
echo 👤 Usuario administrador: admin@empresa.com
echo 🔑 Contraseña: admin123
echo.
echo 🚀 Para iniciar la aplicación: start.bat
echo 📡 Solo backend: start-backend.bat
echo 🌐 Solo frontend: start-frontend.bat
echo 🛑 Para detener todo: stop.bat
echo.
echo ========================================
pause