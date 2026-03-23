@echo off
echo ========================================
echo      BACKEND - CONTROL DE VACACIONES
echo ========================================
echo.

echo 🔍 Verificando dependencias del backend...
if not exist "node_modules" (
    echo ❌ Dependencias no encontradas. Instalando...
    call npm install
    echo.
)

echo ✅ Dependencias verificadas
echo.

echo 📡 Iniciando servidor backend en puerto 5001...
echo 👤 Usuario admin: admin@empresa.com / admin123
echo.
echo 🔗 API disponible en: http://localhost:5001
echo 📊 Health check: http://localhost:5001/health
echo.
echo ⏹️  Para detener: Ctrl+C
echo ========================================
echo.

node debug_login.js