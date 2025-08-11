# 🚀 Guía de Inicio Rápido

## Sistema de Análisis de Producción y Recaudación

---

## ⚡ Inicio en 5 Minutos

### 1. Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
cp .env.example .env
```

### 2. Ejecutar
```bash
python run.py
```

### 3. Acceder
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

---

## 📝 Primer Uso

### 1. Crear Usuario
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "admin",
  "email": "admin@oficina.gob.mx", 
  "full_name": "Administrador",
  "password": "password123"
}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=admin&password=password123"
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 3. Subir Archivo
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer <tu-token>" \
-F "file=@mayo.xls"
```

### 4. Ver Dashboard
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary" \
-H "Authorization: Bearer <tu-token>"
```

---

## 📊 Ejemplo con Datos Reales

### Archivo de Prueba: mayo.xls
✅ **446 registros procesados**
- Servicios consulares mexicanos
- Diferentes estados (Durango, Morelos, DF, etc.)
- Período: Mayo 2025
- Ingresos: $7,752 USD

### Resultados Obtenidos:
- 📈 **60 productos únicos** identificados
- 💰 **91.48% tasa de conversión**
- 🏷️ **Categorización automática**
- 📅 **Análisis temporal por día**

---

## 🔧 Comandos Útiles

### Ver Estado del Sistema
```bash
# Verificar API
curl http://localhost:8000/

# Listar importaciones
curl -H "Authorization: Bearer <token>" \
http://localhost:8000/api/v1/files/batches
```

### Generar Reportes
```bash
# Reporte completo Excel
curl -X GET "http://localhost:8000/api/v1/reports/complete" \
-H "Authorization: Bearer <token>" \
-o "reporte.xlsx"

# Reporte CSV por categorías  
curl -X GET "http://localhost:8000/api/v1/reports/categories?format=csv" \
-H "Authorization: Bearer <token>" \
-o "categorias.csv"
```

---

## 📋 Formatos de Archivo Soportados

### Excel/CSV Estándar
```
| fecha      | producto    | cantidad | vendido | ingresos |
|------------|-------------|----------|---------|----------|
| 2025-05-01 | Servicio A  | 10       | 8       | 160.00   |
```

### Formato Gubernamental (Detectado Automáticamente)
```
| Servicio           | No. trámites | Importe recaudación | Fecha recaudación |
|--------------------|--------------|---------------------|-------------------|
| RCM - DURANGO...   | 5            | 95.0                | 22/05/2025        |
```

---

## ❗ Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Database connection failed"
```bash
# Verificar .env
DATABASE_URL=sqlite:///./production_analytics.db
```

### Error: "File format not supported"
- Verificar que sea .xlsx, .xls o .html
- Comprobar que el archivo no esté corrupto

### Error: "Unauthorized"
```bash
# Generar nuevo token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
-d "username=tu_usuario&password=tu_password"
```

---

## 📚 Próximos Pasos

1. **📖 Leer documentación completa**: `DOCUMENTACION.md`
2. **🔍 Explorar APIs**: http://localhost:8000/docs
3. **📊 Personalizar categorías**: Usar endpoints de productos
4. **📈 Configurar reportes automáticos**
5. **🏭 Configurar para producción**: PostgreSQL + HTTPS

---

## 🎯 Casos de Uso Principales

### 🏛️ Oficina Consular
- Análisis de trámites por estado
- Seguimiento de ingresos consulares  
- Reportes mensuales automáticos

### 📊 Análisis General
- Identificar productos más rentables
- Detectar tendencias temporales
- Optimizar producción basada en demanda

### 📋 Reportería
- Exportación a Excel para directivos
- Dashboards para personal operativo
- Métricas KPI automatizadas

---

*¡Listo para empezar! 🚀*

Para soporte técnico detallado, consulta `DOCUMENTACION.md`