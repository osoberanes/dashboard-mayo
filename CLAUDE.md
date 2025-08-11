# Proyecto Dashboard Mayo - Información de Sesión

## Resumen del Proyecto
Dashboard interactivo de análisis de datos consulares mexicanos usando Streamlit y Plotly para visualizar información de trámites, ingresos y servicios consulares.

## Estado Actual ✅ COMPLETADO - Sesión 11 Agosto 2025
- **Dashboard funcionando** perfectamente en `http://localhost:8501`
- **Datos procesados**: 446 filas de servicios consulares (Mayo 2025)
- **KPIs calculados correctamente**: $251,880 ingresos, 5,375 trámites, 75 canceladas
- **5 categorías** (Pasaportes E/G, Servicios Consulares, Notariales, etc.)
- **60 servicios únicos** disponibles
- **Filtros y visualizaciones** funcionando correctamente

## Estructura de Archivos
```
C:\Users\consuladscrito\claudecode\
├── Inicio/
│   ├── dashboard_mayo.py      # Dashboard principal (Streamlit)
│   ├── data_processor.py      # Procesamiento de datos
│   ├── mayo.xls              # Archivo HTML con datos
│   └── requirements.txt       # Dependencias
├── run_dashboard.bat         # Script de ejecución
└── .venv/                   # Entorno virtual Python
```

## Problemas Resueltos
1. **Error de importación relativa** → Corregido path
2. **Falta dependencia lxml** → Instalada con pip
3. **Archivo .xls es HTML** → Soporte con `pd.read_html()`
4. **Mapeo de columnas incorrecto** → Cambiado 'Concepto' → 'Articulo'
5. **Filtros sin datos** → Categorías ahora disponibles

## Comandos para Ejecutar
```powershell
# Opción 1: Script batch
.\run_dashboard.bat

# Opción 2: Streamlit directo
.\.venv\Scripts\streamlit run Inicio\dashboard_mayo.py

# Opción 3: Con entorno virtual
.\.venv\Scripts\Activate.ps1
streamlit run Inicio\dashboard_mayo.py
```

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

## Funcionalidades del Dashboard
- 📊 Métricas principales (KPIs)
- 📈 Series temporales (diario/mensual/anual)
- 📊 Análisis por categoría
- 🔍 Análisis por servicio
- 📋 Datos detallados exportables
- 🎛️ Filtros por fecha, categoría y servicio

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

## Para Futuras Sesiones
1. **Leer este archivo** al comenzar nueva sesión
2. **Verificar entorno virtual** activado
3. **Ejecutar** `.\run_dashboard.bat` directamente
4. **Si hay errores**, revisar historial de problemas aquí
5. **Debugging**: usar archivos de prueba en directorio raíz