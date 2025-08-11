# 📊 Sistema de Análisis de Producción y Recaudación

## Documentación Técnica Completa

---

## 📑 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Guía de Uso](#guía-de-uso)
5. [API Reference](#api-reference)
6. [Formatos de Archivos Soportados](#formatos-de-archivos-soportados)
7. [Análisis y Reportes](#análisis-y-reportes)
8. [Base de Datos](#base-de-datos)
9. [Troubleshooting](#troubleshooting)
10. [Desarrollo y Extensión](#desarrollo-y-extensión)

---

## 📝 Descripción General

### Propósito
Sistema web desarrollado en Python para analizar patrones de producción y recaudación de oficinas gubernamentales, basado en archivos Excel/HTML de producción diaria que proporciona el sistema oficial.

### Características Principales
- 🔐 **Sistema de autenticación** seguro con JWT
- 📊 **Análisis de tendencias** temporales y por producto
- 📁 **Importación automática** de archivos Excel y HTML
- 🏷️ **Categorización inteligente** de productos/servicios
- 📈 **Dashboard interactivo** con métricas en tiempo real
- 📋 **Generación de reportes** exportables (Excel, CSV)
- 🔍 **Tracking de performance** detallado por producto
- 📱 **API RESTful** para integración con otros sistemas

### Tecnologías Utilizadas
- **Backend**: FastAPI, SQLAlchemy, Pandas, Plotly
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Procesamiento**: pandas, openpyxl, beautifulsoup4
- **Autenticación**: python-jose, passlib
- **Visualización**: plotly

---

## 🏗️ Arquitectura del Sistema

### Estructura del Proyecto
```
claudecode/
├── backend/
│   ├── app/
│   │   ├── api/              # Endpoints REST
│   │   │   ├── auth.py       # Autenticación
│   │   │   ├── files.py      # Carga de archivos
│   │   │   ├── products.py   # Gestión de productos
│   │   │   ├── analytics.py  # Análisis de datos
│   │   │   └── reports.py    # Generación de reportes
│   │   ├── core/             # Configuración central
│   │   │   ├── config.py     # Variables de entorno
│   │   │   ├── database.py   # Conexión DB
│   │   │   └── security.py   # Funciones de seguridad
│   │   ├── models/           # Modelos de datos
│   │   │   ├── user.py       # Usuario
│   │   │   ├── product.py    # Producto y categoría
│   │   │   └── production.py # Registros de producción
│   │   ├── services/         # Lógica de negocio
│   │   │   ├── file_processor.py    # Procesamiento archivos
│   │   │   └── report_generator.py  # Generación reportes
│   │   └── main.py           # Aplicación principal
│   └── alembic/              # Migraciones DB
├── data/
│   └── uploads/              # Archivos subidos
├── frontend/                 # Interfaz web (futuro)
├── tests/                    # Pruebas unitarias
├── requirements.txt          # Dependencias
├── run.py                    # Script de ejecución
└── .env                      # Variables de entorno
```

### Flujo de Datos
1. **Carga de archivo** → Procesamiento automático → Normalización de datos
2. **Análisis** → Cálculo de métricas → Generación de insights
3. **Visualización** → Dashboard → Exportación de reportes

---

## ⚙️ Instalación y Configuración

### Prerrequisitos
- Python 3.11 o superior
- Git (opcional)

### Instalación Paso a Paso

1. **Clonar/Descargar el proyecto**
   ```bash
   # Si usas Git
   git clone <repository-url>
   cd claudecode
   
   # O simplemente descargar y extraer el ZIP
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   ```bash
   # Copiar archivo de ejemplo
   cp .env.example .env
   
   # Editar .env con tus configuraciones
   ```

4. **Configuración del archivo .env**
   ```env
   # Base de datos (SQLite para desarrollo)
   DATABASE_URL=sqlite:///./production_analytics.db
   
   # Para producción con PostgreSQL
   # DATABASE_URL=postgresql://usuario:password@localhost/dbname
   
   # Seguridad
   SECRET_KEY=tu-clave-super-secreta-aqui-cambiar-en-produccion
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Archivos
   UPLOAD_DIR=./data/uploads
   ```

5. **Ejecutar la aplicación**
   ```bash
   python run.py
   ```

6. **Acceder al sistema**
   - API: http://localhost:8000
   - Documentación interactiva: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Configuración para Producción

#### PostgreSQL
1. **Instalar PostgreSQL**
2. **Crear base de datos**
   ```sql
   CREATE DATABASE production_analytics;
   CREATE USER analytics_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE production_analytics TO analytics_user;
   ```
3. **Actualizar .env**
   ```env
   DATABASE_URL=postgresql://analytics_user:secure_password@localhost/production_analytics
   SECRET_KEY=una-clave-muy-segura-y-larga-para-produccion
   ```

#### Docker (Opcional)
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

---

## 📖 Guía de Uso

### 1. Primer Uso del Sistema

#### Registro de Usuario
```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "admin",
  "email": "admin@oficina.gob.mx",
  "full_name": "Administrador",
  "password": "password123"
}'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=admin&password=password123"
```

### 2. Carga de Archivos

#### Formatos Soportados
- **.xlsx** - Excel moderno
- **.xls** - Excel clásico  
- **.html** - Tablas HTML (detectado automáticamente)

#### Vía API
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer <tu-token>" \
-F "file=@mayo.xls"
```

### 3. Consulta de Análisis

#### Dashboard General
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary?start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>"
```

#### Performance por Producto
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/performance" \
-H "Authorization: Bearer <tu-token>"
```

#### Tendencias Temporales
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/trends/revenue?period=daily" \
-H "Authorization: Bearer <tu-token>"
```

### 4. Generación de Reportes

#### Reporte Completo (Excel)
```bash
curl -X GET "http://localhost:8000/api/v1/reports/complete?start_date=2025-05-01" \
-H "Authorization: Bearer <tu-token>" \
-o "reporte_completo.xlsx"
```

#### Reporte por Categorías (CSV)
```bash
curl -X GET "http://localhost:8000/api/v1/reports/categories?format=csv" \
-H "Authorization: Bearer <tu-token>" \
-o "categorias.csv"
```

---

## 🔌 API Reference

### Autenticación

#### POST `/api/v1/auth/register`
Registro de nuevo usuario

**Body:**
```json
{
  "username": "string",
  "email": "string", 
  "full_name": "string",
  "password": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@oficina.gob.mx",
  "full_name": "Administrador",
  "is_active": true,
  "is_admin": false
}
```

#### POST `/api/v1/auth/token`
Login de usuario

**Body:** `application/x-www-form-urlencoded`
```
username=admin&password=password123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Gestión de Archivos

#### POST `/api/v1/files/upload`
Carga y procesa archivo de datos

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body:** Archivo (form-data)

**Response:** `200 OK`
```json
{
  "message": "Successfully imported 446 records",
  "batch_id": 1,
  "records_imported": 446
}
```

#### GET `/api/v1/files/batches`
Lista historial de cargas

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "filename": "mayo.xls",
    "records_imported": 446,
    "import_date": "2025-08-08T10:30:00",
    "status": "completed",
    "error_message": null
  }
]
```

### Análisis de Datos

#### GET `/api/v1/analytics/summary`
Dashboard principal con métricas generales

**Query Parameters:**
- `start_date` (optional): fecha inicio (YYYY-MM-DD)
- `end_date` (optional): fecha fin (YYYY-MM-DD)

**Response:** `200 OK`
```json
{
  "summary": {
    "total_produced": 446,
    "total_sold": 408,
    "total_revenue": 7752.0,
    "active_products": 60,
    "sell_through_rate": 91.48
  },
  "categories": [
    {
      "category_name": "Sin Categoría",
      "product_count": 60,
      "total_revenue": 7752.0,
      "total_production": 446
    }
  ],
  "top_products": [
    {
      "name": "RCM - DISTRITO FEDERAL - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
      "revenue": 380.0
    }
  ]
}
```

#### GET `/api/v1/analytics/performance`
Performance detallada por producto

**Query Parameters:**
- `start_date`, `end_date`: rango de fechas
- `category_id`: filtrar por categoría
- `limit`: número de resultados (default: 50)

**Response:** `200 OK`
```json
[
  {
    "product_id": 3,
    "product_name": "RCM - DISTRITO FEDERAL - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
    "category_name": "Sin Categoría",
    "total_produced": 20,
    "total_sold": 20,
    "total_revenue": 380.0,
    "avg_daily_production": 1.25,
    "sell_through_rate": 100.0
  }
]
```

#### GET `/api/v1/analytics/trends/revenue`
Análisis de tendencias de ingresos

**Query Parameters:**
- `start_date`, `end_date`: rango de fechas
- `product_id`: producto específico
- `category_id`: categoría específica
- `period`: granularidad ("daily", "weekly", "monthly")

**Response:** `200 OK`
```json
{
  "trends": [
    {
      "date": "2025-05-01",
      "value": 57.0
    },
    {
      "date": "2025-05-02", 
      "value": 76.0
    }
  ],
  "period": "daily"
}
```

### Gestión de Productos

#### GET `/api/v1/products/`
Lista productos

**Query Parameters:**
- `skip`: offset (default: 0)
- `limit`: límite (default: 100)
- `category_id`: filtrar por categoría

#### GET `/api/v1/products/categories`
Lista categorías disponibles

#### POST `/api/v1/products/categories`
Crear nueva categoría

**Body:**
```json
{
  "name": "Servicios Consulares",
  "description": "Servicios relacionados con documentos consulares"
}
```

#### PUT `/api/v1/products/{product_id}`
Actualizar producto

#### PUT `/api/v1/products/{product_id}/category/{category_id}`
Asignar producto a categoría

### Reportes

#### GET `/api/v1/reports/performance`
Reporte de performance

**Query Parameters:**
- `start_date`, `end_date`: rango de fechas
- `category_id`: filtrar por categoría
- `format`: "excel" o "csv" (default: "excel")

#### GET `/api/v1/reports/trends`
Reporte de tendencias

**Query Parameters:**
- `start_date`, `end_date`: rango de fechas
- `product_id`: producto específico
- `period`: "daily", "weekly", "monthly"
- `format`: "excel" o "csv"

#### GET `/api/v1/reports/categories`
Reporte por categorías

#### GET `/api/v1/reports/complete`
Reporte completo (múltiples hojas Excel)

---

## 📄 Formatos de Archivos Soportados

### Archivo Excel Estándar

**Columnas esperadas (flexible):**
```
| Columna Original    | Mapeo Interno        | Descripción              |
|---------------------|---------------------|--------------------------|
| fecha/date          | production_date     | Fecha de producción      |
| producto/product    | product_name        | Nombre del producto      |
| codigo/code         | product_code        | Código único             |
| cantidad/quantity   | quantity_produced   | Cantidad producida       |
| vendido/sold        | quantity_sold       | Cantidad vendida         |
| ingresos/revenue    | revenue             | Ingresos generados       |
| costo/cost          | unit_cost           | Costo unitario           |
```

### Archivo Gubernamental (HTML/Excel)

**Columnas específicas detectadas:**
```
| Columna Original           | Mapeo Interno        | Ejemplo                    |
|----------------------------|---------------------|----------------------------|
| Servicio                   | product_name        | RCM - DURANGO - COPIAS...  |
| Concepto                   | product_category    | Servicios Consulares       |
| Articulo                   | product_description | ART. 22 Y 24 LFD          |
| No. de trámites           | quantity_produced   | 5                          |
| Importe recaudación       | revenue             | 95.0                       |
| Fecha recaudación         | production_date     | 22/05/2025                 |
| Derechos                   | unit_cost           | 19.0                       |
| Moneda                     | currency            | USD                        |
```

### Ejemplo de Archivo Procesado Correctamente

**mayo.xls** (446 registros):
- Servicios consulares mexicanos
- Múltiples estados (Durango, Morelos, DF, etc.)
- Fechas: Mayo 2025
- Montos en USD
- Diferentes tipos de actas (nacimiento, defunción)

---

## 📊 Análisis y Reportes

### Métricas Calculadas

#### Performance por Producto
- **Total Producido**: Suma de quantity_produced
- **Total Vendido**: Suma de quantity_sold  
- **Ingresos Totales**: Suma de revenue
- **Producción Promedio Diaria**: Promedio de quantity_produced
- **Tasa de Conversión**: (Total Vendido / Total Producido) × 100

#### Análisis Temporal
- **Tendencias Diarias**: Ingresos por día
- **Tendencias Semanales**: Ingresos por semana
- **Tendencias Mensuales**: Ingresos por mes
- **Patrones Estacionales**: Identificación automática

#### Análisis por Categoría
- **Distribución de Productos**: Cantidad por categoría
- **Participación en Ventas**: Porcentaje de ingresos
- **Performance Relativo**: Comparación entre categorías

### Tipos de Reportes

#### 1. Reporte de Performance
**Contenido:**
- Lista completa de productos
- Métricas de producción y ventas
- Análisis de rentabilidad
- Tasa de conversión

#### 2. Reporte de Tendencias
**Contenido:**
- Serie temporal de ingresos
- Identificación de picos y valles
- Análisis de crecimiento
- Patrones estacionales

#### 3. Reporte por Categorías
**Contenido:**
- Resumen por categoría de producto
- Participación en el mercado
- Análisis comparativo
- Oportunidades de mejora

#### 4. Reporte Completo
**Contenido:** (Múltiples hojas Excel)
- Hoja 1: Performance por Producto
- Hoja 2: Tendencias Diarias
- Hoja 3: Resumen por Categorías
- Hoja 4: Resumen General

### Visualizaciones Disponibles

#### Dashboard Principal
- 📈 Gráfico de tendencias temporales
- 🥧 Distribución por categorías
- 📊 Top productos por ingresos
- 🎯 KPIs principales

#### Análisis Detallado
- 📉 Series temporales interactivas
- 📋 Tablas de performance
- 🔍 Filtros dinámicos por fecha/categoría
- 📱 Exportación a múltiples formatos

---

## 🗄️ Base de Datos

### Modelo de Datos

#### Tabla: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME
);
```

#### Tabla: categories
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT NOW()
);
```

#### Tabla: products
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    code VARCHAR UNIQUE,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    unit_price FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT NOW()
);
```

#### Tabla: production_records
```sql
CREATE TABLE production_records (
    id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) NOT NULL,
    production_date DATE NOT NULL,
    quantity_produced INTEGER DEFAULT 0,
    quantity_sold INTEGER DEFAULT 0,
    revenue FLOAT DEFAULT 0.0,
    unit_cost FLOAT DEFAULT 0.0,
    notes TEXT,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME
);
```

#### Tabla: import_batches
```sql
CREATE TABLE import_batches (
    id INTEGER PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    records_imported INTEGER DEFAULT 0,
    import_date DATETIME DEFAULT NOW(),
    status VARCHAR DEFAULT 'pending',
    error_message TEXT,
    imported_by INTEGER REFERENCES users(id)
);
```

### Índices Recomendados

```sql
-- Performance
CREATE INDEX idx_production_date ON production_records(production_date);
CREATE INDEX idx_product_records ON production_records(product_id);
CREATE INDEX idx_product_category ON products(category_id);

-- Búsquedas
CREATE INDEX idx_product_name ON products(name);
CREATE INDEX idx_category_name ON categories(name);
```

### Migraciones con Alembic

```bash
# Generar migración
alembic revision --autogenerate -m "Add new column"

# Aplicar migraciones  
alembic upgrade head

# Ver historial
alembic history
```

---

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
**Síntoma:** `sqlalchemy.exc.OperationalError`
**Solución:**
```bash
# Verificar configuración en .env
DATABASE_URL=sqlite:///./production_analytics.db

# Para PostgreSQL, verificar que esté corriendo
sudo service postgresql start
```

#### 2. Error de Dependencias
**Síntoma:** `ModuleNotFoundError`
**Solución:**
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar versión de Python
python --version  # Debe ser 3.11+
```

#### 3. Error de Archivo No Soportado
**Síntoma:** `ValueError: No se pudo leer el archivo`
**Solución:**
- Verificar que el archivo esté en formato Excel (.xlsx, .xls) o HTML
- Comprobar que el archivo no esté corrupto
- Verificar permisos de lectura

#### 4. Error de Token JWT
**Síntoma:** `401 Unauthorized`
**Solución:**
```bash
# Generar nuevo token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
-d "username=tu_usuario&password=tu_password"

# Verificar que SECRET_KEY esté configurado
echo $SECRET_KEY
```

#### 5. Error de Memoria con Archivos Grandes
**Síntoma:** `MemoryError` o procesamiento lento
**Solución:**
- Procesar archivos en lotes más pequeños
- Aumentar memoria virtual del sistema
- Considerar usar PostgreSQL en lugar de SQLite

### Logs y Debugging

#### Activar Logs Detallados
```python
# En backend/app/core/config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar Estado del Sistema
```bash
# Verificar conexión API
curl http://localhost:8000/

# Verificar base de datos
python -c "
from backend.app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    print(f'Usuarios: {result.scalar()}')
"
```

### Recuperación de Datos

#### Backup de Base de Datos
```bash
# SQLite
cp production_analytics.db production_analytics_backup.db

# PostgreSQL
pg_dump production_analytics > backup.sql
```

#### Restauración
```bash
# SQLite
cp production_analytics_backup.db production_analytics.db

# PostgreSQL
psql production_analytics < backup.sql
```

---

## 🚀 Desarrollo y Extensión

### Estructura para Nuevas Funcionalidades

#### Agregar Nueva API
1. **Crear endpoint** en `backend/app/api/`
2. **Agregar modelo** en `backend/app/models/` (si necesario)
3. **Implementar lógica** en `backend/app/services/`
4. **Registrar router** en `backend/app/main.py`

#### Ejemplo: Nueva API de Alertas
```python
# backend/app/api/alerts.py
from fastapi import APIRouter, Depends
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/low-performance")
async def get_low_performance_products(
    current_user = Depends(get_current_user)
):
    # Lógica para detectar productos con bajo rendimiento
    pass
```

#### Agregar Nuevo Tipo de Análisis
```python
# backend/app/services/advanced_analytics.py
class AdvancedAnalytics:
    def __init__(self, db: Session):
        self.db = db
    
    def predict_future_sales(self, product_id: int):
        # Implementar predicción con machine learning
        pass
    
    def detect_anomalies(self):
        # Detectar anomalías en los datos
        pass
```

### Testing

#### Configurar Entorno de Pruebas
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from backend.app.core.database import get_db

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///test.db")
    # Setup test database
    yield
    # Cleanup
```

#### Ejecutar Pruebas
```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=backend/app
```

### Deployment

#### Configuración Nginx
```nginx
# /etc/nginx/sites-available/analytics
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Systemd Service
```ini
# /etc/systemd/system/analytics.service
[Unit]
Description=Analytics API
After=network.target

[Service]
Type=simple
User=analytics
WorkingDirectory=/opt/analytics
ExecStart=/opt/analytics/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/analytics
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=analytics
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Monitoreo y Observabilidad

#### Métricas con Prometheus
```python
# backend/app/monitoring.py
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

def track_request(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        REQUEST_LATENCY.observe(time.time() - start_time)
        return result
    return wrapper
```

#### Health Check
```python
# backend/app/health.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": "connected" if check_db() else "disconnected"
    }
```

---

## 📞 Soporte y Contribución

### Reportar Problemas
1. **Verificar** que no esté ya reportado en issues
2. **Incluir** información detallada:
   - Versión del sistema
   - Pasos para reproducir
   - Logs de error
   - Archivo de ejemplo (si aplica)

### Contribuir al Proyecto
1. **Fork** del repositorio
2. **Crear** branch para nueva funcionalidad
3. **Implementar** cambios con tests
4. **Enviar** pull request con descripción detallada

### Roadmap Futuro
- [ ] 🎨 Interfaz web React
- [ ] 🤖 Predicciones con ML
- [ ] 📱 Aplicación móvil
- [ ] 🔔 Sistema de alertas
- [ ] 📊 Dashboards personalizables
- [ ] 🔗 Integración con ERPs
- [ ] 🌐 Soporte multi-idioma
- [ ] 📈 Analytics en tiempo real

---

## 📄 Licencia y Términos

### Uso del Sistema
Este sistema está diseñado específicamente para oficinas gubernamentales y análisis de datos de producción/recaudación oficial.

### Seguridad
- Cambiar `SECRET_KEY` en producción
- Usar HTTPS en producción
- Implementar backup regulares
- Monitorear accesos y logs

### Mantenimiento
- Actualizar dependencias regularmente
- Monitorear performance de base de datos
- Limpiar archivos temporales
- Revisar logs de errores

---

*Documentación generada para el Sistema de Análisis de Producción y Recaudación v1.0*
*Última actualización: 8 de Agosto, 2025*