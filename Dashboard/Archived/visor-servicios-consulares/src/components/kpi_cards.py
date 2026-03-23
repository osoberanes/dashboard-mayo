"""
Componentes de KPIs reutilizables
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional, List
from ..config.constants import NUMBER_FORMATS, NAV_ICONS


def create_kpi_card(title: str, value: Any, 
                   icon: Optional[str] = None,
                   color: str = "primary",
                   format_type: str = "decimal",
                   delta: Optional[float] = None,
                   delta_color: str = "success") -> dbc.Card:
    """
    Crea una tarjeta KPI individual
    
    Args:
        title: Título del KPI
        value: Valor a mostrar
        icon: Ícono opcional
        color: Color del tema (primary, secondary, etc.)
        format_type: Tipo de formato (currency, integer, decimal, percentage)
        delta: Cambio porcentual opcional
        delta_color: Color del delta
    """
    
    # Formatear valor según el tipo
    if format_type in NUMBER_FORMATS:
        if format_type == "integer":
            formatted_value = NUMBER_FORMATS[format_type].format(int(value))
        else:
            formatted_value = NUMBER_FORMATS[format_type].format(value)
    else:
        formatted_value = str(value)
    
    # Crear elementos del contenido
    content_elements = []
    
    # Ícono si se proporciona
    if icon:
        content_elements.append(
            html.Div(
                icon,
                className=f"text-{color} mb-2",
                style={"fontSize": "2rem"}
            )
        )
    
    # Valor principal
    content_elements.append(
        html.H4(
            formatted_value,
            className=f"text-{color} mb-1",
            style={"fontWeight": "bold"}
        )
    )
    
    # Título
    content_elements.append(
        html.P(
            title,
            className="text-muted mb-0",
            style={"fontSize": "0.9rem"}
        )
    )
    
    # Delta si se proporciona
    if delta is not None:
        delta_icon = "↗" if delta >= 0 else "↘"
        delta_text = f"{delta_icon} {abs(delta):.1f}%"
        content_elements.append(
            html.Small(
                delta_text,
                className=f"text-{delta_color if delta >= 0 else 'danger'}",
                style={"fontWeight": "bold"}
            )
        )
    
    return dbc.Card(
        dbc.CardBody(content_elements),
        className="h-100 shadow-sm",
        style={"borderLeft": f"4px solid var(--bs-{color})"}
    )


def create_kpi_row(kpis: Dict[str, Dict[str, Any]]) -> dbc.Row:
    """
    Crea una fila de tarjetas KPI
    
    Args:
        kpis: Diccionario con configuración de KPIs
              {
                'kpi_name': {
                    'title': 'Título',
                    'value': 123.45,
                    'icon': '💰',
                    'format_type': 'currency',
                    'delta': 5.2
                }
              }
    """
    
    cols = []
    num_kpis = len(kpis)
    col_width = 12 // num_kpis if num_kpis > 0 else 12
    
    for i, (key, kpi_config) in enumerate(kpis.items()):
        # Color rotativo para variedad visual
        colors = ["primary", "info", "success", "warning"]
        color = colors[i % len(colors)]
        
        col = dbc.Col(
            create_kpi_card(
                title=kpi_config.get('title', key),
                value=kpi_config.get('value', 0),
                icon=kpi_config.get('icon'),
                color=color,
                format_type=kpi_config.get('format_type', 'decimal'),
                delta=kpi_config.get('delta')
            ),
            width=col_width,
            className="mb-3"
        )
        cols.append(col)
    
    return dbc.Row(cols)


def create_summary_stats_card(stats: Dict[str, Any]) -> dbc.Card:
    """
    Crea tarjeta de estadísticas resumidas
    """
    
    stats_items = []
    
    for key, value in stats.items():
        # Formatear según el tipo de estadística
        if 'ingreso' in key.lower():
            formatted_value = NUMBER_FORMATS['currency'].format(value)
        elif 'tramite' in key.lower() or 'registro' in key.lower():
            formatted_value = NUMBER_FORMATS['integer'].format(int(value))
        else:
            formatted_value = str(value)
        
        stats_items.append(
            dbc.Row([
                dbc.Col(key.replace('_', ' ').title() + ":", width=8),
                dbc.Col(html.Strong(formatted_value), width=4, className="text-end")
            ], className="mb-1")
        )
    
    return dbc.Card([
        dbc.CardHeader(
            html.H5("📊 Estadísticas del Sistema", className="mb-0")
        ),
        dbc.CardBody(stats_items)
    ])


def create_metric_comparison_table(comparisons: List[Dict[str, Any]]) -> dbc.Table:
    """
    Crea tabla de comparación de métricas entre períodos
    
    Args:
        comparisons: Lista de comparaciones
                    [
                        {
                            'metric': 'Ingresos Totales',
                            'period1': 1000,
                            'period2': 1200,
                            'change': 20.0
                        }
                    ]
    """
    
    headers = [
        html.Thead([
            html.Tr([
                html.Th("Métrica"),
                html.Th("Período 1", className="text-center"),
                html.Th("Período 2", className="text-center"),
                html.Th("Cambio", className="text-center")
            ])
        ])
    ]
    
    rows = []
    for comp in comparisons:
        # Formatear valores
        metric = comp['metric']
        
        if 'ingreso' in metric.lower():
            val1 = NUMBER_FORMATS['currency'].format(comp['period1'])
            val2 = NUMBER_FORMATS['currency'].format(comp['period2'])
        elif 'tramite' in metric.lower():
            val1 = NUMBER_FORMATS['integer'].format(int(comp['period1']))
            val2 = NUMBER_FORMATS['integer'].format(int(comp['period2']))
        else:
            val1 = NUMBER_FORMATS['decimal'].format(comp['period1'])
            val2 = NUMBER_FORMATS['decimal'].format(comp['period2'])
        
        # Color del cambio
        change = comp['change']
        change_color = "success" if change >= 0 else "danger"
        change_icon = "↗" if change >= 0 else "↘"
        change_text = f"{change_icon} {abs(change):.1f}%"
        
        row = html.Tr([
            html.Td(metric),
            html.Td(val1, className="text-center"),
            html.Td(val2, className="text-center"),
            html.Td(
                html.Span(change_text, className=f"text-{change_color}"),
                className="text-center"
            )
        ])
        rows.append(row)
    
    tbody = [html.Tbody(rows)]
    
    return dbc.Table(
        headers + tbody,
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )


def create_loading_spinner(text: str = "Cargando...") -> html.Div:
    """Crea spinner de carga con texto"""
    return html.Div([
        dbc.Spinner(
            html.Div(id="loading-output"),
            size="lg",
            color="primary",
            type="border",
            fullscreen=False,
        ),
        html.P(text, className="text-center mt-2 text-muted")
    ], className="text-center py-5")


def create_alert_message(message: str, 
                        alert_type: str = "info",
                        dismissible: bool = True,
                        icon: Optional[str] = None) -> dbc.Alert:
    """
    Crea mensaje de alerta
    
    Args:
        message: Texto del mensaje
        alert_type: Tipo de alerta (success, info, warning, danger)
        dismissible: Si se puede cerrar
        icon: Ícono opcional
    """
    
    content = [html.Span(message)]
    
    if icon:
        content.insert(0, html.Span(icon + " ", style={"marginRight": "8px"}))
    
    return dbc.Alert(
        content,
        color=alert_type,
        dismissable=dismissible,
        className="mb-3"
    )


def create_info_tooltip(text: str, tooltip_text: str) -> html.Span:
    """Crea texto con tooltip informativo"""
    return html.Span([
        text,
        html.Span(
            " ℹ️",
            id=f"tooltip-{hash(text)}",
            style={"cursor": "pointer", "marginLeft": "5px"}
        ),
        dbc.Tooltip(
            tooltip_text,
            target=f"tooltip-{hash(text)}",
            placement="top"
        )
    ])


def create_progress_bar(value: float, 
                       max_value: float = 100,
                       label: Optional[str] = None,
                       color: str = "success",
                       striped: bool = False,
                       animated: bool = False) -> html.Div:
    """
    Crea barra de progreso
    
    Args:
        value: Valor actual
        max_value: Valor máximo
        label: Etiqueta opcional
        color: Color de la barra
        striped: Si tiene rayas
        animated: Si está animada
    """
    
    percentage = min((value / max_value) * 100, 100) if max_value > 0 else 0
    
    components = []
    
    if label:
        components.append(
            html.Div([
                html.Span(label),
                html.Span(f"{value:,.0f} / {max_value:,.0f}", className="float-end")
            ], className="d-flex justify-content-between mb-1")
        )
    
    progress_bar = dbc.Progress(
        value=percentage,
        striped=striped,
        animated=animated,
        color=color,
        style={"height": "20px"}
    )
    
    components.append(progress_bar)
    
    return html.Div(components)