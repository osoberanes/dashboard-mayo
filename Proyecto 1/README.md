# Sistema de Análisis de Producción

Sistema web para analizar patrones de producción y recaudación de oficina gubernamental basado en archivos Excel de producción diaria.

## Características

- 🔐 **Autenticación de usuarios** - Sistema seguro de login y registro
- 📊 **Análisis de tendencias** - Visualización de patrones de producción y ventas
- 📁 **Importación de Excel** - Procesamiento automático de archivos XLS/XLSX
- 🏷️ **Categorización** - Agrupación de productos similares
- 📈 **Dashboard interactivo** - Métricas en tiempo real y visualizaciones
- 📋 **Reportes** - Exportación de análisis y datos
- 🔍 **Performance tracking** - Seguimiento de rendimiento por producto

## Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para manejo de base de datos
- **PostgreSQL/SQLite** - Base de datos (SQLite para desarrollo, PostgreSQL para producción)
- **Pandas** - Procesamiento de datos de Excel
- **Plotly** - Generación de gráficos

### Frontend (Próximamente)
- **React** - Interfaz de usuario
- **TypeScript** - Tipado estático
- **Chart.js/Plotly** - Visualizaciones

## Instalación y Configuración

### 1. Clonar y configurar el proyecto

```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Copiar configuración de ejemplo
cp .env.example .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env`:

```env
DATABASE_URL=sqlite:///./production_analytics.db
SECRET_KEY=tu-clave-secreta-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./data/uploads
```

### 3. Ejecutar la aplicación

```bash
# Ejecutar servidor de desarrollo
python run.py
```

La API estará disponible en: http://localhost:8000

### 4. Documentación de la API

FastAPI genera documentación automática:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estructura del Proyecto

```
claudecode/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints de la API
│   │   ├── core/         # Configuración y utilidades
│   │   ├── models/       # Modelos de base de datos
│   │   └── services/     # Lógica de negocio
│   └── alembic/          # Migraciones de base de datos
├── frontend/             # Aplicación React (próximamente)
├── data/
│   └── uploads/          # Archivos Excel subidos
├── tests/                # Pruebas
└── requirements.txt      # Dependencias Python
```

## Uso del Sistema

### 1. Registro de Usuario

```bash
POST /api/v1/auth/register
```

### 2. Login

```bash
POST /api/v1/auth/token
```

### 3. Subir archivo Excel

```bash
POST /api/v1/files/upload
```

### 4. Ver análisis

```bash
GET /api/v1/analytics/summary
GET /api/v1/analytics/performance
GET /api/v1/analytics/trends/revenue
```

## Formato de Archivos Excel

El sistema acepta archivos Excel con las siguientes columnas (nombres flexibles):

| Columna | Alternativas | Descripción |
|---------|-------------|-------------|
| fecha | date | Fecha de producción |
| producto | product | Nombre del producto |
| codigo | code | Código del producto |
| cantidad | quantity | Cantidad producida |
| vendido | sold | Cantidad vendida |
| ingresos | revenue | Ingresos generados |
| costo | cost | Costo unitario |

## Características del Sistema

### Análisis Disponibles

1. **Performance por Producto**
   - Cantidad total producida/vendida
   - Ingresos totales
   - Tasa de conversión (sell-through rate)
   - Producción promedio diaria

2. **Tendencias Temporales**
   - Ingresos por día/semana/mes
   - Patrones de producción
   - Identificación de picos y bajas

3. **Análisis por Categoría**
   - Distribución de productos por categoría
   - Performance relativo entre categorías
   - Preferencias de mercado

### Características Técnicas

- **Escalabilidad**: Arquitectura modular lista para múltiples usuarios
- **Seguridad**: Autenticación JWT y validación de datos
- **Performance**: Consultas optimizadas y procesamiento eficiente
- **Flexibilidad**: Adaptable a diferentes formatos de Excel

## Próximos Desarrollos

- [ ] Interfaz web React
- [ ] Exportación de reportes en PDF/Excel
- [ ] Predicciones con machine learning
- [ ] Notificaciones automáticas
- [ ] Dashboard en tiempo real
- [ ] Integración con otros sistemas

## Configuración para Producción

### PostgreSQL

```env
DATABASE_URL=postgresql://usuario:password@localhost/production_analytics
```

### Docker (Próximamente)

```bash
docker-compose up -d
```

## Soporte

Para reportar problemas o solicitar características, crea un issue en el repositorio del proyecto.