"""
Página de reportes y exportación avanzada
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, date, timedelta
import io
import base64
from typing import Dict, Any, List, Optional

from ..core import DatabaseManager, AnalyticsEngine, ChartFactory
from ..components import (
    create_page_header, create_alert_message, create_date_range_picker,
    create_service_selector, create_temporal_grouping_selector,
    create_tab_container, create_export_button, create_progress_bar
)
from ..config.settings import settings


class ReportsPage:
    """Controlador de la página de reportes"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine(self.db)
        self.charts = ChartFactory()
    
    def get_layout(self) -> html.Div:
        """Retorna el layout de la página de reportes"""
        
        return html.Div([
            # Encabezado
            create_page_header(
                title="📈 Reportes y Análisis Avanzado",
                subtitle="Exportación, predicciones y análisis detallado",
                actions=[
                    dbc.Button(
                        "📊 Generar Reporte Completo",
                        id="generate-full-report",
                        color="success",
                        size="sm"
                    )
                ]
            ),
            
            # Alertas
            html.Div(id="reports-alerts"),
            
            # Contenido principal
            self._create_reports_content(),
            
            # Stores
            dcc.Store(id="reports-data-store"),
            dcc.Store(id="report-config-store"),
            
            # Download componente para archivos
            dcc.Download(id="download-report")
        ])
    
    def _create_reports_content(self) -> html.Div:
        """Crea contenido principal de reportes"""
        
        tabs = [
            {
                "id": "export-tab",
                "label": "📤 Exportación Personalizada",
                "content": self._create_export_tab()
            },
            {
                "id": "predictions-tab",
                "label": "🔮 Análisis Predictivo",
                "content": self._create_predictions_tab()
            },
            {
                "id": "advanced-tab",
                "label": "📊 Análisis Avanzado",
                "content": self._create_advanced_tab()
            },
            {
                "id": "scheduled-tab",
                "label": "⏰ Reportes Programados",
                "content": self._create_scheduled_tab()
            }
        ]
        
        return create_tab_container(
            tabs=tabs,
            active_tab="export-tab",
            tab_container_id="reports-main"
        )
    
    def _create_export_tab(self) -> html.Div:
        """Crea pestaña de exportación personalizada"""
        
        return html.Div([
            # Configuración de exportación
            dbc.Card([
                dbc.CardHeader("⚙️ Configuración de Exportación"),
                dbc.CardBody([
                    dbc.Row([
                        # Filtros temporales
                        dbc.Col([
                            create_date_range_picker(
                                start_date=date.today() - timedelta(days=365),
                                end_date=date.today(),
                                picker_id="export-date-range",
                                label="Período de datos:"
                            )
                        ], md=6),
                        
                        # Selector de servicio
                        dbc.Col([
                            create_service_selector(
                                services=[],  # Se llenará dinámicamente
                                selector_id="export-service-filter",
                                label="Servicios:",
                                include_all=True
                            )
                        ], md=6)
                    ]),
                    
                    dbc.Row([
                        # Formato de exportación
                        dbc.Col([
                            html.Label("Formato de exportación:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="export-format",
                                options=[
                                    {"label": "📄 CSV", "value": "csv"},
                                    {"label": "📊 Excel (XLSX)", "value": "xlsx"},
                                    {"label": "📋 JSON", "value": "json"},
                                    {"label": "📃 PDF Reporte", "value": "pdf"}
                                ],
                                value="csv",
                                clearable=False
                            )
                        ], md=4),
                        
                        # Nivel de detalle
                        dbc.Col([
                            html.Label("Nivel de detalle:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="export-detail-level",
                                options=[
                                    {"label": "📊 Resumen ejecutivo", "value": "summary"},
                                    {"label": "📈 Datos agregados", "value": "aggregated"},
                                    {"label": "📋 Datos completos", "value": "detailed"}
                                ],
                                value="aggregated",
                                clearable=False
                            )
                        ], md=4),
                        
                        # Incluir gráficas
                        dbc.Col([
                            html.Label("Opciones adicionales:", className="form-label fw-bold"),
                            dbc.Checklist(
                                id="export-options",
                                options=[
                                    {"label": "📊 Incluir gráficas", "value": "charts"},
                                    {"label": "📅 Análisis semanal", "value": "weekly"},
                                    {"label": "🔮 Predicciones", "value": "predictions"}
                                ],
                                value=["charts"],
                                inline=True
                            )
                        ], md=4)
                    ], className="mt-3")
                ])
            ], className="mb-4"),
            
            # Vista previa de datos
            dbc.Card([
                dbc.CardHeader([
                    html.H5("👁️ Vista Previa de Datos", className="mb-0"),
                    dbc.Button(
                        "🔄 Actualizar Vista Previa",
                        id="refresh-export-preview",
                        size="sm",
                        outline=True,
                        className="float-end"
                    )
                ]),
                dbc.CardBody([
                    html.Div(id="export-preview-content"),
                    html.Div(id="export-stats", className="mt-3")
                ])
            ], className="mb-4"),
            
            # Botones de acción
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "📤 Exportar Datos",
                                id="execute-export",
                                color="success",
                                size="lg",
                                className="w-100"
                            )
                        ], md=6),
                        dbc.Col([
                            dbc.Button(
                                "📧 Enviar por Email",
                                id="email-export",
                                color="info",
                                outline=True,
                                size="lg",
                                className="w-100",
                                disabled=True  # Feature para futuro
                            )
                        ], md=6)
                    ])
                ])
            ])
        ])
    
    def _create_predictions_tab(self) -> html.Div:
        """Crea pestaña de análisis predictivo"""
        
        return html.Div([
            # Configuración de predicción
            dbc.Card([
                dbc.CardHeader("🔮 Configuración de Predicción"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Servicio a predecir:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="prediction-service-selector",
                                placeholder="Seleccionar servicio o todos..."
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Períodos a predecir:", className="form-label fw-bold"),
                            dcc.Slider(
                                id="prediction-periods",
                                min=1,
                                max=12,
                                step=1,
                                value=3,
                                marks={i: f"{i} meses" for i in [1, 3, 6, 12]},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "🔮 Generar Predicción",
                                id="generate-prediction",
                                color="primary",
                                className="mt-3"
                            )
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Resultados de predicción
            html.Div(id="prediction-results")
        ])
    
    def _create_advanced_tab(self) -> html.Div:
        """Crea pestaña de análisis avanzado"""
        
        return html.Div([
            # Análisis de correlaciones
            dbc.Card([
                dbc.CardHeader("🔗 Análisis de Correlaciones"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Servicios a correlacionar:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="correlation-services",
                                multi=True,
                                placeholder="Seleccionar servicios..."
                            )
                        ], md=8),
                        dbc.Col([
                            html.Label("Acción:", className="form-label fw-bold"),
                            html.Br(),
                            dbc.Button(
                                "📊 Analizar",
                                id="analyze-correlations",
                                color="primary"
                            )
                        ], md=4)
                    ]),
                    html.Div(id="correlation-results", className="mt-3")
                ])
            ], className="mb-4"),
            
            # Análisis de estacionalidad
            dbc.Card([
                dbc.CardHeader("🌀 Análisis de Estacionalidad"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Período de análisis:", className="form-label fw-bold"),
                            create_date_range_picker(
                                picker_id="seasonality-date-range",
                                label=""
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Métrica:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="seasonality-metric",
                                options=[
                                    {"label": "💰 Ingresos", "value": "ingresos_totales"},
                                    {"label": "📄 Trámites", "value": "num_tramites"}
                                ],
                                value="ingresos_totales"
                            )
                        ], md=6)
                    ]),
                    dbc.Button(
                        "🌀 Analizar Estacionalidad",
                        id="analyze-seasonality",
                        color="primary",
                        className="mt-3"
                    ),
                    html.Div(id="seasonality-results", className="mt-3")
                ])
            ], className="mb-4"),
            
            # Detección de anomalías
            dbc.Card([
                dbc.CardHeader("🚨 Detección de Anomalías"),
                dbc.CardBody([
                    html.P(
                        "Identifica días o períodos con actividad inusual (muy alta o muy baja).",
                        className="text-muted"
                    ),
                    dbc.Button(
                        "🚨 Detectar Anomalías",
                        id="detect-anomalies",
                        color="warning",
                        outline=True
                    ),
                    html.Div(id="anomalies-results", className="mt-3")
                ])
            ])
        ])
    
    def _create_scheduled_tab(self) -> html.Div:
        """Crea pestaña de reportes programados"""
        
        return html.Div([
            # Configuración de reportes programados
            dbc.Card([
                dbc.CardHeader("⏰ Configurar Reporte Programado"),
                dbc.CardBody([
                    dbc.Alert(
                        "🚧 Funcionalidad en desarrollo. Próximamente podrás programar reportes automáticos.",
                        color="info"
                    ),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Frecuencia:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="schedule-frequency",
                                options=[
                                    {"label": "📅 Diario", "value": "daily"},
                                    {"label": "📊 Semanal", "value": "weekly"},
                                    {"label": "🗓️ Mensual", "value": "monthly"}
                                ],
                                placeholder="Seleccionar frecuencia...",
                                disabled=True
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Formato:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id="schedule-format",
                                options=[
                                    {"label": "📧 Email PDF", "value": "email_pdf"},
                                    {"label": "📁 Archivo local", "value": "local_file"}
                                ],
                                placeholder="Seleccionar formato...",
                                disabled=True
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Estado:", className="form-label fw-bold"),
                            html.Br(),
                            dbc.Button(
                                "💾 Guardar Configuración",
                                id="save-schedule",
                                color="success",
                                disabled=True
                            )
                        ], md=4)
                    ])
                ])
            ], className="mb-4"),
            
            # Lista de reportes programados
            dbc.Card([
                dbc.CardHeader("📋 Reportes Programados Activos"),
                dbc.CardBody([
                    dbc.Alert(
                        "No hay reportes programados configurados.",
                        color="light"
                    )
                ])
            ])
        ])


# Instancia global
reports_page = ReportsPage()


# Callbacks para funcionalidad de reportes
@callback(
    [Output("export-preview-content", "children"),
     Output("export-stats", "children")],
    [Input("refresh-export-preview", "n_clicks"),
     Input("export-date-range", "start_date"),
     Input("export-date-range", "end_date"),
     Input("export-service-filter", "value")]
)
def update_export_preview(refresh_clicks, start_date, end_date, service_filter):
    """Actualiza vista previa de exportación"""
    
    try:
        # Cargar datos según filtros
        df = reports_page.db.load_data(start_date, end_date)
        
        if service_filter and service_filter != "ALL":
            df = df[df['servicio'] == service_filter]
        
        if df.empty:
            return (
                create_alert_message("No hay datos para los filtros seleccionados", "info"),
                html.Div()
            )
        
        # Mostrar muestra de datos (primeras 10 filas)
        preview_df = df.head(10)
        
        # Crear tabla de vista previa
        table_header = [
            html.Thead([
                html.Tr([
                    html.Th(col) for col in preview_df.columns[:6]  # Primeras 6 columnas
                ])
            ])
        ]
        
        table_body = [
            html.Tbody([
                html.Tr([
                    html.Td(str(row[col])[:50] + "..." if len(str(row[col])) > 50 else str(row[col]))
                    for col in preview_df.columns[:6]
                ]) for _, row in preview_df.iterrows()
            ])
        ]
        
        preview_table = dbc.Table(
            table_header + table_body,
            bordered=True,
            hover=True,
            responsive=True,
            size="sm"
        )
        
        # Estadísticas
        stats = html.Div([
            dbc.Row([
                dbc.Col([
                    html.P([html.Strong("Total de registros: "), f"{len(df):,}"])
                ], md=3),
                dbc.Col([
                    html.P([html.Strong("Ingresos totales: "), f"${df['ingresos_totales'].sum():,.2f}"])
                ], md=3),
                dbc.Col([
                    html.P([html.Strong("Trámites totales: "), f"{df['num_tramites'].sum():,}"])
                ], md=3),
                dbc.Col([
                    html.P([html.Strong("Servicios únicos: "), f"{df['servicio'].nunique()}"])
                ], md=3)
            ])
        ])
        
        return preview_table, stats
        
    except Exception as e:
        error_msg = create_alert_message(f"Error cargando vista previa: {str(e)}", "danger")
        return error_msg, html.Div()


@callback(
    Output("download-report", "data"),
    [Input("execute-export", "n_clicks")],
    [State("export-date-range", "start_date"),
     State("export-date-range", "end_date"),
     State("export-service-filter", "value"),
     State("export-format", "value"),
     State("export-detail-level", "value"),
     State("export-options", "value")]
)
def export_data(n_clicks, start_date, end_date, service_filter, export_format, 
                detail_level, export_options):
    """Exporta datos según configuración"""
    
    if not n_clicks:
        return dash.no_update
    
    try:
        # Cargar datos
        df = reports_page.db.load_data(start_date, end_date)
        
        if service_filter and service_filter != "ALL":
            df = df[df['servicio'] == service_filter]
        
        if df.empty:
            return dash.no_update
        
        # Procesar según nivel de detalle
        if detail_level == "summary":
            # Resumen ejecutivo
            kpis = reports_page.analytics.get_kpis(start_date, end_date)
            export_df = pd.DataFrame([kpis])
        elif detail_level == "aggregated":
            # Datos agregados por servicio
            export_df = df.groupby('servicio').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).reset_index()
        else:
            # Datos completos
            export_df = df
        
        # Generar archivo según formato
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == "csv":
            filename = f"reporte_consular_{timestamp}.csv"
            return dcc.send_data_frame(export_df.to_csv, filename, index=False)
        
        elif export_format == "xlsx":
            filename = f"reporte_consular_{timestamp}.xlsx"
            return dcc.send_data_frame(export_df.to_excel, filename, index=False)
        
        elif export_format == "json":
            filename = f"reporte_consular_{timestamp}.json"
            return dcc.send_data_frame(
                lambda df: df.to_json(orient='records', indent=2),
                filename
            )
        
    except Exception as e:
        return dash.no_update


@callback(
    Output("prediction-results", "children"),
    [Input("generate-prediction", "n_clicks")],
    [State("prediction-service-selector", "value"),
     State("prediction-periods", "value")]
)
def generate_predictions(n_clicks, service, periods):
    """Genera predicciones basadas en datos históricos"""
    
    if not n_clicks:
        return html.Div()
    
    try:
        # Generar predicción
        prediction_result = reports_page.analytics.predict_next_period(
            service=service if service and service != "ALL" else None,
            periods=periods
        )
        
        if 'error' in prediction_result:
            return create_alert_message(prediction_result['error'], "warning")
        
        # Crear gráfica de predicción
        historical_data = prediction_result['historical_data']
        predictions = prediction_result['predictions']
        
        # Combinar datos históricos y predicciones
        historical_periods = historical_data['periodo_str'].tolist()
        historical_ingresos = historical_data['ingresos_totales'].tolist()
        
        # Generar períodos futuros
        last_period = pd.to_datetime(historical_periods[-1])
        future_periods = []
        for i in range(1, periods + 1):
            future_period = last_period + pd.DateOffset(months=i)
            future_periods.append(future_period.strftime('%Y-%m'))
        
        # Crear gráfica
        fig = reports_page.charts.create_multi_line_chart(
            data_series=[
                {
                    'data': pd.DataFrame({
                        'periodo': historical_periods,
                        'ingresos': historical_ingresos
                    }),
                    'y_col': 'ingresos',
                    'name': 'Histórico',
                    'color': reports_page.charts.colors['primary']
                },
                {
                    'data': pd.DataFrame({
                        'periodo': future_periods,
                        'ingresos': predictions['ingresos']
                    }),
                    'y_col': 'ingresos',
                    'name': 'Predicción',
                    'color': reports_page.charts.colors['warning']
                }
            ],
            x_col='periodo',
            title=f"Predicción de Ingresos - {periods} meses"
        )
        
        # Información de tendencias
        trends = prediction_result['trends']
        trend_info = html.Div([
            html.H5("📈 Análisis de Tendencias"),
            html.P([
                html.Strong("Tendencia de ingresos: "),
                f"${trends['ingresos_slope']:,.2f} por mes ",
                "📈" if trends['ingresos_slope'] > 0 else "📉"
            ]),
            html.P([
                html.Strong("Tendencia de trámites: "),
                f"{trends['tramites_slope']:,.1f} trámites por mes ",
                "📈" if trends['tramites_slope'] > 0 else "📉"
            ])
        ])
        
        return html.Div([
            dcc.Graph(figure=fig),
            trend_info
        ])
        
    except Exception as e:
        return create_alert_message(f"Error generando predicción: {str(e)}", "danger")


# Callback para llenar selectores dinámicamente
@callback(
    [Output("export-service-filter", "options"),
     Output("prediction-service-selector", "options")],
    [Input("reports-alerts", "children")]  # Trigger dummy
)
def update_service_selectors(trigger):
    """Actualiza opciones de servicios en selectores"""
    
    try:
        services = reports_page.db.get_services_list()
        
        options = [{"label": "📊 Todos los servicios", "value": "ALL"}]
        options.extend([{"label": service, "value": service} for service in services[:20]])
        
        return options, options
        
    except Exception:
        return [], []