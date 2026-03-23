# Configuración de Inicio Automático - Dashboard Consular

## 📋 Resumen

Este dashboard se ejecutará automáticamente cada vez que inicies sesión en Windows, corriendo en **http://localhost:8501**

---

## 🚀 Instalación del Inicio Automático

### Opción 1: Configuración Automática (Recomendado)

1. **Abre PowerShell como Administrador:**
   - Presiona `Win + X`
   - Selecciona "Windows PowerShell (Administrador)" o "Terminal (Administrador)"

2. **Navega al directorio:**
   ```powershell
   cd "C:\Users\consuladscrito\claudecode\Dashboard\Inicio"
   ```

3. **Ejecuta el script de configuración:**
   ```powershell
   .\setup_autostart.ps1
   ```

4. **¡Listo!** El dashboard se iniciará automáticamente al iniciar sesión.

---

### Opción 2: Configuración Manual (Task Scheduler)

1. Presiona `Win + R` y escribe: `taskschd.msc`

2. Clic en "Crear tarea básica..."

3. Completa los campos:
   - **Nombre:** Dashboard-Consular-AutoStart
   - **Descripción:** Inicia automáticamente el Dashboard Consular

4. **Desencadenador:** "Al iniciar sesión"

5. **Acción:** "Iniciar un programa"
   - **Programa:** `cmd.exe`
   - **Argumentos:** `/c "C:\Users\consuladscrito\claudecode\Dashboard\Inicio\start_dashboard_service.bat"`

6. Marca las opciones:
   - ✅ Ejecutar tanto si el usuario inicia sesión o no
   - ✅ Ejecutar con los privilegios más altos

---

## 🎮 Uso Diario

### Iniciar Manualmente
```batch
cd "C:\Users\consuladscrito\claudecode\Dashboard\Inicio"
start_dashboard_service.bat
```

### Detener el Dashboard
```batch
cd "C:\Users\consuladscrito\claudecode\Dashboard\Inicio"
stop_dashboard_service.bat
```

### Acceder al Dashboard
Abre tu navegador y ve a: **http://localhost:8501**

---

## 🔧 Administración

### Ver Tarea Programada
```powershell
Get-ScheduledTask -TaskName "Dashboard-Consular-AutoStart"
```

### Deshabilitar Inicio Automático
```powershell
Disable-ScheduledTask -TaskName "Dashboard-Consular-AutoStart"
```

### Habilitar Inicio Automático
```powershell
Enable-ScheduledTask -TaskName "Dashboard-Consular-AutoStart"
```

### Eliminar Tarea Programada
```powershell
Unregister-ScheduledTask -TaskName "Dashboard-Consular-AutoStart" -Confirm:$false
```

O manualmente: Abre `taskschd.msc`, busca la tarea y elimínala.

---

## 📝 Archivos Creados

| Archivo | Descripción |
|---------|-------------|
| `start_dashboard_service.bat` | Inicia el dashboard en puerto 8501 |
| `stop_dashboard_service.bat` | Detiene el dashboard |
| `setup_autostart.ps1` | Configura el inicio automático |
| `INSTRUCCIONES_AUTOSTART.md` | Esta documentación |

---

## 🐛 Solución de Problemas

### El dashboard no inicia automáticamente

1. Verifica que la tarea existe:
   ```powershell
   Get-ScheduledTask -TaskName "Dashboard-Consular-AutoStart"
   ```

2. Revisa el estado de la tarea en `taskschd.msc`

3. Ejecuta manualmente para ver errores:
   ```batch
   start_dashboard_service.bat
   ```

### Puerto 8501 ocupado

Si el puerto 8501 ya está en uso, edita `start_dashboard_service.bat` y cambia el número de puerto:
```batch
--server.port=8502
```

### El dashboard se cierra solo

Verifica que el entorno virtual existe:
```batch
dir "C:\Users\consuladscrito\claudecode\.venv\Scripts\streamlit.exe"
```

Si no existe, reinstala las dependencias:
```batch
cd "C:\Users\consuladscrito\claudecode"
python -m venv .venv
.venv\Scripts\pip install -r Dashboard\Inicio\requirements.txt
```

---

## ⚙️ Configuración Avanzada

### Cambiar puerto

Edita `start_dashboard_service.bat`, línea que dice:
```batch
--server.port=8501
```

### Permitir acceso desde otras computadoras en la red

Cambia en `start_dashboard_service.bat`:
```batch
--server.address=localhost
```
Por:
```batch
--server.address=0.0.0.0
```

Luego accede desde otra PC usando: `http://[IP-DE-TU-PC]:8501`

---

## 📊 Estado del Sistema

- **Puerto:** 8501
- **Modo:** Headless (sin ventanas emergentes)
- **Reinicio automático:** Sí (hasta 3 intentos)
- **Usuario:** consuladscrito
- **Ruta del proyecto:** C:\Users\consuladscrito\claudecode\Dashboard\Inicio

---

## 💡 Recomendaciones

1. **Rendimiento:** El dashboard consume aproximadamente 200-300 MB de RAM
2. **Actualización:** Si actualizas el código, reinicia el servicio para ver los cambios
3. **Logs:** Los errores se mostrarán en la ventana de cmd si ejecutas manualmente
4. **Seguridad:** Si expones el dashboard en la red, considera agregar autenticación

---

## 📞 Soporte

Si tienes problemas, verifica:
- ✅ Python está instalado
- ✅ El entorno virtual existe en `.venv`
- ✅ Las dependencias están instaladas
- ✅ El archivo `dashboard_enhanced.py` existe
- ✅ No hay otro servicio usando el puerto 8501

Para ver qué está usando el puerto 8501:
```batch
netstat -ano | findstr :8501
```
