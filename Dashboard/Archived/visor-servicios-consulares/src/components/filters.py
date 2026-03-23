"""
Componentes de filtros reutilizables
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple

from ..config.constants import TEMPORAL_GROUPINGS, NAV_ICONS


def create_date_range_picker(start_date: Optional[date] = None,
                           end_date: Optional[date] = None,
                           picker_id: str = "date-range-picker",
                           label: str = "Rango de fechas:") -> html.Div:
    """
    Crea selector de rango de fechas
    
    Args:
        start_date: Fecha de inicio por defecto
        end_date: Fecha de fin por defecto  
        picker_id: ID del componente
        label: Etiqueta del filtro
    """
    
    # Fechas por defecto si no se proporcionan
    if not start_date:
        start_date = date.today() - timedelta(days=365)
    if not end_date:
        end_date = date.today()
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.DatePickerRange(
            id=picker_id,
            start_date=start_date,
            end_date=end_date,
            display_format='DD/MM/YYYY',
            style={'width': '100%'},
            className="form-control"
        )
    ], className="mb-3")


def create_service_selector(services: List[str],
                          selected_service: Optional[str] = None,
                          selector_id: str = "service-selector",
                          label: str = "Servicio:",
                          placeholder: str = "Seleccionar servicio...",
                          include_all: bool = True) -> html.Div:
    """
    Crea selector de servicio
    
    Args:
        services: Lista de servicios disponibles
        selected_service: Servicio seleccionado por defecto
        selector_id: ID del componente
        label: Etiqueta del filtro
        placeholder: Texto placeholder
        include_all: Si incluir opción "Todos"
    """
    
    options = []
    
    if include_all:
        options.append({"label": "📊 Todos los servicios", "value": "ALL"})
    
    for service in services:
        options.append({"label": service, "value": service})
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Dropdown(
            id=selector_id,
            options=options,
            value=selected_service,
            placeholder=placeholder,
            clearable=True,
            searchable=True,
            className="mb-2"
        )
    ], className="mb-3")


def create_category_selector(categories: List[str],
                           selected_categories: Optional[List[str]] = None,
                           selector_id: str = "category-selector",
                           label: str = "Categorías:",
                           multi: bool = True) -> html.Div:
    """
    Crea selector de categorías con opción múltiple
    """
    
    options = [{"label": cat, "value": cat} for cat in categories]
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Dropdown(
            id=selector_id,
            options=options,
            value=selected_categories,
            placeholder="Seleccionar categorías...",
            multi=multi,
            clearable=True,
            searchable=True,
            className="mb-2"
        )
    ], className="mb-3")


def create_temporal_grouping_selector(selected_grouping: str = "mensual",
                                    selector_id: str = "temporal-grouping",
                                    label: str = "Agrupación temporal:",
                                    include_icons: bool = True) -> html.Div:
    """
    Crea selector de agrupación temporal
    """
    
    options = []
    icons = {
        'diario': '📅',
        'semanal': '📆', 
        'mensual': '🗓️',
        'trimestral': '📋',
        'anual': '📊'
    }
    
    for key, config in TEMPORAL_GROUPINGS.items():
        icon = icons.get(key, '') + " " if include_icons else ""
        label_text = icon + config['label']
        options.append({"label": label_text, "value": key})
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Dropdown(
            id=selector_id,
            options=options,
            value=selected_grouping,
            clearable=False,
            searchable=False,
            className="mb-2"
        )
    ], className="mb-3")


def create_metric_selector(metrics: List[Tuple[str, str]],
                         selected_metric: Optional[str] = None,
                         selector_id: str = "metric-selector",
                         label: str = "Métrica a analizar:",
                         include_icons: bool = True) -> html.Div:
    """
    Crea selector de métrica
    
    Args:
        metrics: Lista de tuplas (value, label)
        selected_metric: Métrica seleccionada
        selector_id: ID del componente
        label: Etiqueta
        include_icons: Si incluir iconos
    """
    
    metric_icons = {
        'ingresos_totales': '💰',
        'num_tramites': '📄',
        'ingreso_por_tramite': '💵',
        'formas_canceladas': '❌'
    }
    
    options = []
    for value, label_text in metrics:
        icon = metric_icons.get(value, '📊') + " " if include_icons else ""
        full_label = icon + label_text
        options.append({"label": full_label, "value": value})
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Dropdown(
            id=selector_id,
            options=options,
            value=selected_metric or (metrics[0][0] if metrics else None),
            clearable=False,
            searchable=False,
            className="mb-2"
        )
    ], className="mb-3")


def create_top_n_selector(selected_n: int = 10,
                        min_value: int = 5,
                        max_value: int = 50,
                        step: int = 5,
                        selector_id: str = "top-n-selector",
                        label: str = "Número de elementos:") -> html.Div:
    """
    Crea selector numérico para top N elementos
    """
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Slider(
            id=selector_id,
            min=min_value,
            max=max_value,
            step=step,
            value=selected_n,
            marks={i: str(i) for i in range(min_value, max_value + 1, step * 2)},
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], className="mb-4")


def create_filter_panel(filters_config: List[Dict[str, Any]],
                       panel_id: str = "filter-panel",
                       collapsible: bool = True,
                       default_open: bool = True) -> html.Div:
    """
    Crea panel de filtros completo
    
    Args:
        filters_config: Lista de configuraciones de filtros
        panel_id: ID del panel
        collapsible: Si el panel es colapsible
        default_open: Si está abierto por defecto
    """
    
    filter_components = []
    
    for filter_config in filters_config:
        filter_type = filter_config.get('type')
        
        if filter_type == 'date_range':
            component = create_date_range_picker(**filter_config.get('props', {}))
        elif filter_type == 'service':
            component = create_service_selector(**filter_config.get('props', {}))
        elif filter_type == 'category':
            component = create_category_selector(**filter_config.get('props', {}))
        elif filter_type == 'temporal':
            component = create_temporal_grouping_selector(**filter_config.get('props', {}))
        elif filter_type == 'metric':
            component = create_metric_selector(**filter_config.get('props', {}))
        elif filter_type == 'top_n':
            component = create_top_n_selector(**filter_config.get('props', {}))
        else:
            continue
        
        filter_components.append(component)
    
    content = html.Div(filter_components, className="p-3")
    
    if collapsible:
        return dbc.Card([
            dbc.CardHeader([
                html.H5([
                    NAV_ICONS['settings'] + " Filtros de Análisis"
                ], className="mb-0"),
                dbc.Button(
                    "Colapsar" if default_open else "Expandir",
                    id=f"{panel_id}-toggle",
                    size="sm",
                    outline=True,
                    className="float-end"
                )
            ]),
            dbc.Collapse(
                dbc.CardBody(filter_components),
                id=f"{panel_id}-collapse",
                is_open=default_open
            )
        ])
    else:
        return dbc.Card([
            dbc.CardHeader(
                html.H5([
                    NAV_ICONS['settings'] + " Filtros de Análisis"
                ], className="mb-0")
            ),
            dbc.CardBody(filter_components)
        ])


def create_quick_filters(filter_id: str = "quick-filters") -> html.Div:
    """
    Crea filtros rápidos para períodos comunes
    """
    
    quick_options = [
        {"label": "📅 Último mes", "value": "last_month"},
        {"label": "🗓️ Últimos 3 meses", "value": "last_3_months"},
        {"label": "📊 Último año", "value": "last_year"},
        {"label": "📋 Todo", "value": "all_time"}
    ]
    
    buttons = []
    for option in quick_options:
        buttons.append(
            dbc.Button(
                option["label"],
                id=f"{filter_id}-{option['value']}",
                size="sm",
                outline=True,
                className="me-2 mb-2"
            )
        )
    
    return html.Div([
        html.Label("Filtros rápidos:", className="form-label fw-bold mb-2"),
        html.Div(buttons, className="d-flex flex-wrap")
    ], className="mb-3")


def create_search_filter(search_id: str = "search-filter",
                        placeholder: str = "Buscar servicios...",
                        label: str = "Búsqueda:") -> html.Div:
    """
    Crea filtro de búsqueda
    """
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dbc.InputGroup([
            dbc.Input(
                id=search_id,
                placeholder=placeholder,
                type="text",
                debounce=True
            ),
            dbc.InputGroupText("🔍")
        ])
    ], className="mb-3")


def create_filter_reset_button(button_id: str = "reset-filters") -> dbc.Button:
    """
    Crea botón para resetear filtros
    """
    return dbc.Button([
        "🔄 Resetear Filtros"
    ], id=button_id, color="secondary", outline=True, size="sm")


def create_export_button(button_id: str = "export-data",
                        button_text: str = "📄 Exportar Datos") -> dbc.Button:
    """
    Crea botón de exportación
    """
    return dbc.Button(
        button_text,
        id=button_id,
        color="success",
        outline=True,
        size="sm"
    )