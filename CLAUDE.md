# Proyecto Dashboard Mayo - Información de Sesión

## Resumen del Proyecto
Dashboard interactivo de análisis de datos consulares mexicanos usando Streamlit y Plotly para visualizar información de trámites, ingresos y servicios consulares.

## Estado Actual ✅ COMPLETADO - Sesión 13 Agosto 2025 🆕 ACTUALIZADO
- **Dashboard MEJORADO** funcionando en `http://localhost:8503` / `http://localhost:8506`
- **Dashboard original** funcionando en `http://localhost:8501`
- **Base de datos SQLite** implementada para gestión histórica
- **Gestión de archivos** múltiples con validación automática
- **Análisis histórico** y comparativo entre períodos
- **Sistema de carga** con detección de duplicados
- **Exportación avanzada** (CSV/Excel) con filtros
- **🔧 Agrupación de Servicios** - Consolida RCM y PASAPORTES ORDINARIOS
- **Análisis de agrupaciones** con visualizaciones detalladas
- **Aplicación permanente** de cambios a base de datos
- **🆕 NUEVA: Comparación Consolidada** - Todos los períodos en una sola gráfica
- **UI mejorada** con navegación por botones individuales
- **Controles temporales** (diario/mensual/anual) en todas las gráficas
- **KPIs optimizados** con promedios diarios y desviación estándar

## Estructura de Archivos ACTUALIZADA
```
C:\Users\consuladscrito\claudecode\
├── Inicio/
│   ├── dashboard_mayo.py         # Dashboard original (Streamlit)
│   ├── dashboard_enhanced.py     # Dashboard MEJORADO con BD
│   ├── data_processor.py         # Procesador original
│   ├── enhanced_data_processor.py # Procesador con BD
│   ├── database_manager.py       # Gestor de base de datos SQLite
│   ├── file_manager.py          # Gestor de carga de archivos
│   ├── file_upload_page.py      # Página de gestión de archivos
│   ├── consular_data.db         # Base de datos SQLite (creada automáticamente)
│   ├── mayo.xls                 # Archivo HTML original
│   └── requirements.txt         # Dependencias
├── period_comparison_page.py    # Página comparación de períodos ACTUALIZADA
├── service_grouping_page.py     # Página agrupación de servicios
├── robust_data_processor.py     # Procesador robusto de datos
├── run_dashboard.bat            # Script dashboard original
├── run_enhanced_dashboard.bat   # Script dashboard MEJORADO
└── .venv/                      # Entorno virtual Python
```

## Problemas Resueltos
1. **Error de importación relativa** → Corregido path
2. **Falta dependencia lxml** → Instalada con pip
3. **Archivo .xls es HTML** → Soporte con `pd.read_html()`
4. **Mapeo de columnas incorrecto** → Cambiado 'Concepto' → 'Articulo'
5. **Filtros sin datos** → Categorías ahora disponibles

## Comandos para Ejecutar
### Dashboard MEJORADO (Puerto 8503) - RECOMENDADO ✅
```powershell
# Opción 1: Script batch (NUEVO)
.\run_enhanced_dashboard.bat

# Opción 2: Streamlit directo
.\.venv\Scripts\streamlit run Inicio\dashboard_enhanced.py --server.port=8503
```

### Dashboard Original (Puerto 8501) - Mantenido
```powershell
# Opción 1: Script batch original
.\run_dashboard.bat

# Opción 2: Streamlit directo
.\.venv\Scripts\streamlit run Inicio\dashboard_mayo.py
```

### URLs de Acceso
- **Dashboard Mejorado**: http://localhost:8503 / http://localhost:8506 ⭐
- **Dashboard Original**: http://localhost:8501

## Dependencias Instaladas
- pandas>=1.5.0
- openpyxl>=3.1.0
- streamlit>=1.25.0
- plotly>=5.15.0
- xlrd>=2.0.0
- lxml>=4.9.0

## Datos del Archivo mayo.xls
- **Formato**: HTML disfrazado como .xls
- **Contenido**: Servicios consulares mexicanos Mayo 2025
- **Columnas principales**: Servicio, Articulo, Derechos, No. trámites, Importe USD, Fecha recaudación
- **Categorías**: Pasaportes E/G, Servicios Consulares, Notariales, etc.

## Funcionalidades del Dashboard MEJORADO
### 📈 Análisis de Datos (Página Principal) 🆕 ACTUALIZADA
- 📊 **KPIs optimizados** con promedio diario de ingresos y desviación estándar
- 📈 **Controles temporales** en todas las gráficas (diario/mensual/anual)
- 📊 Análisis comparativo por categoría con navegación mejorada
- 🔍 Top servicios con múltiples criterios y diseño optimizado
- ⚡ Análisis de eficiencia y tasas con UI rediseñada
- 🎛️ Filtros avanzados por fecha y categoría
- 📋 Exportación CSV/Excel con filtros
- 🖱️ **Navegación por botones** individuales (sin dropdown)

### 📁 Gestión de Archivos (Nueva Página)
- 🔍 **Búsqueda automática** de archivos (.xls/.xlsx/.html)
- 👁️ **Previsualización** y validación de archivos
- 📤 **Carga individual** con drag & drop
- 📤 **Carga en lote** de múltiples archivos
- 🚫 **Validación de duplicados** por fecha
- 📊 **Estado de la base de datos** en tiempo real
- 📁 **Historial de archivos** cargados
- 🗑️ **Eliminación selectiva** de datos por archivo

### 🔧 Agrupación de Servicios (🆕 NUEVA PÁGINA)
- **📊 Análisis de Agrupaciones**: Vista general de servicios agrupables
  - **RCM**: 53 servicios únicos → "RCM - Expedición Diaria" 
  - **PASAPORTES**: 8 servicios únicos → "Pasaportes Ordinarios"
  - **Estadísticas**: 591 + 424 = 1,015 registros agrupables
  
- **🔍 Desglose Detallado**: Análisis profundo por grupo
  - **Visualizaciones**: TreeMap, gráficos de pastel, análisis temporal
  - **Filtros temporales** y por criterios
  - **Métricas**: ingresos/trámite, tasas de cancelación
  
- **⚙️ Aplicar Cambios**: Modificación permanente de BD
  - **Vista previa** de cambios con confirmaciones
  - **Aplicación segura** con múltiples validaciones
  - **Backup recomendado** antes de aplicar
  
- **📈 Comparación**: Antes vs Después de agrupación
  - **Reducción de complejidad** en reportes
  - **Consolidación** de servicios similares

### 📊 Comparación de Períodos (🆕 COMPLETAMENTE REDISEÑADA)
- **🔍 Configuración flexible** de hasta 3 períodos simultáneos
- **📈 Gráfica consolidada** - Todos los períodos en la misma visualización
- **🎨 Código de colores** diferenciado por período (azul, naranja, verde)
- **🕒 Controles temporales** independientes (diario/mensual/trimestral/anual)
- **📊 KPIs comparativos** - Solo métricas esenciales (sin servicios únicos)
- **📋 Tabla de estadísticas** con variación porcentual vs período base
- **💾 Persistencia de datos** - No se borran al cambiar controles
- **🎛️ Interactividad mejorada** con leyendas clickeables y hover detallado

### ⚙️ Configuración (Nueva Página)
- 💾 **Backup de base de datos** automático
- 📊 **Información del sistema** y estadísticas
- 🔧 **Mantenimiento** y limpieza de cache
- 📥 **Exportación masiva** con filtros de fecha

## Mapeo de Columnas HTML → Dashboard
```python
'Servicio' → 'servicio'
'Articulo' → 'categoria'  # Clave: usar Articulo, no Concepto
'Derechos' → 'costo_unitario'
'No. de trámites' → 'num_tramites'
'Importe USD' → 'ingresos_totales'
'Fecha recaudación' → 'fecha_emision'
'No. cancelados' → 'formas_canceladas'
```

## Historial de Problemas Resueltos (Cronológico)

### Problema 1: Error de ejecución inicial
- **Error**: `ImportError: attempted relative import with no known parent package`
- **Causa**: Ejecutar .py directamente con python en lugar de streamlit
- **Solución**: Usar `streamlit run` siempre, nunca `python dashboard_mayo.py`

### Problema 2: Streamlit no reconocido
- **Error**: `'streamlit' is not recognized as the name of a cmdlet`
- **Causa**: streamlit no en PATH
- **Solución**: Usar ruta completa `.\.venv\Scripts\streamlit run`

### Problema 3: Archivo no encontrado
- **Error**: `[Errno 2] No such file or directory: 'mayo.xls'`
- **Causa**: Código busca en directorio raíz, archivo está en `Inicio/`
- **Solución**: Cambiar ruta a `"Inicio/mayo.xls"`

### Problema 4: Archivo no es ZIP
- **Error**: `File is not a zip file`
- **Causa**: mayo.xls es HTML disfrazado, no Excel real
- **Solución**: Agregar soporte `pd.read_html()` en data_processor.py

### Problema 5: Dependencia faltante
- **Error**: `Missing optional dependency 'lxml'`
- **Causa**: lxml necesario para parsear HTML
- **Solución**: `pip install lxml` y agregar a requirements.txt

### Problema 6: Dashboard sin datos
- **Error**: Dashboard carga pero no muestra información
- **Causa**: Mapeo incorrecto de columnas - 'Concepto' estaba vacío
- **Solución**: Cambiar mapeo de `'Concepto': 'categoria'` → `'Articulo': 'categoria'`

## Lecciones Aprendidas
1. **Siempre verificar formato real del archivo** (HTML vs Excel)
2. **Mapear columnas según contenido real**, no nombres esperados
3. **Instalar dependencias específicas** para parsear diferentes formatos
4. **Usar debugging paso a paso** para identificar problemas de flujo de datos
5. **Validar que filtros tengan datos** antes de aplicarlos

## Comandos de Debugging Útiles
```python
# Verificar carga de datos
processor = MayoDataProcessor("Inicio/mayo.xls")
df = processor.load_data()
print(f"Columnas: {list(df.columns)}")
print(f"Filas: {len(df)}")

# Verificar mapeo
df_clean = processor.clean_data()
print(f"Categorías: {processor.get_categories_list()}")
```

## Notas Técnicas Importantes
- **mayo.xls es HTML**, no Excel real - usar `pd.read_html()`
- **Fechas en formato DD/MM/YYYY** - convertir con `pd.to_datetime(format='%d/%m/%Y')`  
- **lxml requerido** para parsear HTML
- **Streamlit cache** mejora rendimiento con `@st.cache_data`
- **Mapeo crítico**: usar 'Articulo' como 'categoria', no 'Concepto'
- **Datos de Mayo 2025** - fechas futuras válidas

## NUEVAS FUNCIONALIDADES IMPLEMENTADAS (Sesión 12 Agosto 2025) ✨

### 🗄️ Base de Datos SQLite Local
- **Archivo**: `Inicio/consular_data.db` (creado automáticamente)
- **Esquema completo** con índices optimizados
- **Gestión de duplicados** por servicio + fecha + categoría
- **Historial de archivos** cargados con estadísticas
- **Backup automático** con timestamp

### 📁 Sistema de Gestión de Archivos
- **Búsqueda recursiva** de archivos .xls/.xlsx/.html en directorios
- **Validación automática** de estructura antes de cargar
- **Carga en lote** con progreso y estadísticas
- **Previsualización** de datos antes de confirmar carga
- **Detección inteligente** de archivos ya cargados

### 📊 Análisis Histórico Avanzado
- **Comparación temporal** entre períodos
- **Métricas de eficiencia** (tasas, promedios, tendencias)
- **Top servicios** por múltiples criterios
- **Análisis por fuente** de archivo
- **Filtros dinámicos** con rango de fechas completo

### 🔧 Herramientas de Administración
- **Eliminación selectiva** de datos por archivo origen
- **Exportación avanzada** con filtros temporales
- **Información del sistema** en tiempo real
- **Mantenimiento** de cache y base de datos

## Arquitectura de Archivos

### Archivos Principales (NUEVOS)
- **`database_manager.py`**: Gestor completo SQLite con CRUD
- **`file_manager.py`**: Validación y carga de archivos múltiples
- **`enhanced_data_processor.py`**: Procesador con capacidades históricas
- **`file_upload_page.py`**: Interfaz completa de gestión de archivos
- **`dashboard_enhanced.py`**: Dashboard principal mejorado con UI rediseñada
- **`period_comparison_page.py`**: Página de comparación con gráficas consolidadas
- **`service_grouping_page.py`**: Página de agrupación de servicios
- **`robust_data_processor.py`**: Procesador robusto con validaciones

### Esquema de Base de Datos
```sql
-- Tabla principal de datos
consular_data (
  id, servicio, categoria, costo_unitario, 
  num_tramites, ingresos_totales, fecha_emision,
  formas_canceladas, archivo_origen, fecha_carga
)

-- Tabla de control de archivos
archivos_cargados (
  id, nombre_archivo, ruta_archivo, fecha_carga,
  registros_insertados, registros_duplicados, estado
)
```

## Flujo de Trabajo Recomendado

### Primera Vez
1. **Ejecutar**: `.\run_enhanced_dashboard.bat`
2. **Ir a**: "📁 Gestión de Archivos"
3. **Buscar archivos** en directorios con datos
4. **Cargar archivos** validados
5. **Regresar a**: "📈 Análisis de Datos"

### Uso Regular
1. **Dashboard mejorado**: http://localhost:8503 / http://localhost:8506 ⭐
2. **Cargar nuevos archivos** según necesidad
3. **Análisis histórico** con todos los datos
4. **Comparación de períodos** con gráficas consolidadas
5. **Exportaciones** con filtros temporales

## Para Futuras Sesiones
1. **Leer este archivo** al comenzar nueva sesión
2. **Usar dashboard MEJORADO** (`.\run_enhanced_dashboard.bat`)
3. **Base de datos preserva** todos los datos entre sesiones
4. **Si hay errores**, revisar historial de problemas aquí
5. **Debugging**: verificar base de datos en página Configuración

---

## ACTUALIZACIONES SESIÓN 13 AGOSTO 2025 🆕

### Cambios Implementados Esta Sesión:

#### 🎨 Rediseño de UI del Dashboard Principal
- **Navegación mejorada**: Cambio de dropdown sidebar a botones individuales
- **Layout optimizado**: Diseño conforme a especificaciones visuales del usuario
- **Responsividad mejorada**: Mejor distribución de elementos y espacios

#### 📊 Optimización de KPIs
- **Métricas actualizadas**: Promedio diario de ingresos en lugar de ingreso por trámite
- **Nueva métrica**: Desviación estándar de ingresos diarios para análisis de variabilidad
- **Cálculo mejorado**: Agrupación por fecha para estadísticas más precisas

#### 🕒 Controles Temporales Universales
- **Gráficas de líneas**: Opción diaria/mensual/anual en todas las visualizaciones temporales
- **Flexibilidad de análisis**: Usuarios pueden ajustar granularidad temporal según necesidad
- **Consistencia**: Mismo control disponible en todas las páginas relevantes

#### 📈 Revolucion en Comparación de Períodos
- **Estrategia consolidada**: Todos los períodos en una sola gráfica superpuesta
- **Eliminación de duplicación**: Adiós a gráficas apiladas horizontalmente
- **Código de colores**: Azul (#1f77b4), Naranja (#ff7f0e), Verde (#2ca02c) para períodos 1, 2, 3
- **KPIs simplificados**: Eliminado "servicios únicos", conservadas métricas esenciales
- **Persistencia de datos**: session_state evita pérdida de datos al cambiar controles
- **Interactividad avanzada**: Hover detallado, leyendas clickeables, ejes optimizados

### Problemas Resueltos Esta Sesión:

#### Problema 7: Errores en nombres de columnas de gráficas
- **Error**: `Value of 'x' is not the name of a column. Expected [...] but received: periodo`
- **Causa**: Uso de métodos de procesador inexistentes y nombres de columnas incorrectos
- **Solución**: Reemplazo por operaciones directas de DataFrame con nombres correctos

#### Problema 8: Pérdida de datos en comparación de períodos
- **Error**: Información desaparecía al cambiar dropdowns de control
- **Causa**: Falta de persistencia entre interacciones de usuario
- **Solución**: Implementación de `st.session_state.periods_data` para mantener estado

#### Problema 9: Gráficas apiladas poco efectivas
- **Error**: Múltiples gráficas separadas dificultaban comparación visual
- **Causa**: Estrategia de visualización por separado
- **Solución**: Función `create_consolidated_timeline_chart()` con todos los períodos superpuestos

### Archivos Modificados Esta Sesión:
1. **`dashboard_enhanced.py`**: 
   - Navegación por botones individuales
   - KPIs con promedio diario y desviación estándar
   - Controles temporales en gráficas de líneas
   - Layout redesigned según especificaciones

2. **`period_comparison_page.py`**:
   - Función `create_consolidated_timeline_chart()` nueva
   - Eliminación de KPI "servicios únicos" 
   - Implementación de `session_state` para persistencia
   - Tabla de estadísticas comparativas mejorada

### Estado Técnico Final:
- ✅ **UI completamente rediseñada** según especificaciones del usuario
- ✅ **Comparación consolidada** funcionando en una sola gráfica
- ✅ **Controles temporales** disponibles en todas las visualizaciones relevantes
- ✅ **KPIs optimizados** con métricas más relevantes (promedio diario + desv. std)
- ✅ **Persistencia de datos** en comparación de períodos
- ✅ **Navegación intuitiva** con botones individuales vs dropdown
- ✅ **Dashboard ejecutable** en http://localhost:8506

### Funcionalidades Verificadas:
- 🔍 Búsqueda y carga de archivos múltiples
- 📊 Análisis histórico con base de datos SQLite
- 📈 Gráficas interactivas con controles temporales
- 🔧 Agrupación de servicios RCM y Pasaportes
- 📋 Comparación visual de hasta 3 períodos simultáneamente
- 💾 Exportación de datos con filtros avanzados
- ⚙️ Configuración y mantenimiento del sistema
- 🆕 **NUEVA**: Comparación año vs año del mismo período
- 🆕 **NUEVA**: Análisis por día de la semana
- 🆕 **NUEVA**: Exportación completa a PDF

---

## ACTUALIZACIONES SESIÓN 14 AGOSTO 2025 🆕 REVOLUCIONARIAS

### Cambios Implementados Esta Sesión:

#### 🔄 **Rediseño COMPLETO de Comparación de Períodos**
- **Nueva filosofía**: Comparar **mismo período de diferentes años** (ej: Mayo 2024 vs Mayo 2025)
- **Interfaz intuitiva**: Selección por año + período en lugar de fechas arbitrarias
- **Dropdown de períodos**: Meses individuales + Trimestres (Q1, Q2, Q3, Q4)
- **Multiselección de años**: Hasta 7 años simultáneamente con colores diferenciados

#### 📈 **Gráfica Consolidada Revolucionaria**
- **Una sola gráfica** con múltiples líneas (una por año)
- **Eje X inteligente**: Días del período, semanas, o meses según agrupación
- **Colores automáticos**: Paleta de 7 colores rotativos para años
- **Hover mejorado**: Información detallada por año y período
- **Interactividad completa**: Leyendas clickeables, zoom, pan

#### 🎛️ **Dropdown Expandido Masivamente**
- **Totales**: Ingresos Totales + Número de Trámites Totales
- **Servicios individuales**: TODOS los servicios disponibles en BD
- **Detección automática**: Lista dinámica desde base de datos
- **Análisis granular**: Comparar comportamiento de servicios específicos

#### 📅 **Agrupación Temporal SEMANAL**
- **Nueva opción**: Diario, **Semanal**, Mensual
- **Análisis por semana**: Útil para detectar patrones semanales
- **Flexibilidad total**: Cambiar agrupación sin perder datos
- **Eje X adaptativo**: Etiquetas optimizadas por tipo de agrupación

#### 📊 **Análisis por Día de la Semana (COMPLETAMENTE NUEVO)**
- **Detección automática**: Mayor y menor actividad por día
- **Métricas duales**: Ingresos promedio Y trámites promedio por día
- **Tabla completa**: Estadísticas para todos los días (Lunes-Domingo)
- **Insight empresarial**: Identificar patrones operacionales semanales

#### 📄 **Exportación PDF Profesional (COMPLETAMENTE NUEVO)**
- **Botón de exportación**: Genera PDF completo de la página
- **Contenido integral**:
  - KPIs comparativos en tabla profesional
  - Gráfica incluida como imagen PNG de alta calidad
  - Análisis semanal con días destacados
  - Fecha y hora de generación
- **Nombres inteligentes**: Archivo con período, años, y timestamp
- **Tecnología robusta**: ReportLab + Kaleido para conversión gráficas
- **Descarga directa**: Botón de descarga inmediata en navegador

#### 🎨 **KPIs Optimizados**
- **4 métricas clave**:
  - 💰 Ingresos Totales (con delta vs año base)
  - 📄 Trámites Totales (con delta vs año base)  
  - 📊 Ingreso Diario Promedio
  - 📋 Trámites Diario Promedio
- **Comparación inteligente**: Deltas automáticos respecto al primer año
- **Formato profesional**: Monedas, miles, decimales apropiados

### Problemas Resueltos Esta Sesión:

#### Problema 10: Comparación de fechas arbitrarias poco útil
- **Error**: Difícil comparar mismos períodos de diferentes años
- **Causa**: Interfaz basada en rangos de fechas libres
- **Solución**: Nueva interfaz año + período para comparaciones estacionales

#### Problema 11: Gráficas múltiples confusas
- **Error**: Varias gráficas separadas dificultaban comparación
- **Causa**: Una gráfica por período en layout vertical
- **Solución**: Gráfica única consolidada con líneas por año superpuestas

#### Problema 12: Dropdown limitado de elementos
- **Error**: Solo ingresos y trámites totales disponibles
- **Causa**: Opciones hardcodeadas sin servicios individuales
- **Solución**: Generación dinámica desde BD con todos los servicios

#### Problema 13: Falta análisis de patrones semanales
- **Error**: No había forma de identificar días de mayor/menor actividad
- **Causa**: Solo agrupación diaria, mensual, anual
- **Solución**: Nuevo análisis por día de semana con estadísticas

#### Problema 14: Sin capacidad de exportación
- **Error**: Imposible generar reportes para compartir
- **Causa**: No existía funcionalidad de exportación
- **Solución**: Sistema completo de generación PDF con contenido integral

### Archivos Modificados Esta Sesión:

1. **`period_comparison_page.py`**: 
   - **REDISEÑO COMPLETO** (814 líneas)
   - Nueva función `configure_year_comparison()`
   - Nueva función `create_year_comparison_chart()`
   - Nueva función `calculate_weekly_statistics()`
   - Nueva función `show_weekly_analysis()`
   - Nueva función `create_pdf_report()`
   - Eliminadas funciones obsoletas de comparación anterior

2. **`requirements.txt`**:
   - Agregadas dependencias: `reportlab>=4.4.0`, `matplotlib>=3.10.0`, `kaleido>=1.0.0`

3. **`test_new_functionality.py`** (NUEVO):
   - Tests completos de todas las funcionalidades
   - Verificación de componentes PDF
   - Tests de configuración de períodos
   - Validación de estadísticas semanales

### Estado Técnico Final:

- ✅ **Interfaz completamente rediseñada** para comparación año vs año
- ✅ **Gráfica consolidada funcional** con líneas por año
- ✅ **Dropdown expandido** con servicios individuales dinámicos
- ✅ **Agrupación semanal** implementada y funcional
- ✅ **Análisis día de semana** con estadísticas mayor/menor actividad
- ✅ **Exportación PDF completa** con gráficas, tablas y análisis
- ✅ **Testing verificado** de componentes core sin Streamlit
- ✅ **Dependencias instaladas** y verificadas (ReportLab, Kaleido, Matplotlib)

### Flujo de Usuario Nuevo:

1. **Seleccionar Período Base**: Mayo, Q2, etc.
2. **Elegir Años**: 2024, 2025, 2026... (multiselect)
3. **Configurar Elemento**: Totales o servicio específico
4. **Ajustar Agrupación**: Diario/Semanal/Mensual
5. **Ejecutar Comparación**: Ver gráfica consolidada con líneas por año
6. **Revisar KPIs**: Deltas automáticos entre años
7. **Analizar Patrones**: Días de mayor/menor actividad
8. **Exportar PDF**: Reporte completo para compartir

### Beneficios Empresariales:

- **Análisis estacional**: Comparar mismo período año tras año
- **Detección de tendencias**: Identificar crecimiento/decrecimiento anual  
- **Optimización operativa**: Días de semana más/menos productivos
- **Reportes profesionales**: PDFs para presentaciones ejecutivas
- **Análisis granular**: Por servicio específico o totales
- **Flexibilidad temporal**: Diario, semanal, mensual según necesidad

### Arquitectura Técnica:

```python
# Nueva estructura de funciones principales
show_period_comparison_page()
├── get_available_years_and_periods()    # Detecta años/meses disponibles
├── configure_year_comparison()          # UI de selección año + período  
├── execute_year_comparison()            # Ejecuta comparación
├── show_year_comparison_results()       # Coordina visualización
    ├── show_year_comparative_kpis()     # KPIs con deltas
    ├── show_year_timeline_chart()       # Gráfica consolidada
    ├── show_weekly_analysis()           # Análisis día semana
    └── show_pdf_export_button()         # Exportación PDF
```

### Para Futuras Sesiones:

1. **Leer esta sección** antes de continuar desarrollo
2. **Usar funcionalidades nuevas** en lugar de versiones obsoletas
3. **Período vs Año** es el nuevo paradigma de comparación
4. **PDF incluye todo**: No desarrollar exportaciones parciales
5. **Testing independiente** disponible en `test_new_functionality.py`

---