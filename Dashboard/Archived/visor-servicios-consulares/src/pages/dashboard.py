"""
Página principal del dashboard con análisis integrado
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List

from ..core import DatabaseManager, AnalyticsEngine, ChartFactory
from ..components import (
    create_kpi_row, create_date_range_picker, create_service_selector,
    create_temporal_grouping_selector, create_metric_selector,
    create_page_header, create_alert_message, create_loading_spinner,
    create_tab_container
)
from ..config.settings import settings


class DashboardPage:
    """Controlador de la página principal del dashboard"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine(self.db)
        self.charts = ChartFactory()
        
    def get_layout(self) -> html.Div:
        """Retorna el layout de la página del dashboard"""
        
        return html.Div([
            # Encabezado de página
            create_page_header(
                title="📊 Dashboard Principal",
                subtitle=settings.app.subtitle,
                actions=[
                    dbc.Button(
                        "🔄 Actualizar",
                        id="refresh-dashboard",
                        color="primary",
                        outline=True,
                        size="sm"
                    )
                ]
            ),
            
            # Área de alertas
            html.Div(id="dashboard-alerts"),
            
            # Filtros principales
            self._create_main_filters(),
            
            # KPIs principales
            html.Div(id="main-kpis", className="mb-4"),
            
            # Contenido principal con pestañas
            self._create_main_content(),
            
            # Stores para datos
            dcc.Store(id="dashboard-data-store"),
            dcc.Store(id="filter-state-store"),
            
            # Interval para actualización automática
            dcc.Interval(
                id="dashboard-interval",
                interval=settings.app.chart_refresh_interval,
                n_intervals=0,
                disabled=not settings.app.debug
            )
        ])
    
    def _create_main_filters(self) -> dbc.Card:
        """Crea panel de filtros principales"""
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5("🎛️ Filtros de Análisis", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    # Rango de fechas
                    dbc.Col([
                        create_date_range_picker(
                            start_date=date.today() - timedelta(days=365),
                            end_date=date.today(),
                            picker_id="main-date-range",
                            label="Período de análisis:"
                        )
                    ], md=4),
                    
                    # Selector de servicio
                    dbc.Col([
                        create_service_selector(
                            services=[],  # Se llenará dinámicamente
                            selector_id="main-service-filter",
                            label="Servicio específico:",
                            include_all=True
                        )
                    ], md=4),
                    
                    # Agrupación temporal
                    dbc.Col([
                        create_temporal_grouping_selector(
                            selected_grouping="mensual",
                            selector_id="main-temporal-grouping",
                            label="Agrupación temporal:"
                        )
                    ], md=4)
                ])
            ])
        ], className="mb-4")
    
    def _create_main_content(self) -> html.Div:
        """Crea contenido principal con pestañas"""
        
        tabs = [
            {
                "id": "overview-tab",
                "label": "📊 Vista General", 
                "content": self._create_overview_tab()
            },
            {
                "id": "temporal-tab",
                "label": "📈 Análisis Temporal",
                "content": self._create_temporal_tab()
            },
            {
                "id": "services-tab", 
                "label": "🔧 Análisis por Servicios",
                "content": self._create_services_tab()
            },
            {
                "id": "comparison-tab",
                "label": "⚖️ Comparación de Períodos",
                "content": self._create_comparison_tab()
            }
        ]
        
        return create_tab_container(
            tabs=tabs,
            active_tab="overview-tab",
            tab_container_id="main-dashboard"
        )
    
    def _create_overview_tab(self) -> html.Div:
        """Crea pestaña de vista general"""
        
        return html.Div([
            # Gráficas principales lado a lado
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("💰 Evolución de Ingresos"),
                        dbc.CardBody([
                            dcc.Graph(id="overview-income-chart")
                        ])
                    ])
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📄 Evolución de Trámites"),
                        dbc.CardBody([
                            dcc.Graph(id="overview-tramites-chart")
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            # Top servicios
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🏆 Top Servicios por Ingresos"),
                        dbc.CardBody([
                            dcc.Graph(id="overview-top-services-chart")
                        ])
                    ])
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Análisis Semanal"),
                        dbc.CardBody([
                            html.Div(id="overview-weekly-analysis")
                        ])
                    ])
                ], md=6)
            ])
        ])
    
    def _create_temporal_tab(self) -> html.Div:
        """Crea pestaña de análisis temporal"""
        
        return html.Div([
            # Controles adicionales
            dbc.Row([
                dbc.Col([
                    create_metric_selector(
                        metrics=[
                            ('ingresos_totales', 'Ingresos Totales'),
                            ('num_tramites', 'Número de Trámites'),
                            ('ingreso_por_tramite', 'Ingreso por Trámite')
                        ],
                        selector_id="temporal-metric-selector",
                        label="Métrica a analizar:"
                    )
                ], md=6)
            ], className="mb-3"),
            
            # Gráfica temporal principal
            dbc.Card([
                dbc.CardHeader("📈 Análisis Temporal Detallado"),
                dbc.CardBody([
                    dcc.Graph(id="temporal-main-chart")
                ])
            ], className="mb-4"),
            
            # Estadísticas temporales
            html.Div(id="temporal-stats")
        ])
    
    def _create_services_tab(self) -> html.Div:
        """Crea pestaña de análisis por servicios"""
        
        return html.Div([
            # Gráfica de distribución de servicios
            dbc.Card([
                dbc.CardHeader("🎯 Análisis de Servicio Específico"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Servicio a analizar:", className="fw-bold"),
                            dcc.Dropdown(
                                id="service-analysis-selector",
                                placeholder="Seleccionar servicio...",
                                className="mb-3"
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Métrica:", className="fw-bold"),
                            dcc.Dropdown(
                                id="service-metric-selector",
                                options=[
                                    {"label": "💰 Ingresos", "value": "ingresos_totales"},
                                    {"label": "📄 Trámites", "value": "num_tramites"}
                                ],
                                value="ingresos_totales",
                                className="mb-3"
                            )
                        ], md=6)
                    ]),
                    dcc.Graph(id="service-analysis-chart")
                ])
            ], className="mb-4"),
            
            # Tabla de servicios
            dbc.Card([
                dbc.CardHeader("📋 Resumen de Todos los Servicios"),
                dbc.CardBody([
                    html.Div(id="services-table")
                ])
            ])
        ])
    
    def _create_comparison_tab(self) -> html.Div:
        """Crea pestaña de comparación de períodos"""
        
        return html.Div([
            # Configuración de comparación
            dbc.Card([
                dbc.CardHeader("⚙️ Configuración de Comparación"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Período Base:", className="fw-bold"),
                            create_date_range_picker(
                                picker_id="comparison-period1",
                                label=""
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Período a Comparar:", className="fw-bold"),
                            create_date_range_picker(
                                picker_id="comparison-period2", 
                                label=""
                            )
                        ], md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "🔄 Ejecutar Comparación",
                                id="execute-comparison",
                                color="primary",
                                className="mt-3"
                            )
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Resultados de comparación
            html.Div(id="comparison-results")
        ])


# Instancia global de la página
dashboard_page = DashboardPage()


# Callbacks para la funcionalidad del dashboard
@callback(
    [Output("main-kpis", "children"),
     Output("dashboard-data-store", "data"),
     Output("dashboard-alerts", "children")],
    [Input("main-date-range", "start_date"),
     Input("main-date-range", "end_date"),
     Input("main-service-filter", "value"),
     Input("refresh-dashboard", "n_clicks"),
     Input("dashboard-interval", "n_intervals")]
)
def update_main_kpis(start_date, end_date, service_filter, refresh_clicks, interval_updates):
    """Actualiza KPIs principales y datos base"""
    
    try:
        # Convertir fechas si es necesario
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        
        # Obtener KPIs
        kpis = dashboard_page.analytics.get_kpis(
            start_date.strftime('%Y-%m-%d') if start_date else None,
            end_date.strftime('%Y-%m-%d') if end_date else None
        )
        
        # Preparar configuración de KPIs para la vista
        kpi_config = {
            'ingresos': {
                'title': 'Ingresos Totales',
                'value': kpis['total_ingresos'],
                'icon': '💰',
                'format_type': 'currency'
            },
            'tramites': {
                'title': 'Trámites Totales', 
                'value': kpis['total_tramites'],
                'icon': '📄',
                'format_type': 'integer'
            },
            'promedio_diario': {
                'title': 'Promedio Diario',
                'value': kpis['promedio_diario_ingresos'], 
                'icon': '📊',
                'format_type': 'currency'
            },
            'eficiencia': {
                'title': 'Ingreso por Trámite',
                'value': kpis['ingreso_por_tramite'],
                'icon': '⚡',
                'format_type': 'currency'
            }
        }
        
        kpi_cards = create_kpi_row(kpi_config)
        
        # Datos para store
        store_data = {
            'kpis': kpis,
            'last_updated': datetime.now().isoformat(),
            'filters': {
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                'service_filter': service_filter
            }
        }
        
        # Alert de éxito
        alert = create_alert_message(
            f"✅ Datos actualizados: {kpis['total_tramites']} trámites, ${kpis['total_ingresos']:,.2f} en ingresos",
            alert_type="success",
            dismissible=True
        )
        
        return kpi_cards, store_data, alert
        
    except Exception as e:
        error_alert = create_alert_message(
            f"❌ Error cargando datos: {str(e)}",
            alert_type="danger"
        )
        
        # KPIs vacíos en caso de error
        empty_kpis = create_kpi_row({
            'error': {
                'title': 'Error en datos',
                'value': 0,
                'icon': '❌',
                'format_type': 'integer'
            }
        })
        
        return empty_kpis, {}, error_alert


@callback(
    [Output("overview-income-chart", "figure"),
     Output("overview-tramites-chart", "figure")],
    [Input("dashboard-data-store", "data"),
     Input("main-temporal-grouping", "value")]
)
def update_overview_charts(data_store, temporal_grouping):
    """Actualiza gráficas de la vista general"""
    
    if not data_store:
        empty_fig = dashboard_page.charts._create_empty_chart("No hay datos disponibles")
        return empty_fig, empty_fig
    
    try:
        filters = data_store.get('filters', {})
        
        # Obtener datos temporales
        temporal_data = dashboard_page.analytics.get_temporal_analysis(
            grouping=temporal_grouping or 'mensual',
            start_date=filters.get('start_date'),
            end_date=filters.get('end_date')
        )
        
        if temporal_data.empty:
            empty_fig = dashboard_page.charts._create_empty_chart("No hay datos para el período")
            return empty_fig, empty_fig
        
        # Gráfica de ingresos
        income_chart = dashboard_page.charts.create_line_chart(
            data=temporal_data,
            x_col='periodo_str',
            y_col='ingresos_totales',
            title=f"Evolución de Ingresos - {temporal_grouping.title()}",
            color=dashboard_page.charts.colors['primary']
        )
        
        # Gráfica de trámites
        tramites_chart = dashboard_page.charts.create_line_chart(
            data=temporal_data,
            x_col='periodo_str', 
            y_col='num_tramites',
            title=f"Evolución de Trámites - {temporal_grouping.title()}",
            color=dashboard_page.charts.colors['success']
        )
        
        return income_chart, tramites_chart
        
    except Exception as e:
        error_fig = dashboard_page.charts._create_empty_chart(f"Error: {str(e)}")
        return error_fig, error_fig


@callback(
    Output("overview-top-services-chart", "figure"),
    [Input("dashboard-data-store", "data")]
)
def update_top_services_chart(data_store):
    """Actualiza gráfica de top servicios"""
    
    if not data_store:
        return dashboard_page.charts._create_empty_chart("No hay datos disponibles")
    
    try:
        filters = data_store.get('filters', {})
        
        # Obtener top servicios
        top_services = dashboard_page.analytics.get_top_services(
            by='ingresos',
            top_n=10,
            start_date=filters.get('start_date'),
            end_date=filters.get('end_date')
        )
        
        if top_services.empty:
            return dashboard_page.charts._create_empty_chart("No hay datos de servicios")
        
        # Crear gráfica de barras horizontales
        chart = dashboard_page.charts.create_bar_chart(
            data=top_services,
            x_col='servicio',
            y_col='ingresos_totales',
            title="Top 10 Servicios por Ingresos",
            orientation='h',
            color_col='ingresos_totales'
        )
        
        return chart
        
    except Exception as e:
        return dashboard_page.charts._create_empty_chart(f"Error: {str(e)}")


@callback(
    Output("overview-weekly-analysis", "children"),
    [Input("dashboard-data-store", "data")]
)
def update_weekly_analysis(data_store):
    """Actualiza análisis semanal"""
    
    if not data_store:
        return create_alert_message("No hay datos disponibles", "info")
    
    try:
        filters = data_store.get('filters', {})
        
        # Obtener análisis semanal
        weekly_analysis = dashboard_page.analytics.get_weekly_analysis(
            start_date=filters.get('start_date'),
            end_date=filters.get('end_date')
        )
        
        if 'error' in weekly_analysis:
            return create_alert_message(weekly_analysis['error'], "warning")
        
        # Crear tabla semanal
        weekly_data = weekly_analysis['weekly_data']
        
        table_rows = []
        for _, row in weekly_data.iterrows():
            table_rows.append(
                html.Tr([
                    html.Td(row['dia_semana_es']),
                    html.Td(f"${row['ingresos_totales']:,.2f}"),
                    html.Td(f"{row['num_tramites']:,.0f}")
                ])
            )
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Día"),
                    html.Th("Ingresos Promedio"),
                    html.Th("Trámites Promedio")
                ])
            ]),
            html.Tbody(table_rows)
        ], bordered=True, hover=True, size="sm")
        
        # Información adicional
        max_day = weekly_analysis['max_ingresos_dia']
        min_day = weekly_analysis['min_ingresos_dia']
        
        summary = html.Div([
            html.P([
                html.Strong("Día más activo: "), f"{max_day}"
            ], className="mb-1"),
            html.P([
                html.Strong("Día menos activo: "), f"{min_day}"
            ], className="mb-0")
        ], className="mt-3")
        
        return html.Div([table, summary])
        
    except Exception as e:
        return create_alert_message(f"Error en análisis semanal: {str(e)}", "danger")


# Callback para llenar dinámicamente el selector de servicios
@callback(
    Output("main-service-filter", "options"),
    [Input("dashboard-data-store", "data")]
)
def update_service_options(data_store):
    """Actualiza opciones del selector de servicios"""
    
    try:
        services = dashboard_page.db.get_services_list()
        
        options = [{"label": "📊 Todos los servicios", "value": "ALL"}]
        
        for service in services[:20]:  # Limitar a 20 para mejor UX
            options.append({"label": service, "value": service})
        
        return options
        
    except Exception:
        return [{"label": "Error cargando servicios", "value": ""}]