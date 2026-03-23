"""
Visor de Servicios Consulares - Versión Simplificada Funcional
"""
import dash
from dash import html, dcc, Input, Output, State, dash_table, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import sqlite3
import os
import base64
import io

# Configurar aplicación
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Visor de Servicios Consulares"

# Configuraciones
DB_PATH = "data/consular_data.db"

def init_database():
    """Inicializa la base de datos si no existe"""
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
        
        # Total registros
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM consular_data")
        total_registros = cursor.fetchone()[0]
        
        if total_registros == 0:
            return {"total_registros": 0, "mensaje": "No hay datos cargados"}
        
        # Estadísticas básicas
        cursor.execute("""
            SELECT 
                COUNT(*) as total_registros,
                SUM(ingresos_totales) as total_ingresos,
                SUM(num_tramites) as total_tramites,
                MIN(fecha_emision) as fecha_min,
                MAX(fecha_emision) as fecha_max,
                COUNT(DISTINCT servicio) as servicios_unicos
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
            "servicios_unicos": result[5]
        }
    except Exception as e:
        return {"error": str(e)}

def load_data_from_db():
    """Carga datos desde la base de datos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM consular_data ORDER BY fecha_emision DESC", conn)
        conn.close()
        
        if not df.empty:
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame()

def parse_uploaded_file(contents, filename):
    """Parsea archivo subido"""
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if 'xls' in filename.lower():
            # Intentar como Excel primero
            try:
                df = pd.read_excel(io.BytesIO(decoded))
            except:
                # Si falla, intentar como HTML
                df = pd.read_html(io.BytesIO(decoded))[0]
        elif 'html' in filename.lower():
            df = pd.read_html(io.BytesIO(decoded))[0]
        else:
            return None, "Formato de archivo no soportado"
        
        # Mapeo de columnas esperado (basado en archivo real)
        column_mapping = {
            'Servicio': 'servicio',
            'Articulo': 'categoria',  # Usar Articulo, no Concepto (que está vacío)
            'Derechos': 'costo_unitario',
            'No. de trámites': 'num_tramites',
            'Importe USD': 'ingresos_totales',
            'Fecha recaudación': 'fecha_emision',
            'No. cancelados': 'formas_canceladas'
        }
        
        # Verificar que las columnas necesarias existen
        required_columns = list(column_mapping.keys())
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Columnas faltantes en el archivo: {', '.join(missing_columns)}. Columnas disponibles: {', '.join(df.columns)}"
        
        # Renombrar columnas
        df = df.rename(columns=column_mapping)
        
        # Filtrar solo las columnas que necesitamos
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
        return None, f"Error procesando archivo: {str(e)}"

# Layout de la aplicación
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🚀 Visor de Servicios Consulares", className="text-primary mb-1"),
            html.P("Sistema de análisis de datos consulares", className="text-muted mb-4")
        ])
    ]),
    
    # Navegación con pestañas
    dbc.Tabs([
        # Pestaña de Estado
        dbc.Tab(label="📊 Estado del Sistema", tab_id="status-tab"),
        
        # Pestaña de Carga de Datos
        dbc.Tab(label="📁 Cargar Datos", tab_id="upload-tab"),
        
        # Pestaña de Dashboard
        dbc.Tab(label="📈 Dashboard", tab_id="dashboard-tab"),
        
        # Pestaña de Datos
        dbc.Tab(label="📋 Ver Datos", tab_id="data-tab")
        
    ], id="main-tabs", active_tab="status-tab"),
    
    html.Hr(),
    
    # Contenido dinámico
    html.Div(id="tab-content"),
    
    # Stores
    dcc.Store(id="data-store"),
    dcc.Interval(id="interval-component", interval=5000, n_intervals=0)
    
], fluid=True, className="py-3")

# Callbacks
@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "status-tab":
        return render_status_tab()
    elif active_tab == "upload-tab":
        return render_upload_tab()
    elif active_tab == "dashboard-tab":
        return render_dashboard_tab()
    elif active_tab == "data-tab":
        return render_data_tab()
    return html.Div("Selecciona una pestaña")

def render_status_tab():
    """Renderiza pestaña de estado"""
    summary = get_data_summary()
    
    if "error" in summary:
        alert = dbc.Alert(f"❌ Error: {summary['error']}", color="danger")
    elif summary.get("total_registros", 0) == 0:
        alert = dbc.Alert("⚠️ No hay datos cargados. Ve a la pestaña 'Cargar Datos'", color="warning")
    else:
        alert = dbc.Alert("✅ Sistema funcionando correctamente", color="success")
    
    cards = []
    if summary.get("total_registros", 0) > 0:
        cards = [
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{summary['total_registros']:,}", className="text-primary"),
                        html.P("Registros Totales", className="mb-0")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${summary['total_ingresos']:,.2f}", className="text-success"),
                        html.P("Ingresos Totales", className="mb-0")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{summary['total_tramites']:,}", className="text-info"),
                        html.P("Trámites Totales", className="mb-0")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{summary['servicios_unicos']:,}", className="text-warning"),
                        html.P("Servicios Únicos", className="mb-0")
                    ])
                ])
            ], md=3)
        ]
    
    return html.Div([
        alert,
        dbc.Row(cards, className="mb-4"),
        
        dbc.Card([
            dbc.CardHeader("📋 Información del Sistema"),
            dbc.CardBody([
                html.P(f"🗂️ Base de datos: {DB_PATH}"),
                html.P(f"📅 Rango de fechas: {summary.get('fecha_min', 'N/A')} - {summary.get('fecha_max', 'N/A')}"),
                html.P(f"🕒 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            ])
        ])
    ])

def render_upload_tab():
    """Renderiza pestaña de carga"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📤 Cargar Archivo de Datos"),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                                html.H4('Arrastra archivos aquí o haz clic para seleccionar'),
                                html.P('Formatos soportados: .xls, .xlsx, .html')
                            ], className="text-center py-4"),
                            style={
                                'width': '100%',
                                'height': '200px',
                                'lineHeight': '200px',
                                'borderWidth': '2px',
                                'borderStyle': 'dashed',
                                'borderRadius': '10px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            multiple=False
                        ),
                        
                        html.Div(id="upload-status", className="mt-3")
                    ])
                ])
            ], md=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("💡 Instrucciones"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li("Arrastra o selecciona un archivo .xls, .xlsx o .html"),
                            html.Li("El archivo debe tener las columnas esperadas"),
                            html.Li("Los datos se cargarán automáticamente"),
                            html.Li("Ve al Dashboard para visualizar los datos")
                        ])
                    ])
                ])
            ], md=4)
        ])
    ])

def render_dashboard_tab():
    """Renderiza pestaña de dashboard"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📈 Evolución de Ingresos"),
                    dbc.CardBody([
                        dcc.Graph(id="income-chart")
                    ])
                ])
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Top Servicios"),
                    dbc.CardBody([
                        dcc.Graph(id="services-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🎯 Análisis Temporal"),
                    dbc.CardBody([
                        dcc.Graph(id="temporal-chart")
                    ])
                ])
            ])
        ])
    ])

def render_data_tab():
    """Renderiza pestaña de datos"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader("📋 Datos Cargados"),
            dbc.CardBody([
                html.Div(id="data-table")
            ])
        ])
    ])

@app.callback(
    Output("upload-status", "children"),
    Output("data-store", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def handle_file_upload(contents, filename):
    if contents is None:
        return "", {}
    
    df, error = parse_uploaded_file(contents, filename)
    
    if error:
        return dbc.Alert(f"❌ {error}", color="danger"), {}
    
    try:
        # Insertar en base de datos
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('consular_data', conn, if_exists='append', index=False)
        conn.close()
        
        success_msg = dbc.Alert(
            f"✅ Archivo '{filename}' cargado exitosamente. {len(df)} registros insertados.",
            color="success"
        )
        
        return success_msg, {"uploaded": True, "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        error_msg = dbc.Alert(f"❌ Error guardando datos: {str(e)}", color="danger")
        return error_msg, {}

@app.callback(
    [Output("income-chart", "figure"),
     Output("services-chart", "figure"),
     Output("temporal-chart", "figure")],
    [Input("data-store", "data"),
     Input("interval-component", "n_intervals")]
)
def update_dashboard_charts(data_store, n_intervals):
    df = load_data_from_db()
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No hay datos disponibles", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig, empty_fig
    
    # Gráfico de ingresos por fecha
    df_daily = df.groupby('fecha_emision').agg({
        'ingresos_totales': 'sum',
        'num_tramites': 'sum'
    }).reset_index()
    
    income_fig = px.line(df_daily, x='fecha_emision', y='ingresos_totales',
                        title='Evolución de Ingresos Diarios')
    
    # Top servicios
    df_services = df.groupby('servicio').agg({
        'ingresos_totales': 'sum'
    }).reset_index().nlargest(10, 'ingresos_totales')
    
    services_fig = px.bar(df_services, x='ingresos_totales', y='servicio',
                         title='Top 10 Servicios por Ingresos', orientation='h')
    
    # Análisis temporal
    temporal_fig = px.scatter(df, x='fecha_emision', y='ingresos_totales',
                             size='num_tramites', color='categoria',
                             title='Análisis Temporal por Categoría')
    
    return income_fig, services_fig, temporal_fig

@app.callback(
    Output("data-table", "children"),
    [Input("data-store", "data"),
     Input("interval-component", "n_intervals")]
)
def update_data_table(data_store, n_intervals):
    df = load_data_from_db()
    
    if df.empty:
        return dbc.Alert("No hay datos para mostrar", color="info")
    
    # Mostrar últimos 100 registros
    df_display = df.head(100).copy()
    
    # Formatear columnas para mostrar
    display_columns = ['servicio', 'categoria', 'num_tramites', 'ingresos_totales', 'fecha_emision']
    df_display = df_display[display_columns]
    
    return dash_table.DataTable(
        data=df_display.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df_display.columns],
        page_size=20,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    )

if __name__ == '__main__':
    # Inicializar base de datos
    init_database()
    
    # Ejecutar aplicación
    app.run(
        host='127.0.0.1',
        port=8050,
        debug=True
    )