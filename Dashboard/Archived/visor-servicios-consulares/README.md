# Visor de Servicios Consulares

Sistema profesional de análisis y visualización de datos consulares mexicanos con arquitectura modular y frontend optimizado.

## 🚀 Características Principales

- **Dashboard interactivo** con Plotly Dash
- **Base de datos SQLite** optimizada
- **Análisis temporal** y comparativo avanzado
- **Exportación PDF** profesional
- **Arquitectura modular** y escalable
- **Testing automatizado**

## 📁 Estructura del Proyecto

```
visor-servicios-consulares/
├── src/
│   ├── config/          # Configuraciones centralizadas
│   ├── core/            # Lógica de negocio principal
│   ├── components/      # Componentes reutilizables
│   └── pages/           # Páginas del dashboard
├── tests/               # Tests automatizados
├── docs/                # Documentación
├── data/                # Datos y base de datos
└── requirements.txt     # Dependencias
```

## 🛠️ Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv
.venv\Scripts\activate  # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python src/app.py
```

## 🎯 Navegación

### 📊 Dashboard Principal
- Análisis general con KPIs principales
- Gráficas temporales interactivas
- Comparación de períodos
- Análisis por servicio específico

### 🔧 Administración
- Gestión de archivos de datos
- Configuración del sistema
- Backup automático

### 📈 Reportes
- Exportación PDF avanzada
- Análisis predictivo básico
- Reportes programados

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/

# Test específico
pytest tests/test_database.py -v
```

## 📖 Documentación

Ver `docs/` para documentación detallada de:
- API Reference
- Guías de usuario
- Configuración avanzada

## 🔄 Migración desde Dashboard Mayo

Este proyecto es una reescritura completa del Dashboard Mayo original con:
- Arquitectura modular
- Performance optimizada
- UI/UX mejorada
- Código simplificado y mantenible

---

**Desarrollado por:** Claude Code Assistant  
**Versión:** 2.0  
**Fecha:** Agosto 2025