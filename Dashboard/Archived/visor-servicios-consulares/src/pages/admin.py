"""
Página de administración del sistema
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import os
import base64
import io
from typing import Dict, Any, List, Optional

from ..core import DatabaseManager, AnalyticsEngine
from ..components import (
    create_page_header, create_alert_message, create_summary_stats_card,
    create_loading_spinner, create_progress_bar, create_tab_container,
    create_export_button
)
from ..config.settings import settings
from ..config.constants import SUPPORTED_FILE_EXTENSIONS, HTML_COLUMN_MAPPING


class AdminPage:
    """Controlador de la página de administración"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine(self.db)
    
    def get_layout(self) -> html.Div:
        """Retorna el layout de la página de administración"""
        
        return html.Div([
            # Encabezado
            create_page_header(
                title="🔧 Administración del Sistema",
                subtitle="Gestión de archivos, configuración y mantenimiento",
                actions=[
                    dbc.Button(
                        "🔄 Actualizar Estado",
                        id="admin-refresh",
                        color="primary",
                        outline=True,
                        size="sm"
                    )
                ]
            ),
            
            # Alertas
            html.Div(id="admin-alerts"),
            
            # Contenido principal con pestañas
            self._create_admin_content(),
            
            # Stores
            dcc.Store(id="admin-data-store"),
            dcc.Store(id="file-upload-store")
        ])
    
    def _create_admin_content(self) -> html.Div:
        """Crea contenido principal de administración"""
        
        tabs = [
            {
                "id": "files-tab",
                "label": "📁 Gestión de Archivos",
                "content": self._create_files_tab()
            },
            {
                "id": "system-tab",
                "label": "⚙️ Sistema",
                "content": self._create_system_tab()
            },
            {
                "id": "maintenance-tab",
                "label": "🔧 Mantenimiento",
                "content": self._create_maintenance_tab()
            }
        ]
        
        return create_tab_container(
            tabs=tabs,
            active_tab="files-tab",
            tab_container_id="admin-main"
        )
    
    def _create_files_tab(self) -> html.Div:
        """Crea pestaña de gestión de archivos"""
        
        return html.Div([
            # Carga de archivos
            dbc.Card([
                dbc.CardHeader("📤 Cargar Archivos de Datos"),
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                            html.H4('Arrastra archivos aquí o haz clic para seleccionar'),
                            html.P(
                                f'Formatos soportados: {", ".join(SUPPORTED_FILE_EXTENSIONS)}',
                                className="text-muted"
                            )
                        ]),
                        style={
                            'width': '100%',
                            'height': '200px',
                            'lineHeight': '200px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'margin': '10px',
                            'backgroundColor': '#f8f9fa'
                        },
                        multiple=True
                    ),
                    html.Div(id='upload-output'),
                    html.Div(id='upload-progress')
                ])
            ], className="mb-4"),
            
            # Lista de archivos cargados
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📋 Archivos en el Sistema", className="mb-0"),
                    dbc.Button(
                        "🔄 Actualizar Lista",
                        id="refresh-file-list",
                        size="sm",
                        outline=True,
                        className="float-end"
                    )
                ]),
                dbc.CardBody([
                    html.Div(id="file-list-content")
                ])
            ], className="mb-4"),
            
            # Búsqueda de archivos en directorio
            dbc.Card([
                dbc.CardHeader("🔍 Búsqueda de Archivos"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id="search-directory-input",
                                    placeholder="Ruta del directorio a buscar...",
                                    value="./data"
                                ),
                                dbc.Button(
                                    "🔍 Buscar",
                                    id="search-files-btn",
                                    color="primary"
                                )
                            ])
                        ], md=10),
                        dbc.Col([
                            dbc.Button(
                                "📤 Cargar Encontrados",
                                id="load-found-files-btn",
                                color="success",
                                disabled=True
                            )
                        ], md=2)
                    ]),
                    html.Div(id="found-files-content", className="mt-3")
                ])
            ])
        ])
    
    def _create_system_tab(self) -> html.Div:
        """Crea pestaña de información del sistema"""
        
        return html.Div([
            # Estado del sistema
            dbc.Row([
                dbc.Col([
                    html.Div(id="system-stats-card")
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🗄️ Base de Datos"),
                        dbc.CardBody([
                            html.Div(id="database-info")
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            # Configuración actual
            dbc.Card([
                dbc.CardHeader("⚙️ Configuración del Sistema"),
                dbc.CardBody([
                    html.Div(id="system-config-display")
                ])
            ], className="mb-4"),
            
            # Logs del sistema
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📜 Registro de Actividad", className="mb-0"),
                    dbc.Button(
                        "🔄 Actualizar",
                        id="refresh-logs",
                        size="sm",
                        outline=True,
                        className="float-end"
                    )
                ]),
                dbc.CardBody([
                    html.Div(id="system-logs", 
                           style={'maxHeight': '300px', 'overflowY': 'scroll'})
                ])
            ])
        ])
    
    def _create_maintenance_tab(self) -> html.Div:
        """Crea pestaña de mantenimiento"""
        
        return html.Div([
            # Acciones de mantenimiento
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("💾 Backup y Restauración"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "💾 Crear Backup",
                                        id="create-backup-btn",
                                        color="success",
                                        className="w-100 mb-2"
                                    ),
                                    dbc.Button(
                                        "🗑️ Limpiar Backups Antiguos",
                                        id="cleanup-backups-btn", 
                                        color="warning",
                                        outline=True,
                                        className="w-100"
                                    )
                                ])
                            ]),
                            html.Div(id="backup-status", className="mt-3")
                        ])
                    ])
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🧹 Limpieza del Sistema"),
                        dbc.CardBody([
                            dbc.Button(
                                "🗑️ Limpiar Cache",
                                id="clear-cache-btn",
                                color="warning",
                                outline=True,
                                className="w-100 mb-2"
                            ),
                            dbc.Button(
                                "📊 Optimizar Base de Datos",
                                id="optimize-db-btn",
                                color="info",
                                outline=True,
                                className="w-100 mb-2"
                            ),
                            dbc.Button(
                                "🗂️ Limpiar Archivos Temporales",
                                id="clean-temp-btn",
                                color="secondary",
                                outline=True,
                                className="w-100"
                            ),
                            html.Div(id="maintenance-status", className="mt-3")
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            # Exportación masiva
            dbc.Card([
                dbc.CardHeader("📤 Exportación Masiva"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Formato de exportación:", className="fw-bold"),
                            dcc.Dropdown(
                                id="export-format-selector",
                                options=[
                                    {"label": "📄 CSV", "value": "csv"},
                                    {"label": "📊 Excel", "value": "xlsx"}, 
                                    {"label": "📋 JSON", "value": "json"}
                                ],
                                value="csv",
                                clearable=False
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Período:", className="fw-bold"),
                            dcc.DatePickerRange(
                                id="export-date-range",
                                display_format='DD/MM/YYYY'
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Acción:", className="fw-bold"),
                            html.Br(),
                            dbc.Button(
                                "📤 Exportar Todo",
                                id="export-all-btn",
                                color="success"
                            )
                        ], md=4)
                    ]),
                    html.Div(id="export-status", className="mt-3")
                ])
            ])
        ])


# Instancia global
admin_page = AdminPage()


# Callbacks para funcionalidad de administración
@callback(
    [Output("system-stats-card", "children"),
     Output("database-info", "children"),
     Output("admin-data-store", "data")],
    [Input("admin-refresh", "n_clicks"),
     Input("refresh-file-list", "n_clicks")]
)
def update_system_info(refresh_clicks, file_refresh_clicks):
    """Actualiza información del sistema"""
    
    try:
        # Obtener estadísticas de la base de datos
        db_stats = admin_page.db.get_summary_stats()
        date_range = admin_page.db.get_date_range()
        
        # Crear tarjeta de estadísticas
        stats_card = create_summary_stats_card(db_stats)
        
        # Información de la base de datos
        db_size = 0
        if os.path.exists(admin_page.db.db_path):
            db_size = os.path.getsize(admin_page.db.db_path) / (1024 * 1024)  # MB
        
        db_info = html.Div([
            html.P([html.Strong("Ruta: "), html.Code(admin_page.db.db_path)]),
            html.P([html.Strong("Tamaño: "), f"{db_size:.2f} MB"]),
            html.P([html.Strong("Rango de fechas: "), 
                   f"{date_range.get('fecha_min', 'N/A')} - {date_range.get('fecha_max', 'N/A')}"]),
            html.P([html.Strong("Estado: "), 
                   dbc.Badge("✅ Operativa", color="success")])
        ])
        
        # Datos para store
        store_data = {
            'db_stats': db_stats,
            'db_info': {
                'path': admin_page.db.db_path,
                'size_mb': db_size,
                'date_range': date_range
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return stats_card, db_info, store_data
        
    except Exception as e:
        error_card = create_alert_message(f"Error obteniendo información: {str(e)}", "danger")
        return error_card, error_card, {}


@callback(
    Output("file-list-content", "children"),
    [Input("admin-data-store", "data"),
     Input("refresh-file-list", "n_clicks")]
)
def update_file_list(data_store, refresh_clicks):
    """Actualiza lista de archivos cargados"""
    
    try:
        file_history = admin_page.db.get_file_history()
        
        if file_history.empty:
            return create_alert_message("No hay archivos cargados en el sistema", "info")
        
        # Crear tabla de archivos
        table_rows = []
        for _, file_record in file_history.iterrows():
            status_color = "success" if file_record['estado'] == 'exitoso' else "danger"
            
            table_rows.append(
                html.Tr([
                    html.Td(file_record['nombre_archivo']),
                    html.Td(file_record['fecha_carga'].strftime('%d/%m/%Y %H:%M')),
                    html.Td(f"{file_record['registros_insertados']:,}"),
                    html.Td(f"{file_record['registros_duplicados']:,}"),
                    html.Td(dbc.Badge(file_record['estado'], color=status_color)),
                    html.Td([
                        dbc.Button(
                            "🗑️",
                            id=f"delete-file-{file_record['id']}",
                            size="sm",
                            color="danger",
                            outline=True,
                            title="Eliminar archivo"
                        )
                    ])
                ])
            )
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Archivo"),
                    html.Th("Fecha Carga"),
                    html.Th("Insertados"),
                    html.Th("Duplicados"),
                    html.Th("Estado"),
                    html.Th("Acciones")
                ])
            ]),
            html.Tbody(table_rows)
        ], bordered=True, hover=True, responsive=True)
        
        return table
        
    except Exception as e:
        return create_alert_message(f"Error cargando lista de archivos: {str(e)}", "danger")


@callback(
    Output('upload-output', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')]
)
def handle_file_upload(list_of_contents, list_of_names, list_of_dates):
    """Maneja la carga de archivos"""
    
    if list_of_contents is None:
        return html.Div()
    
    results = []
    
    for content, name, date in zip(list_of_contents, list_of_names, list_of_dates):
        try:
            # Decodificar archivo
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            # Verificar extensión
            if not any(name.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTENSIONS):
                results.append(
                    create_alert_message(
                        f"❌ {name}: Formato no soportado",
                        "danger"
                    )
                )
                continue
            
            # Procesar archivo según tipo
            df = None
            if name.lower().endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif name.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(decoded))
            elif name.lower().endswith('.html'):
                df = pd.read_html(io.StringIO(decoded.decode('utf-8')))[0]
            
            if df is None or df.empty:
                results.append(
                    create_alert_message(
                        f"❌ {name}: Archivo vacío o no se pudo procesar",
                        "danger"
                    )
                )
                continue
            
            # Mapear columnas si es HTML
            if name.lower().endswith('.html'):
                df = df.rename(columns=HTML_COLUMN_MAPPING)
            
            # Verificar columnas requeridas
            required_cols = ['servicio', 'fecha_emision', 'ingresos_totales', 'num_tramites']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                results.append(
                    create_alert_message(
                        f"❌ {name}: Faltan columnas: {', '.join(missing_cols)}",
                        "danger"
                    )
                )
                continue
            
            # Limpiar y preparar datos
            df = df.fillna(0)
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'], errors='coerce')
            df = df.dropna(subset=['fecha_emision'])
            
            # Insertar en base de datos
            insert_result = admin_page.db.insert_data(df, name)
            
            results.append(
                create_alert_message(
                    f"✅ {name}: {insert_result['insertados']} registros insertados, "
                    f"{insert_result['duplicados']} duplicados",
                    "success"
                )
            )
            
        except Exception as e:
            results.append(
                create_alert_message(
                    f"❌ Error procesando {name}: {str(e)}",
                    "danger"
                )
            )
    
    return html.Div(results)


@callback(
    Output("backup-status", "children"),
    [Input("create-backup-btn", "n_clicks"),
     Input("cleanup-backups-btn", "n_clicks")]
)
def handle_backup_operations(create_clicks, cleanup_clicks):
    """Maneja operaciones de backup"""
    
    if not ctx.triggered:
        return html.Div()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if button_id == "create-backup-btn" and create_clicks:
            backup_path = admin_page.db.backup_database()
            return create_alert_message(
                f"✅ Backup creado exitosamente: {backup_path}",
                "success"
            )
        
        elif button_id == "cleanup-backups-btn" and cleanup_clicks:
            admin_page.db.cleanup_old_backups()
            return create_alert_message(
                "✅ Backups antiguos eliminados",
                "success"
            )
        
    except Exception as e:
        return create_alert_message(
            f"❌ Error en operación de backup: {str(e)}",
            "danger"
        )
    
    return html.Div()


@callback(
    Output("system-config-display", "children"),
    [Input("admin-data-store", "data")]
)
def display_system_config(data_store):
    """Muestra configuración del sistema"""
    
    config_items = [
        {"label": "Título de la aplicación", "value": settings.app.title},
        {"label": "Modo debug", "value": str(settings.app.debug)},
        {"label": "Puerto", "value": str(settings.app.port)},
        {"label": "Base de datos", "value": settings.database.path},
        {"label": "Directorio de backups", "value": settings.database.backup_dir},
        {"label": "Tema UI", "value": settings.ui.theme},
        {"label": "Altura de gráficas", "value": f"{settings.ui.chart_height}px"},
        {"label": "Directorio de exportación", "value": settings.export.export_dir}
    ]
    
    config_rows = []
    for item in config_items:
        config_rows.append(
            dbc.Row([
                dbc.Col(html.Strong(item["label"] + ":"), width=6),
                dbc.Col(html.Code(item["value"]), width=6)
            ], className="mb-2")
        )
    
    return html.Div(config_rows)