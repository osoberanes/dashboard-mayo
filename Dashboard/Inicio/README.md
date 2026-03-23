# Dashboard de Análisis Mayo.xls

Dashboard interactivo para visualizar y analizar los datos del archivo `mayo.xls` con métricas de trámites, ingresos y formas canceladas.

## Características

### 📊 KPIs Principales
- **Ingresos Totales**: Suma de todos los ingresos (columna F)
- **Trámites Realizados**: Total de trámites procesados (columna E)
- **Formas Canceladas**: Número de formas canceladas en emisión (columna M)
- **Costo Promedio**: Promedio del costo unitario de trámites

### 🔍 Filtros Dinámicos
- **Rango de fechas**: Filtrar por periodo específico
- **Categorías**: Selección múltiple de categorías de servicios
- **Servicios**: Filtrado por servicios específicos (jerarquía: Categoría → Servicio)

### 📈 Visualizaciones
1. **Series Temporales**: Análisis por día, mes o año
2. **Por Categoría**: Gráficos de barras y distribución tipo pastel
3. **Por Servicio**: Top 20 servicios con drill-down por categoría
4. **Datos Detallados**: Tablas con diferentes niveles de agrupación

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Asegurarse de que `mayo.xls` esté en el mismo directorio

## Uso

Ejecutar el dashboard:
```bash
streamlit run dashboard_mayo.py
```

El dashboard se abrirá en `http://localhost:8501`

## Estructura de Datos Esperada

El archivo `mayo.xls` debe tener la siguiente estructura:

- **Columna A**: Servicios otorgados
- **Columna C**: Categorías de servicios  
- **Columna D**: Costo unitario por trámite
- **Columna E**: Número de trámites realizados
- **Columna F**: Ingresos totales (D × E)
- **Columna J**: Fecha de emisión (formato DD/MM/AAAA)
- **Columna M**: Formas canceladas durante la emisión

## Archivos

- `dashboard_mayo.py`: Dashboard principal con interfaz Streamlit
- `data_processor.py`: Clase para procesamiento y limpieza de datos
- `requirements.txt`: Dependencias de Python necesarias

## Funcionalidades Avanzadas

- **Caché de datos**: Los datos se cargan una sola vez para mejor rendimiento
- **Exportación**: Descarga de datos filtrados en formato CSV
- **Responsive**: Interfaz adaptable a diferentes tamaños de pantalla
- **Manejo de errores**: Validación y limpieza automática de datos

## Estado del Proyecto (Última sesión)

✅ **COMPLETADO** - Dashboard funcionando correctamente
- Archivo mayo.xls es formato HTML (no Excel real)
- Dependencia lxml instalada
- Mapeo de columnas corregido: usar 'Articulo' como 'categoria'
- 446 filas de datos procesadas exitosamente
- 5 categorías y 60 servicios disponibles
- KPIs: $251,880 ingresos, 5,375 trámites, 75 canceladas

### Comandos Rápidos
```powershell
# Ejecutar desde raíz del proyecto
.\run_dashboard.bat

# O manualmente
.\.venv\Scripts\streamlit run Inicio\dashboard_mayo.py
```