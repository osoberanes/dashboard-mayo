# 🏢 Control de Vacaciones

Sistema completo para la gestión de solicitudes de vacaciones con autenticación, roles de usuario y flujo de aprobación.

## 🚀 Inicio Rápido

### 1. Instalación Inicial
```bash
# Ejecutar una sola vez para configurar el proyecto
setup.bat
```

### 2. Iniciar Aplicación Completa
```bash
# Inicia tanto backend como frontend
start.bat
```

### 3. Acceder al Sistema
- **URL**: http://localhost:5173
- **Usuario Admin**: `admin@empresa.com`
- **Contraseña**: `admin123`

## 📜 Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `setup.bat` | Instalación inicial del proyecto |
| `start.bat` | Inicia toda la aplicación (backend + frontend) |
| `stop.bat` | Detiene todos los servidores |
| `start-backend.bat` | Solo servidor backend (puerto 5001) |
| `start-frontend.bat` | Solo servidor frontend (puerto 5173) |

## 🏗️ Arquitectura

### Backend (Puerto 5001)
- **Node.js + Express**
- **SQLite** para desarrollo
- **JWT** para autenticación
- **bcrypt** para encriptación de contraseñas

### Frontend (Puerto 5173)
- **React 18** con Vite
- **React Router** para navegación
- **Axios** para llamadas API
- **CSS Modules** para estilos

## 👥 Roles de Usuario

### 🔴 Admin (A)
- Gestión completa de usuarios
- Aprobación/rechazo de solicitudes
- Acceso a reportes y estadísticas
- Configuración del sistema

### 🟡 Manager (B)
- Aprobación/rechazo de solicitudes
- Vista de reportes de su área
- Gestión de usuarios de su departamento

### 🟢 Employee (C)
- Crear solicitudes de vacaciones
- Ver sus propias solicitudes
- Cambiar contraseña

## 🗃️ Base de Datos

### Tablas Principales
- **usuarios**: Información de usuarios y roles
- **solicitudes_vacaciones**: Solicitudes con flujo de aprobación
- **departamentos**: Organización por departamentos
- **dias_festivos**: Calendario de días festivos

## 🔧 Funcionalidades

### ✅ Implementadas
- [x] Autenticación JWT con roles
- [x] Crear/ver solicitudes de vacaciones
- [x] Flujo de aprobación/rechazo
- [x] Dashboard con estadísticas
- [x] Gestión de usuarios (admin)
- [x] Cálculo automático de días
- [x] Validaciones básicas de fechas

### 🚧 Pendientes
- [ ] Validaciones avanzadas (viernes, usuarios espejo)
- [ ] Integración con Google Sheets
- [ ] Calendario visual de vacaciones
- [ ] Notificaciones por email
- [ ] Acumulación automática de días

## 🛠️ Desarrollo

### Estructura del Proyecto
```
Control_Vacaciones/
├── server/                 # Backend estructura original
├── client/                 # Frontend React
├── debug_login.js          # Servidor temporal funcional
├── database.sqlite         # Base de datos SQLite
├── start.bat              # Script principal
├── stop.bat               # Script para detener
└── README.md              # Esta documentación
```

### APIs Disponibles

#### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/verify` - Verificar token

#### Solicitudes
- `GET /api/solicitudes` - Listar solicitudes
- `POST /api/solicitudes` - Crear solicitud
- `PUT /api/solicitudes/:id/aprobar` - Aprobar solicitud
- `PUT /api/solicitudes/:id/rechazar` - Rechazar solicitud

#### Usuarios (Admin)
- `GET /api/usuarios` - Listar usuarios
- `POST /api/usuarios` - Crear usuario
- `PUT /api/usuarios/:id/toggle` - Activar/desactivar usuario

#### Reportes
- `GET /api/reportes/estadisticas` - Estadísticas generales

## 🔒 Seguridad

- **JWT Tokens** con expiración de 24h
- **bcrypt** para hash de contraseñas
- **Validación de roles** en cada endpoint
- **CORS** configurado para desarrollo
- **Sanitización** de inputs

## 🐛 Solución de Problemas

### Puerto ocupado
```bash
# Detener todos los procesos
stop.bat

# Verificar puertos
netstat -ano | findstr :5001
netstat -ano | findstr :5173
```

### Dependencias faltantes
```bash
# Reinstalar todo
setup.bat
```

### Base de datos corrupta
```bash
# Eliminar y recrear
del database.sqlite
start-backend.bat
```

## 📞 Soporte

Para problemas o mejoras, revisar:
1. Logs del backend en la consola
2. Consola del navegador (F12)
3. Verificar que ambos servidores estén corriendo

---

**🎉 ¡Sistema listo para usar!** 

Ejecuta `start.bat` y visita http://localhost:5173