# Reporte Mensual de Expedición de Documentos

## Descripción

Módulo del Dashboard Consular que genera reportes mensuales detallados de expedición de servicios con análisis comparativos.

## Características

### 📊 Funcionalidades Principales

1. **Tabla de Servicios del Mes**
   - Nombre del servicio
   - Cantidad de servicios expedidos
   - Total recaudado
   - Ingreso promedio por trámite

2. **Comparativa con Períodos Anteriores**
   - Comparación con mes anterior
   - Comparación con mismo mes del año anterior
   - Porcentajes de incremento/decremento
   - Indicadores visuales (↑ ↓)

3. **Gráficas Interactivas**
   - **Top 10 Servicios**: Barras horizontales por ingresos
   - **Comparación Temporal**: Barras agrupadas comparando 3 períodos
   - **Evolución de Servicio**: Gráfica de línea de últimos 12 meses

4. **Exportación a PDF**
   - Reporte completo con todas las tablas
   - Gráficas embebidas en alta calidad
   - Formato profesional con branding

## Uso

### Acceso al Módulo

1. Iniciar el dashboard: `streamlit run dashboard_enhanced.py`
2. En el menú lateral, hacer clic en **"Reporte Mensual"**

### Generar un Reporte

1. **Seleccionar período**:
   - Elegir el mes (dropdown)
   - Elegir el año (dropdown)

2. **Hacer clic en "🔍 Generar Reporte"**

3. **Revisar el reporte**:
   - KPIs generales del mes
   - Tabla de servicios expedidos
   - Tabla comparativa con períodos anteriores
   - Gráficas interactivas

4. **Exportar a PDF** (opcional):
   - Hacer clic en "📥 Generar y Descargar PDF"
   - El PDF se descargará automáticamente

## Estructura del Reporte

### Sección 1: KPIs Generales
- 💰 Ingresos Totales
- 📝 Trámites Realizados
- 🏷️ Servicios Activos
- 💵 Ingreso Promedio por Trámite

### Sección 2: Tabla de Servicios
Columnas:
- Servicio
- Cantidad
- Ingresos Totales
- Ingreso Promedio

### Sección 3: Tabla Comparativa
Columnas:
- Servicio
- Ingresos Mes Actual
- Ingresos Mes Anterior
- % Cambio vs Mes Anterior
- Ingresos Mismo Mes Año Anterior
- % Cambio vs Año Anterior

### Sección 4: Gráficas

#### Gráfica 1: Top 10 Servicios
- Tipo: Barras horizontales
- Métrica: Ingresos totales
- Ordenado: De mayor a menor

#### Gráfica 2: Comparación entre Períodos
- Tipo: Barras agrupadas
- Períodos comparados:
  - Mes actual
  - Mes anterior
  - Mismo mes año anterior
- Top 5 servicios

#### Gráfica 3: Evolución Temporal
- Tipo: Línea dual (ingresos + trámites)
- Período: Últimos 12 meses
- Servicio: Seleccionable por el usuario

## Archivos del Módulo

### `monthly_report_page.py`
Archivo principal con toda la funcionalidad:

**Funciones principales:**
- `show_monthly_report_page()`: Página principal
- `generate_monthly_report()`: Genera datos del reporte
- `display_monthly_report()`: Muestra el reporte completo
- `show_comparative_table()`: Tabla con comparativas
- `create_monthly_pdf_report()`: Genera el PDF

### Integración en `dashboard_enhanced.py`

Cambios realizados:
1. **Línea 11**: Importación del módulo
   ```python
   from monthly_report_page import show_monthly_report_page
   ```

2. **Líneas 216-218**: Botón en sidebar
   ```python
   if st.sidebar.button("Reporte Mensual", ...):
       st.session_state.current_page = "Reporte Mensual"
       st.rerun()
   ```

3. **Líneas 252-253**: Case para mostrar página
   ```python
   elif page == "Reporte Mensual":
       show_monthly_report_page()
   ```

## Requisitos Técnicos

### Dependencias
Todas ya instaladas en el proyecto:
- ✅ `streamlit >= 1.25.0`
- ✅ `pandas >= 1.5.0`
- ✅ `plotly >= 5.15.0`
- ✅ `reportlab >= 4.4.0`
- ✅ `kaleido >= 1.0.0`

### Base de Datos
- Requiere datos cargados en `consular_data.db`
- Tabla: `consular_data`
- Columnas necesarias:
  - `servicio`
  - `num_tramites`
  - `ingresos_totales`
  - `fecha_emision`

## Ejemplos de Uso

### Caso 1: Reporte Mensual Estándar
```
1. Seleccionar: Mayo 2024
2. Generar Reporte
3. Revisar datos y gráficas
4. Exportar a PDF
```

### Caso 2: Análisis de Tendencia de Servicio Específico
```
1. Seleccionar: Cualquier mes
2. Generar Reporte
3. En "Evolución Temporal", seleccionar servicio (ej: "Pasaportes Ordinarios")
4. Analizar tendencia de últimos 12 meses
```

### Caso 3: Comparación con Año Anterior
```
1. Seleccionar: Mayo 2024
2. Generar Reporte
3. Ir a "Tabla Comparativa"
4. Revisar columna "% Cambio Año" para ver crecimiento/decremento
```

## Interpretación de Resultados

### Indicadores de Cambio Porcentual

- **↑ Verde (Positivo)**: Incremento respecto al período anterior
  - Ejemplo: `+15.3% ↑` = 15.3% más que el período de comparación

- **↓ Rojo (Negativo)**: Decremento respecto al período anterior
  - Ejemplo: `-8.2% ↓` = 8.2% menos que el período de comparación

- **→ Gris (Neutro)**: Sin cambio
  - Ejemplo: `0.0% →` = Mismo valor

- **N/A**: No hay datos para comparar
  - El servicio no existía en el período anterior

## Formato del PDF

### Estructura del Documento
1. Portada con título y fecha
2. Resumen ejecutivo (tabla KPIs)
3. Tabla de servicios expedidos (top 15)
4. Análisis comparativo (top 10)
5. Gráficas en páginas separadas

### Nombre del Archivo
Formato: `reporte_mensual_MM_YYYY_YYYYMMDD_HHMM.pdf`

Ejemplo: `reporte_mensual_05_2024_20241017_1430.pdf`
- Mes: 05 (Mayo)
- Año: 2024
- Fecha generación: 17/10/2024 14:30

## Solución de Problemas

### Error: "No se encontraron datos para [Mes] [Año]"
**Causa**: No hay registros en la base de datos para ese período
**Solución**:
1. Verificar que los datos estén cargados en "Gestión de Archivos"
2. Seleccionar un mes/año diferente con datos disponibles

### Error al generar PDF
**Causa**: Problema con kaleido o archivos temporales
**Solución**:
1. Verificar que kaleido esté instalado: `pip list | grep kaleido`
2. Verificar permisos de escritura en directorio temporal
3. Reiniciar el dashboard

### Gráficas no se muestran
**Causa**: Datos insuficientes para el servicio seleccionado
**Solución**:
1. Seleccionar un servicio con más historial
2. Verificar que haya datos de al menos 2-3 meses

## Mejoras Futuras (Opcionales)

- [ ] Filtro por categoría de servicios
- [ ] Exportación a Excel
- [ ] Comparación de múltiples meses simultáneamente
- [ ] Envío automático por email
- [ ] Programación de reportes recurrentes
- [ ] Benchmark con otras oficinas consulares

## Soporte

Para problemas o dudas:
1. Revisar esta documentación
2. Verificar que todas las dependencias estén instaladas
3. Consultar logs del dashboard en la terminal

---

**Versión**: 1.0
**Fecha**: Octubre 2024
**Autor**: Dashboard Consular - Análisis Histórico
