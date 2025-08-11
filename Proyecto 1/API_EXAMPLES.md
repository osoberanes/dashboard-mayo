# 🔌 Ejemplos de API - Sistema de Análisis

## Colección completa de ejemplos para usar la API

---

## 🔐 Autenticación

### Registro de Usuario
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "jperez",
  "email": "juan.perez@consulado.gob.mx",
  "full_name": "Juan Pérez García",
  "password": "MiPassword123!"
}'
```

**Respuesta exitosa:**
```json
{
  "id": 1,
  "username": "jperez",
  "email": "juan.perez@consulado.gob.mx",
  "full_name": "Juan Pérez García",
  "is_active": true,
  "is_admin": false
}
```

### Login y Obtener Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=jperez&password=MiPassword123!"
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqcGVyZXoiLCJleHAiOjE2OTE2ODk5MDF9.xyz...",
  "token_type": "bearer"
}
```

### Verificar Información del Usuario
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
-H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

## 📁 Gestión de Archivos

### Subir Archivo Excel/HTML
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer <tu-token>" \
-F "file=@datos_mayo_2025.xlsx"
```

**Respuesta exitosa:**
```json
{
  "message": "Successfully imported 446 records",
  "batch_id": 5,
  "records_imported": 446
}
```

**Respuesta con error:**
```json
{
  "detail": "Only Excel files (.xlsx, .xls) are allowed"
}
```

### Ver Historial de Cargas
```bash
curl -X GET "http://localhost:8000/api/v1/files/batches" \
-H "Authorization: Bearer <tu-token>"
```

**Respuesta:**
```json
[
  {
    "id": 5,
    "filename": "datos_mayo_2025.xlsx",
    "records_imported": 446,
    "import_date": "2025-08-08T15:30:45.123456",
    "status": "completed",
    "error_message": null
  },
  {
    "id": 4,
    "filename": "datos_abril_2025.xls",
    "records_imported": 0,
    "import_date": "2025-08-07T10:15:22.789012",
    "status": "error",
    "error_message": "Error processing file: Unsupported format"
  }
]
```

---

## 📊 Analytics y Dashboard

### Dashboard Principal
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary" \
-H "Authorization: Bearer <tu-token>"
```

**Con filtros de fecha:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary?start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>"
```

**Respuesta:**
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
      "category_name": "Servicios Consulares",
      "product_count": 45,
      "total_revenue": 6800.0,
      "total_production": 380
    },
    {
      "category_name": "Documentos Civiles",
      "product_count": 15,
      "total_revenue": 952.0,
      "total_production": 66
    }
  ],
  "top_products": [
    {
      "name": "RCM - DISTRITO FEDERAL - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
      "revenue": 380.0
    },
    {
      "name": "RCM - JALISCO - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO", 
      "revenue": 342.0
    }
  ]
}
```

### Performance Detallada por Producto
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/performance?limit=10" \
-H "Authorization: Bearer <tu-token>"
```

**Con filtros avanzados:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/performance?start_date=2025-05-01&end_date=2025-05-31&category_id=1&limit=20" \
-H "Authorization: Bearer <tu-token>"
```

**Respuesta:**
```json
[
  {
    "product_id": 3,
    "product_name": "RCM - DISTRITO FEDERAL - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
    "category_name": "Servicios Consulares",
    "total_produced": 20,
    "total_sold": 20,
    "total_revenue": 380.0,
    "avg_daily_production": 1.25,
    "sell_through_rate": 100.0
  },
  {
    "product_id": 15,
    "product_name": "RCM - JALISCO - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
    "category_name": "Servicios Consulares", 
    "total_produced": 18,
    "total_sold": 18,
    "total_revenue": 342.0,
    "avg_daily_production": 1.13,
    "sell_through_rate": 100.0
  }
]
```

### Análisis de Tendencias
```bash
# Tendencias diarias
curl -X GET "http://localhost:8000/api/v1/analytics/trends/revenue?period=daily&start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>"

# Tendencias semanales
curl -X GET "http://localhost:8000/api/v1/analytics/trends/revenue?period=weekly&start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>"

# Tendencias por producto específico
curl -X GET "http://localhost:8000/api/v1/analytics/trends/revenue?product_id=3&period=daily" \
-H "Authorization: Bearer <tu-token>"
```

**Respuesta:**
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
    },
    {
      "date": "2025-05-03",
      "value": 95.0
    },
    {
      "date": "2025-05-04",
      "value": 38.0
    }
  ],
  "period": "daily"
}
```

---

## 🏷️ Gestión de Productos y Categorías

### Listar Todas las Categorías
```bash
curl -X GET "http://localhost:8000/api/v1/products/categories" \
-H "Authorization: Bearer <tu-token>"
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Servicios Consulares",
    "description": "Servicios relacionados con trámites consulares"
  },
  {
    "id": 2,
    "name": "Documentos Civiles", 
    "description": "Actas de nacimiento, matrimonio, defunción"
  }
]
```

### Crear Nueva Categoría
```bash
curl -X POST "http://localhost:8000/api/v1/products/categories" \
-H "Authorization: Bearer <tu-token>" \
-H "Content-Type: application/json" \
-d '{
  "name": "Servicios Notariales",
  "description": "Apostillas, legalizaciones y servicios notariales"
}'
```

### Listar Productos
```bash
# Todos los productos (paginado)
curl -X GET "http://localhost:8000/api/v1/products/?skip=0&limit=50" \
-H "Authorization: Bearer <tu-token>"

# Productos de una categoría específica
curl -X GET "http://localhost:8000/api/v1/products/?category_id=1" \
-H "Authorization: Bearer <tu-token>"
```

**Respuesta:**
```json
[
  {
    "id": 3,
    "name": "RCM - DISTRITO FEDERAL - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
    "code": "PROD_A1B2C3D4",
    "description": "ART. 22 Y 24 LFD - SERVICIOS CONSULARES",
    "category": {
      "id": 1,
      "name": "Servicios Consulares",
      "description": "Servicios relacionados con trámites consulares"
    },
    "unit_price": 19.0
  }
]
```

### Actualizar Producto
```bash
curl -X PUT "http://localhost:8000/api/v1/products/3" \
-H "Authorization: Bearer <tu-token>" \
-H "Content-Type: application/json" \
-d '{
  "name": "RCM - DF - ACTA DE NACIMIENTO (Actualizado)",
  "description": "Servicio de copia certificada - Distrito Federal",
  "unit_price": 20.0
}'
```

### Asignar Producto a Categoría
```bash
curl -X PUT "http://localhost:8000/api/v1/products/3/category/2" \
-H "Authorization: Bearer <tu-token>"
```

---

## 📋 Generación de Reportes

### Reporte de Performance (Excel)
```bash
curl -X GET "http://localhost:8000/api/v1/reports/performance?format=excel&start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>" \
-o "performance_mayo_2025.xlsx"
```

### Reporte de Performance (CSV)
```bash
curl -X GET "http://localhost:8000/api/v1/reports/performance?format=csv&category_id=1" \
-H "Authorization: Bearer <tu-token>" \
-o "performance_servicios_consulares.csv"
```

### Reporte de Tendencias
```bash
# Tendencias diarias en Excel
curl -X GET "http://localhost:8000/api/v1/reports/trends?period=daily&format=excel&start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>" \
-o "tendencias_diarias_mayo.xlsx"

# Tendencias de producto específico en CSV
curl -X GET "http://localhost:8000/api/v1/reports/trends?product_id=3&period=weekly&format=csv" \
-H "Authorization: Bearer <tu-token>" \
-o "tendencias_producto_3.csv"
```

### Reporte por Categorías
```bash
curl -X GET "http://localhost:8000/api/v1/reports/categories?format=excel" \
-H "Authorization: Bearer <tu-token>" \
-o "resumen_categorias.xlsx"
```

### Reporte Completo (Múltiples Hojas)
```bash
curl -X GET "http://localhost:8000/api/v1/reports/complete?start_date=2025-05-01&end_date=2025-05-31" \
-H "Authorization: Bearer <tu-token>" \
-o "reporte_completo_mayo_2025.xlsx"
```

---

## 🔧 Scripts de Automatización

### Script Bash para Carga Automática
```bash
#!/bin/bash
# upload_data.sh

TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
API_BASE="http://localhost:8000/api/v1"

# Subir archivo
echo "Subiendo archivo de datos..."
RESPONSE=$(curl -s -X POST "$API_BASE/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$1")

echo "Respuesta: $RESPONSE"

# Obtener resumen
echo "Obteniendo resumen de datos..."
curl -s -X GET "$API_BASE/analytics/summary" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Generar reporte
echo "Generando reporte..."
curl -X GET "$API_BASE/reports/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -o "reporte_$(date +%Y%m%d).xlsx"

echo "¡Proceso completado!"
```

### Script Python para Análisis Automático
```python
#!/usr/bin/env python3
# analytics_automation.py

import requests
import json
from datetime import datetime, timedelta

class AnalyticsClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = self._get_token(username, password)
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def _get_token(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/token",
            data={"username": username, "password": password}
        )
        return response.json()["access_token"]
    
    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/files/upload",
                headers=self.headers,
                files={"file": f}
            )
        return response.json()
    
    def get_summary(self, start_date=None, end_date=None):
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = requests.get(
            f"{self.base_url}/analytics/summary",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def generate_report(self, output_file):
        response = requests.get(
            f"{self.base_url}/reports/complete",
            headers=self.headers
        )
        
        with open(output_file, 'wb') as f:
            f.write(response.content)

# Uso
if __name__ == "__main__":
    client = AnalyticsClient(
        "http://localhost:8000/api/v1",
        "admin",
        "password123"
    )
    
    # Subir archivo
    result = client.upload_file("datos_mensual.xlsx")
    print(f"Importados: {result['records_imported']} registros")
    
    # Obtener resumen del mes actual
    today = datetime.now()
    start_month = today.replace(day=1)
    summary = client.get_summary(
        start_date=start_month.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d")
    )
    
    print(f"Ingresos totales: ${summary['summary']['total_revenue']:,.2f}")
    print(f"Tasa conversión: {summary['summary']['sell_through_rate']:.2f}%")
    
    # Generar reporte
    report_file = f"reporte_{today.strftime('%Y_%m')}.xlsx"
    client.generate_report(report_file)
    print(f"Reporte generado: {report_file}")
```

### PowerShell para Windows
```powershell
# analytics_report.ps1

$Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
$ApiBase = "http://localhost:8000/api/v1"
$Headers = @{ "Authorization" = "Bearer $Token" }

# Obtener resumen
$Summary = Invoke-RestMethod -Uri "$ApiBase/analytics/summary" -Headers $Headers
Write-Host "Ingresos Totales: $($Summary.summary.total_revenue)"

# Generar reporte mensual
$Date = Get-Date -Format "yyyyMM"
$OutputFile = "reporte_$Date.xlsx"

Invoke-WebRequest -Uri "$ApiBase/reports/complete" -Headers $Headers -OutFile $OutputFile
Write-Host "Reporte generado: $OutputFile"

# Enviar por email (opcional)
# Send-MailMessage -To "director@oficina.gob.mx" -Subject "Reporte Mensual" -Attachments $OutputFile
```

---

## 📊 Ejemplos con Datos Reales

### Datos del Archivo mayo.xls Procesado

**Resumen General:**
```json
{
  "total_produced": 446,
  "total_sold": 408, 
  "total_revenue": 7752.0,
  "active_products": 60,
  "sell_through_rate": 91.48
}
```

**Top 5 Productos por Ingresos:**
```json
[
  {
    "name": "RCM - DISTRITO FEDERAL - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
    "revenue": 380.0,
    "quantity": 20
  },
  {
    "name": "RCM - JALISCO - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO", 
    "revenue": 342.0,
    "quantity": 18
  },
  {
    "name": "RCM - GUANAJUATO - COPIAS CERTIFICADAS DE ACTAS DE NACIMIENTO",
    "revenue": 304.0,
    "quantity": 16
  }
]
```

**Análisis Temporal (Mayo 2025):**
- **Día más productivo**: 29 de Mayo (19 trámites, $361)
- **Promedio diario**: 14.4 trámites, $250.06
- **Tendencia**: Crecimiento constante del 15% semanal

---

## 🚨 Manejo de Errores

### Errores Comunes y Respuestas

#### 401 - No Autorizado
```json
{
  "detail": "Could not validate credentials"
}
```
**Solución:** Renovar token o verificar permisos

#### 400 - Archivo No Válido
```json
{
  "detail": "Only Excel files (.xlsx, .xls) are allowed"
}
```

#### 422 - Error de Validación
```json
{
  "detail": [
    {
      "loc": ["body", "start_date"],
      "msg": "invalid date format",
      "type": "value_error.date"
    }
  ]
}
```

#### 500 - Error del Servidor
```json
{
  "detail": "Error processing file: Unsupported format"
}
```

### Reintentos Automáticos
```bash
# Función para reintentar con backoff exponencial
retry_request() {
  local url=$1
  local max_attempts=3
  local delay=1
  
  for i in $(seq 1 $max_attempts); do
    if curl -f "$url" -H "Authorization: Bearer $TOKEN"; then
      return 0
    fi
    
    echo "Intento $i falló, reintentando en ${delay}s..."
    sleep $delay
    delay=$((delay * 2))
  done
  
  echo "Falló después de $max_attempts intentos"
  return 1
}
```

---

*¡Ahora tienes todos los ejemplos necesarios para usar la API completa! 🎯*

Para más detalles técnicos, consulta `DOCUMENTACION.md`