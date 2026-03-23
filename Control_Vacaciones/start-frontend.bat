@echo off
echo ========================================
echo     FRONTEND - CONTROL DE VACACIONES
echo ========================================
echo.

echo 🔍 Verificando dependencias del frontend...
cd client

if not exist "node_modules" (
    echo ❌ Dependencias no encontradas. Instalando...
    call npm install
    echo.
)

echo ✅ Dependencias verificadas
echo.

echo 🌐 Iniciando servidor frontend en puerto 5173...
echo 🔗 Aplicación disponible en: http://localhost:5173
echo 📡 Conectando con backend en: http://localhost:5001
echo.
echo ⚠️  NOTA: Asegúrate de que el backend esté corriendo
echo    Usa start-backend.bat en otra ventana
echo.
echo ⏹️  Para detener: Ctrl+C
echo ========================================
echo.

npm run dev