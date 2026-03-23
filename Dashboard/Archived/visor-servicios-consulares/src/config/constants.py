"""
Constantes del sistema
"""

# Columnas de la base de datos
DB_COLUMNS = {
    'servicio': 'TEXT',
    'categoria': 'TEXT', 
    'costo_unitario': 'REAL',
    'num_tramites': 'INTEGER',
    'ingresos_totales': 'REAL',
    'fecha_emision': 'DATE',
    'formas_canceladas': 'INTEGER',
    'archivo_origen': 'TEXT',
    'fecha_carga': 'TIMESTAMP'
}

# Mapeo de columnas HTML a BD
HTML_COLUMN_MAPPING = {
    'Servicio': 'servicio',
    'Articulo': 'categoria',
    'Derechos': 'costo_unitario',
    'No. de trámites': 'num_tramites',
    'Importe USD': 'ingresos_totales',
    'Fecha recaudación': 'fecha_emision',
    'No. cancelados': 'formas_canceladas'
}

# Tipos de agrupación temporal
TEMPORAL_GROUPINGS = {
    'diario': {
        'label': 'Diario',
        'format': '%Y-%m-%d',
        'pandas_freq': 'D'
    },
    'semanal': {
        'label': 'Semanal', 
        'format': '%Y-W%U',
        'pandas_freq': 'W'
    },
    'mensual': {
        'label': 'Mensual',
        'format': '%Y-%m',
        'pandas_freq': 'M'
    },
    'trimestral': {
        'label': 'Trimestral',
        'format': '%Y-Q%q',
        'pandas_freq': 'Q'
    },
    'anual': {
        'label': 'Anual',
        'format': '%Y',
        'pandas_freq': 'Y'
    }
}

# Días de la semana en español
DIAS_SEMANA = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes', 
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

# Meses en español
MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Extensiones de archivo soportadas
SUPPORTED_FILE_EXTENSIONS = ['.xls', '.xlsx', '.html', '.csv']

# Límites del sistema
MAX_FILE_SIZE_MB = 50
MAX_RECORDS_DISPLAY = 1000
MAX_CHART_POINTS = 500

# Mensajes de estado
STATUS_MESSAGES = {
    'loading': '🔄 Cargando datos...',
    'success': '✅ Operación exitosa',
    'error': '❌ Error en la operación',
    'warning': '⚠️ Advertencia',
    'info': 'ℹ️ Información',
    'no_data': '📭 No hay datos disponibles'
}

# Iconos para navegación
NAV_ICONS = {
    'dashboard': '📊',
    'admin': '🔧', 
    'reports': '📈',
    'settings': '⚙️',
    'upload': '📁',
    'export': '📄',
    'backup': '💾',
    'help': '❓'
}

# Configuración de tablas
TABLE_CONFIG = {
    'page_size': 50,
    'sort_action': 'native',
    'filter_action': 'native',
    'style_cell': {
        'textAlign': 'left',
        'padding': '10px',
        'fontFamily': 'Arial, sans-serif'
    },
    'style_header': {
        'backgroundColor': '#f8f9fa',
        'fontWeight': 'bold',
        'border': '1px solid #dee2e6'
    },
    'style_data': {
        'border': '1px solid #dee2e6'
    }
}

# Configuración de gráficas por defecto
CHART_LAYOUTS = {
    'line': {
        'showlegend': True,
        'hovermode': 'x unified',
        'xaxis': {'showgrid': True, 'gridcolor': '#f0f0f0'},
        'yaxis': {'showgrid': True, 'gridcolor': '#f0f0f0'}
    },
    'bar': {
        'showlegend': False,
        'hovermode': 'closest'
    },
    'pie': {
        'showlegend': True,
        'hovermode': 'closest'
    }
}

# Formatos de número
NUMBER_FORMATS = {
    'currency': '${:,.2f}',
    'integer': '{:,}',
    'decimal': '{:,.2f}',
    'percentage': '{:.1%}'
}

# Configuración de exportación PDF
PDF_CONFIG = {
    'page_size': 'A4',
    'margins': {
        'top': 72,
        'bottom': 72, 
        'left': 72,
        'right': 72
    },
    'title_font_size': 16,
    'subtitle_font_size': 14,
    'body_font_size': 10,
    'table_font_size': 8
}