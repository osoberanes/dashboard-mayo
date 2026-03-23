"""
Visor de Servicios Consulares - Dashboard Moderno y Dinámico
Frontend atractivo con funcionalidades avanzadas de análisis
"""
import dash
from dash import html, dcc, Input, Output, State, dash_table, callback, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import sqlite3
import os
import base64
import io
import json

# Configurar aplicación con tema moderno
app = dash.Dash(__name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ]
)
app.title = "🚀 Visor de Servicios Consulares"

# Configuraciones
DB_PATH = "data/consular_data.db"

# Paleta de colores moderna
COLORS = {
    'primary': '#3B82F6',     # Blue
    'secondary': '#8B5CF6',   # Purple  
    'success': '#10B981',     # Green
    'warning': '#F59E0B',     # Amber
    'danger': '#EF4444',      # Red
    'info': '#06B6D4',        # Cyan
    'dark': '#1F2937',        # Gray-800
    'light': '#F8FAFC',       # Gray-50
    'gradient_1': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'gradient_2': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'gradient_3': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
}

def init_database():
    """Inicializa la base de datos"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consular_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servicio TEXT NOT NULL,
            categoria TEXT,
            costo_unitario REAL,
            num_tramites INTEGER,
            ingresos_totales REAL,
            fecha_emision DATE,
            formas_canceladas INTEGER DEFAULT 0,
            archivo_origen TEXT,
            fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_data_summary():
    """Obtiene resumen de datos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM consular_data")
        total_registros = cursor.fetchone()[0]
        
        if total_registros == 0:
            return {"total_registros": 0}
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_registros,
                SUM(ingresos_totales) as total_ingresos,
                SUM(num_tramites) as total_tramites,
                MIN(fecha_emision) as fecha_min,
                MAX(fecha_emision) as fecha_max,
                COUNT(DISTINCT servicio) as servicios_unicos,
                AVG(ingresos_totales) as promedio_ingresos
            FROM consular_data
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "total_registros": result[0],
            "total_ingresos": result[1] or 0,
            "total_tramites": result[2] or 0,
            "fecha_min": result[3],
            "fecha_max": result[4],
            "servicios_unicos": result[5],
            "promedio_ingresos": result[6] or 0
        }
    except Exception as e:
        return {"error": str(e)}

def load_data_from_db(start_date=None, end_date=None, servicio=None):
    """Carga datos con filtros"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        query = "SELECT * FROM consular_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND fecha_emision >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND fecha_emision <= ?"
            params.append(end_date)
            
        if servicio and servicio != "TODOS":
            query += " AND servicio = ?"
            params.append(servicio)
        
        query += " ORDER BY fecha_emision DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
            
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame()

def get_available_services():
    """Obtiene lista de servicios disponibles"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT servicio FROM consular_data ORDER BY servicio")
        services = [row[0] for row in cursor.fetchall()]
        conn.close()
        return services
    except:
        return []

def parse_uploaded_file(contents, filename):
    """Parsea archivo subido"""
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if 'xls' in filename.lower():
            try:
                df = pd.read_excel(io.BytesIO(decoded))
            except:
                df = pd.read_html(io.BytesIO(decoded))[0]
        elif 'html' in filename.lower():
            df = pd.read_html(io.BytesIO(decoded))[0]
        else:
            return None, "Formato no soportado"
        
        # Mapeo de columnas
        column_mapping = {
            'Servicio': 'servicio',
            'Articulo': 'categoria',
            'Derechos': 'costo_unitario',
            'No. de trámites': 'num_tramites',
            'Importe USD': 'ingresos_totales',
            'Fecha recaudación': 'fecha_emision',
            'No. cancelados': 'formas_canceladas'
        }
        
        # Verificar columnas
        missing_columns = [col for col in column_mapping.keys() if col not in df.columns]
        if missing_columns:
            return None, f"Columnas faltantes: {', '.join(missing_columns)}"
        
        df = df.rename(columns=column_mapping)
        df = df[[col for col in column_mapping.values() if col in df.columns]]
        
        # Limpiar datos
        for col in ['costo_unitario', 'num_tramites', 'ingresos_totales', 'formas_canceladas']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce').fillna(0)
        
        if 'fecha_emision' in df.columns:
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'], format='%d/%m/%Y', errors='coerce')
        
        df['archivo_origen'] = filename
        
        return df, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"

# CSS personalizado
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-color: #3B82F6;
                --secondary-color: #8B5CF6;
                --success-color: #10B981;
                --warning-color: #F59E0B;
                --danger-color: #EF4444;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 0;
            }
            
            .main-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                margin: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                animation: slideInUp 0.6s ease-out;
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .header-gradient {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
            }
            
            .card-modern {
                border: none !important;
                border-radius: 15px !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
                transition: all 0.3s ease !important;
                background: white !important;
            }
            
            .card-modern:hover {
                transform: translateY(-5px) !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
            }
            
            .kpi-card {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 15px;
                padding: 25px;
                color: white;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
                border: none;
            }
            
            .kpi-card:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            }
            
            .kpi-value {
                font-size: 2.5rem;
                font-weight: 700;
                margin: 10px 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            .kpi-label {
                font-size: 1rem;
                opacity: 0.9;
                font-weight: 500;
            }
            
            .control-panel {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                margin-bottom: 20px;
            }
            
            .btn-modern {
                border-radius: 25px !important;
                font-weight: 600 !important;
                padding: 12px 30px !important;
                transition: all 0.3s ease !important;
                border: none !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
            }
            
            .btn-modern:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
            }
            
            .nav-tabs .nav-link {
                border-radius: 25px 25px 0 0 !important;
                font-weight: 600 !important;
                padding: 15px 25px !important;
                margin-right: 5px !important;
                transition: all 0.3s ease !important;
            }
            
            .nav-tabs .nav-link.active {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
                color: white !important;
                border: none !important;
            }
            
            .upload-zone {
                border: 2px dashed var(--primary-color) !important;
                border-radius: 15px !important;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.05)) !important;
                transition: all 0.3s ease !important;
                padding: 40px !important;
            }
            
            .upload-zone:hover {
                border-color: var(--secondary-color) !important;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)) !important;
                transform: scale(1.02) !important;
            }
            
            .metric-selector {
                background: white;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                margin: 10px 0;
            }
            
            .chart-container {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            
            .chart-container:hover {
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
            }
            
            .loading-spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 3px solid rgba(59, 130, 246, 0.3);
                border-radius: 50%;
                border-top-color: var(--primary-color);
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .comparison-panel {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                margin: 20px 0;
            }
            
            .date-range-picker {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout principal
app.layout = html.Div([
    html.Div([
        # Header moderno
        html.Div([
            html.H1("🚀 Visor de Servicios Consulares", className="header-gradient mb-2", style={'fontSize': '3rem'}),
            html.P("Dashboard Interactivo de Análisis Consular", className="text-muted", style={'fontSize': '1.2rem'})
        ], className="text-center mb-4"),
        
        # Navegación con pestañas modernas
        dbc.Tabs([
            dbc.Tab(label="📊 Dashboard Inteligente", tab_id="dashboard", className="tab-modern"),
            dbc.Tab(label="📈 Comparación Temporal", tab_id="comparison", className="tab-modern"),
            dbc.Tab(label="📁 Gestión de Datos", tab_id="management", className="tab-modern"),
            dbc.Tab(label="📋 Explorador de Datos", tab_id="explorer", className="tab-modern")
        ], id="main-tabs", active_tab="dashboard"),
        
        html.Hr(style={'margin': '30px 0', 'border': 'none', 'height': '1px', 'background': 'linear-gradient(90deg, transparent, #3B82F6, transparent)'}),
        
        # Contenido dinámico
        html.Div(id="tab-content"),
        
        # Stores para datos
        dcc.Store(id="data-store"),
        dcc.Store(id="filter-store"),
        dcc.Store(id="comparison-store"),
        
        # Interval para actualizaciones
        dcc.Interval(id="interval-component", interval=10000, n_intervals=0)
        
    ], className="main-container")
])

# Callback para renderizar contenido de pestañas
@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "dashboard":
        return render_dashboard_tab()
    elif active_tab == "comparison":
        return render_comparison_tab()
    elif active_tab == "management":
        return render_management_tab()
    elif active_tab == "explorer":
        return render_explorer_tab()
    return html.Div("Selecciona una pestaña")

def render_dashboard_tab():
    """Dashboard principal con KPIs y controles interactivos"""
    
    summary = get_data_summary()
    services = get_available_services()
    
    return html.Div([
        # KPIs animados
        html.Div(id="kpi-cards", className="mb-4"),
        
        # Panel de control interactivo
        html.Div([
            html.H4("🎛️ Controles Interactivos", className="text-white mb-3"),
            
            dbc.Row([
                # Selector de métrica
                dbc.Col([
                    html.Label("📊 Métrica a Analizar:", className="text-white fw-bold mb-2"),
                    dcc.Dropdown(
                        id="metric-selector",
                        options=[
                            {"label": "💰 Ingresos Totales", "value": "ingresos_totales"},
                            {"label": "📄 Número de Trámites", "value": "num_tramites"},
                            {"label": "⚡ Ingreso por Trámite", "value": "ingreso_por_tramite"},
                            {"label": "🔢 Servicios Únicos", "value": "servicios_unicos"}
                        ],
                        value="ingresos_totales",
                        className="mb-3",
                        style={'color': '#333'}
                    )
                ], md=3),
                
                # Selector de servicio
                dbc.Col([
                    html.Label("🔧 Servicio Específico:", className="text-white fw-bold mb-2"),
                    dcc.Dropdown(
                        id="service-selector",
                        options=[{"label": "📊 Todos los servicios", "value": "TODOS"}] + 
                               [{"label": service, "value": service} for service in services[:15]],
                        value="TODOS",
                        className="mb-3",
                        style={'color': '#333'}
                    )
                ], md=3),
                
                # Rango de fechas
                dbc.Col([
                    html.Label("📅 Rango de Fechas:", className="text-white fw-bold mb-2"),
                    dcc.DatePickerRange(
                        id="date-range-picker",
                        start_date=date.today() - timedelta(days=365),
                        end_date=date.today(),
                        display_format='DD/MM/YYYY',
                        className="mb-3"
                    )
                ], md=4),
                
                # Botón de actualización
                dbc.Col([
                    html.Label("🔄 Acción:", className="text-white fw-bold mb-2"),
                    html.Br(),
                    dbc.Button(
                        "Actualizar Dashboard",
                        id="update-dashboard",
                        color="light",
                        className="btn-modern"
                    )
                ], md=2)
            ])
        ], className="control-panel"),
        
        # Gráficas principales
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("📈 Evolución Temporal", className="mb-3"),
                    dcc.Graph(id="main-timeline-chart")
                ], className="chart-container")
            ], md=6),
            
            dbc.Col([
                html.Div([
                    html.H5("🏆 Top Servicios", className="mb-3"),
                    dcc.Graph(id="top-services-chart")
                ], className="chart-container")
            ], md=6)
        ], className="mb-4"),
        
        # Gráficas secundarias
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("📊 Distribución por Categoría", className="mb-3"),
                    dcc.Graph(id="category-distribution-chart")
                ], className="chart-container")
            ], md=4),
            
            dbc.Col([
                html.Div([
                    html.H5("📈 Tendencia Semanal", className="mb-3"),
                    dcc.Graph(id="weekly-trend-chart")
                ], className="chart-container")
            ], md=4),
            
            dbc.Col([
                html.Div([
                    html.H5("🎯 Análisis de Eficiencia", className="mb-3"),
                    dcc.Graph(id="efficiency-chart")
                ], className="chart-container")
            ], md=4)
        ])
    ])

def render_comparison_tab():
    """Pestaña de comparación temporal avanzada"""
    
    return html.Div([
        # Panel de configuración de comparación
        html.Div([
            html.H4("⚖️ Configuración de Comparación Temporal", className="text-white mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.Label("📅 Período Base:", className="text-white fw-bold"),
                    dcc.DatePickerRange(
                        id="comparison-period-1",
                        start_date=date.today() - timedelta(days=60),
                        end_date=date.today() - timedelta(days=30),
                        display_format='DD/MM/YYYY'
                    )
                ], md=4),
                
                dbc.Col([
                    html.Label("📅 Período a Comparar:", className="text-white fw-bold"),
                    dcc.DatePickerRange(
                        id="comparison-period-2",
                        start_date=date.today() - timedelta(days=30),
                        end_date=date.today(),
                        display_format='DD/MM/YYYY'
                    )
                ], md=4),
                
                dbc.Col([
                    html.Label("📊 Métrica de Comparación:", className="text-white fw-bold"),
                    dcc.Dropdown(
                        id="comparison-metric",
                        options=[
                            {"label": "💰 Ingresos", "value": "ingresos_totales"},
                            {"label": "📄 Trámites", "value": "num_tramites"},
                            {"label": "🔢 Servicios Únicos", "value": "servicios_count"}
                        ],
                        value="ingresos_totales",
                        style={'color': '#333'}
                    )
                ], md=4)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "🔄 Ejecutar Comparación",
                        id="execute-comparison",
                        color="light",
                        className="btn-modern",
                        size="lg"
                    )
                ], className="text-center")
            ])
        ], className="comparison-panel"),
        
        # Resultados de comparación
        html.Div(id="comparison-results"),
        
        # Gráficas de comparación
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("📊 Comparación Temporal", className="mb-3"),
                    dcc.Graph(id="comparison-timeline-chart")
                ], className="chart-container")
            ], md=6),
            
            dbc.Col([
                html.Div([
                    html.H5("🎯 Análisis de Diferencias", className="mb-3"),
                    dcc.Graph(id="comparison-diff-chart")
                ], className="chart-container")
            ], md=6)
        ])
    ])

def render_management_tab():
    """Pestaña de gestión de datos mejorada"""
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("📤 Carga de Archivos", className="mb-4"),
                    
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt fa-4x mb-3", style={'color': COLORS['primary']}),
                            html.H4('Arrastra archivos aquí o haz clic para seleccionar', className="mb-3"),
                            html.P('Formatos soportados: .xls, .xlsx, .html', className="text-muted")
                        ], className="text-center"),
                        className="upload-zone",
                        multiple=False
                    ),
                    
                    html.Div(id="upload-status", className="mt-4")
                ], className="card-modern", style={'padding': '30px'})
            ], md=8),
            
            dbc.Col([
                html.Div([
                    html.H5("📋 Estado del Sistema", className="mb-3"),
                    html.Div(id="system-status-info")
                ], className="card-modern", style={'padding': '20px'})
            ], md=4)
        ], className="mb-4"),
        
        # Gestión avanzada
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("🔧 Herramientas Avanzadas", className="mb-3"),
                    dbc.ButtonGroup([
                        dbc.Button("🔄 Limpiar Cache", color="warning", className="btn-modern"),
                        dbc.Button("📊 Recalcular Métricas", color="info", className="btn-modern"),
                        dbc.Button("💾 Exportar Datos", color="success", className="btn-modern")
                    ], className="mb-3")
                ], className="card-modern", style={'padding': '20px'})
            ])
        ])
    ])

def render_explorer_tab():
    """Explorador de datos interactivo"""
    
    return html.Div([
        html.Div([
            html.H4("🔍 Filtros Avanzados", className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.Label("📅 Filtro de Fechas:", className="fw-bold"),
                    dcc.DatePickerRange(
                        id="explorer-date-range",
                        start_date=date.today() - timedelta(days=90),
                        end_date=date.today(),
                        display_format='DD/MM/YYYY'
                    )
                ], md=4),
                
                dbc.Col([
                    html.Label("🔧 Filtro de Servicio:", className="fw-bold"),
                    dcc.Dropdown(
                        id="explorer-service-filter",
                        placeholder="Seleccionar servicio..."
                    )
                ], md=4),
                
                dbc.Col([
                    html.Label("📊 Registros por Página:", className="fw-bold"),
                    dcc.Dropdown(
                        id="explorer-page-size",
                        options=[
                            {"label": "25 registros", "value": 25},
                            {"label": "50 registros", "value": 50},
                            {"label": "100 registros", "value": 100}
                        ],
                        value=50
                    )
                ], md=4)
            ])
        ], className="metric-selector mb-4"),
        
        # Tabla de datos
        html.Div([
            html.H5("📋 Datos Filtrados", className="mb-3"),
            html.Div(id="data-explorer-table")
        ], className="card-modern", style={'padding': '20px'})
    ])

# Callbacks principales
@app.callback(
    Output("kpi-cards", "children"),
    [Input("update-dashboard", "n_clicks"),
     Input("interval-component", "n_intervals")],
    [State("date-range-picker", "start_date"),
     State("date-range-picker", "end_date"),
     State("service-selector", "value")]
)
def update_kpi_cards(n_clicks, n_intervals, start_date, end_date, service):
    """Actualiza las tarjetas KPI"""
    
    df = load_data_from_db(start_date, end_date, service)
    
    if df.empty:
        return html.Div([
            dbc.Alert("⚠️ No hay datos disponibles para el rango seleccionado", color="warning", className="text-center")
        ])
    
    # Calcular métricas
    total_ingresos = df['ingresos_totales'].sum()
    total_tramites = df['num_tramites'].sum()
    servicios_unicos = df['servicio'].nunique()
    promedio_diario = df.groupby('fecha_emision')['ingresos_totales'].sum().mean()
    
    # Crear tarjetas KPI
    kpi_cards = dbc.Row([
        dbc.Col([
            html.Div([
                html.I(className="fas fa-dollar-sign fa-2x mb-2"),
                html.Div(f"${total_ingresos:,.2f}", className="kpi-value"),
                html.Div("Ingresos Totales", className="kpi-label")
            ], className="kpi-card", style={'background': COLORS['gradient_1']})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-file-alt fa-2x mb-2"),
                html.Div(f"{total_tramites:,}", className="kpi-value"),
                html.Div("Trámites Procesados", className="kpi-label")
            ], className="kpi-card", style={'background': COLORS['gradient_2']})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-cogs fa-2x mb-2"),
                html.Div(f"{servicios_unicos}", className="kpi-value"),
                html.Div("Servicios Únicos", className="kpi-label")
            ], className="kpi-card", style={'background': COLORS['gradient_3']})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-chart-line fa-2x mb-2"),
                html.Div(f"${promedio_diario:.0f}", className="kpi-value"),
                html.Div("Promedio Diario", className="kpi-label")
            ], className="kpi-card", style={'background': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'})
        ], md=3)
    ])
    
    return kpi_cards

@app.callback(
    [Output("main-timeline-chart", "figure"),
     Output("top-services-chart", "figure"),
     Output("category-distribution-chart", "figure"),
     Output("weekly-trend-chart", "figure"),
     Output("efficiency-chart", "figure")],
    [Input("update-dashboard", "n_clicks"),
     Input("metric-selector", "value"),
     Input("interval-component", "n_intervals")],
    [State("date-range-picker", "start_date"),
     State("date-range-picker", "end_date"),
     State("service-selector", "value")]
)
def update_dashboard_charts(n_clicks, metric, n_intervals, start_date, end_date, service):
    """Actualiza todas las gráficas del dashboard"""
    
    df = load_data_from_db(start_date, end_date, service)
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No hay datos disponibles", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
    
    # Gráfica 1: Evolución temporal
    if metric == "ingreso_por_tramite":
        df_temp = df.copy()
        df_temp['ingreso_por_tramite'] = df_temp['ingresos_totales'] / df_temp['num_tramites'].replace(0, 1)
        df_daily = df_temp.groupby('fecha_emision')['ingreso_por_tramite'].mean().reset_index()
        y_col = 'ingreso_por_tramite'
        title = "Evolución del Ingreso por Trámite"
    elif metric == "servicios_unicos":
        df_daily = df.groupby('fecha_emision')['servicio'].nunique().reset_index()
        y_col = 'servicio'
        title = "Evolución de Servicios Únicos por Día"
    else:
        df_daily = df.groupby('fecha_emision')[metric].sum().reset_index()
        y_col = metric
        title = f"Evolución de {metric.replace('_', ' ').title()}"
    
    timeline_fig = px.line(df_daily, x='fecha_emision', y=y_col, title=title)
    timeline_fig.update_traces(line_color=COLORS['primary'], line_width=3)
    timeline_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        title_font_size=16
    )
    
    # Gráfica 2: Top servicios
    if metric in ['ingresos_totales', 'num_tramites']:
        df_services = df.groupby('servicio')[metric].sum().nlargest(10).reset_index()
    else:
        df_services = df.groupby('servicio')['ingresos_totales'].sum().nlargest(10).reset_index()
        metric = 'ingresos_totales'
    
    services_fig = px.bar(df_services, x=metric, y='servicio', orientation='h',
                         title="Top 10 Servicios", color=metric,
                         color_continuous_scale='Viridis')
    services_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12)
    )
    
    # Gráfica 3: Distribución por categoría
    df_category = df.groupby('categoria')['ingresos_totales'].sum().reset_index()
    category_fig = px.pie(df_category, values='ingresos_totales', names='categoria',
                         title="Distribución por Categoría")
    category_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12)
    )
    
    # Gráfica 4: Tendencia semanal
    df['dia_semana'] = df['fecha_emision'].dt.day_name()
    df_weekly = df.groupby('dia_semana')['ingresos_totales'].mean().reset_index()
    
    # Ordenar días de la semana
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_weekly['dia_semana'] = pd.Categorical(df_weekly['dia_semana'], categories=days_order, ordered=True)
    df_weekly = df_weekly.sort_values('dia_semana')
    
    weekly_fig = px.bar(df_weekly, x='dia_semana', y='ingresos_totales',
                       title="Tendencia Semanal", color='ingresos_totales',
                       color_continuous_scale='Blues')
    weekly_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12)
    )
    
    # Gráfica 5: Análisis de eficiencia
    df_efficiency = df.copy()
    df_efficiency['eficiencia'] = df_efficiency['ingresos_totales'] / df_efficiency['num_tramites'].replace(0, 1)
    
    efficiency_fig = px.scatter(df_efficiency, x='num_tramites', y='ingresos_totales',
                               size='eficiencia', color='categoria',
                               title="Análisis de Eficiencia (Trámites vs Ingresos)",
                               hover_data=['servicio'])
    efficiency_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12)
    )
    
    return timeline_fig, services_fig, category_fig, weekly_fig, efficiency_fig

@app.callback(
    [Output("upload-status", "children"),
     Output("data-store", "data")],
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def handle_file_upload(contents, filename):
    """Maneja la carga de archivos"""
    if contents is None:
        return "", {}
    
    df, error = parse_uploaded_file(contents, filename)
    
    if error:
        return dbc.Alert(f"❌ {error}", color="danger"), {}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('consular_data', conn, if_exists='append', index=False)
        conn.close()
        
        success_msg = dbc.Alert([
            html.H5("✅ ¡Carga Exitosa!", className="mb-2"),
            html.P(f"Archivo '{filename}' procesado correctamente"),
            html.P(f"📊 {len(df)} registros insertados en la base de datos")
        ], color="success")
        
        return success_msg, {"uploaded": True, "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        error_msg = dbc.Alert(f"❌ Error guardando datos: {str(e)}", color="danger")
        return error_msg, {}

@app.callback(
    Output("system-status-info", "children"),
    Input("interval-component", "n_intervals")
)
def update_system_status(n_intervals):
    """Actualiza información del sistema"""
    
    summary = get_data_summary()
    
    if "error" in summary:
        return dbc.Alert(f"❌ Error: {summary['error']}", color="danger")
    
    if summary.get("total_registros", 0) == 0:
        return dbc.Alert("⚠️ No hay datos cargados", color="warning")
    
    return html.Div([
        html.P([html.Strong("📊 Registros: "), f"{summary['total_registros']:,}"]),
        html.P([html.Strong("💰 Ingresos: "), f"${summary['total_ingresos']:,.2f}"]),
        html.P([html.Strong("📄 Trámites: "), f"{summary['total_tramites']:,}"]),
        html.P([html.Strong("🔧 Servicios: "), f"{summary['servicios_unicos']}"]),
        html.P([html.Strong("📅 Período: "), f"{summary['fecha_min']} - {summary['fecha_max']}"])
    ])

if __name__ == '__main__':
    init_database()
    app.run(host='127.0.0.1', port=8050, debug=True)