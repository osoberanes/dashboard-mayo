"""
Componentes de navegación y layout
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict, Optional, Any

from ..config.settings import settings
from ..config.constants import NAV_ICONS


def create_navbar(brand_text: str = None) -> dbc.Navbar:
    """
    Crea barra de navegación principal
    """
    
    brand_text = brand_text or settings.app.title
    
    return dbc.Navbar(
        dbc.Container([
            # Logo y título
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src="/assets/logo.png", height="30px"), width="auto"),
                    dbc.Col(dbc.NavbarBrand(brand_text, className="ms-2")),
                ], align="center", className="g-0"),
                href="/",
                style={"textDecoration": "none"}
            ),
            
            # Botones de navegación
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("🏠 Inicio", href="/", external_link=True)),
                dbc.NavItem(dbc.NavLink("📊 Dashboard", href="/dashboard", external_link=True)),
                dbc.NavItem(dbc.NavLink("🔧 Admin", href="/admin", external_link=True)),
                dbc.NavItem(dbc.NavLink("📈 Reportes", href="/reports", external_link=True)),
            ], className="ms-auto", navbar=True),
        ]),
        color="dark",
        dark=True,
        className="mb-4"
    )


def create_sidebar(pages: List[Dict[str, Any]], 
                  current_page: str = "dashboard",
                  sidebar_id: str = "sidebar") -> html.Div:
    """
    Crea barra lateral de navegación
    
    Args:
        pages: Lista de páginas con formato:
               [{"id": "dashboard", "label": "Dashboard", "icon": "📊"}]
        current_page: Página actualmente activa
        sidebar_id: ID de la barra lateral
    """
    
    nav_items = []
    
    for page in pages:
        page_id = page.get('id')
        label = page.get('label', page_id.title())
        icon = page.get('icon', '📄')
        
        # Determinar si está activo
        is_active = page_id == current_page
        
        nav_item = dbc.NavItem(
            dbc.NavLink(
                [icon + " " + label],
                href=f"/{page_id}",
                active=is_active,
                id=f"nav-{page_id}",
                className="py-3"
            )
        )
        nav_items.append(nav_item)
    
    return html.Div([
        html.Div([
            html.H4([
                NAV_ICONS['dashboard'] + " " + settings.app.title
            ], className="text-white mb-4 px-3"),
            
            dbc.Nav(
                nav_items,
                vertical=True,
                pills=True,
                className="flex-column"
            ),
        ], className="p-3"),
        
        # Información del sistema en la parte inferior
        html.Div([
            html.Hr(className="text-white-50"),
            html.Small([
                "v2.0 - Sistema Modular",
                html.Br(),
                "Claude Code Assistant"
            ], className="text-white-50 px-3")
        ], className="mt-auto")
        
    ], id=sidebar_id, 
       className="bg-dark position-fixed h-100",
       style={
           "width": settings.ui.sidebar_width,
           "top": "0",
           "left": "0",
           "zIndex": "1000",
           "overflowY": "auto"
       })


def create_breadcrumb(items: List[Dict[str, str]]) -> dbc.Breadcrumb:
    """
    Crea breadcrumb de navegación
    
    Args:
        items: Lista de elementos con formato:
               [{"label": "Inicio", "href": "/"}, {"label": "Dashboard", "active": True}]
    """
    
    breadcrumb_items = []
    
    for item in items:
        breadcrumb_items.append(
            dbc.BreadcrumbItem(
                item['label'],
                href=item.get('href'),
                active=item.get('active', False)
            )
        )
    
    return dbc.Breadcrumb(breadcrumb_items)


def create_page_header(title: str, 
                      subtitle: Optional[str] = None,
                      actions: Optional[List[html.Component]] = None) -> html.Div:
    """
    Crea encabezado de página estandarizado
    
    Args:
        title: Título principal
        subtitle: Subtítulo opcional
        actions: Lista de componentes de acciones (botones, etc.)
    """
    
    header_content = [
        html.H1(title, className="mb-1")
    ]
    
    if subtitle:
        header_content.append(
            html.P(subtitle, className="text-muted mb-0")
        )
    
    left_col = dbc.Col(header_content, width="auto")
    
    # Crear fila con título a la izquierda y acciones a la derecha
    row_items = [left_col]
    
    if actions:
        right_col = dbc.Col(
            html.Div(actions, className="d-flex gap-2"),
            width="auto",
            className="ms-auto"
        )
        row_items.append(right_col)
    
    return html.Div([
        dbc.Row(row_items, className="align-items-center"),
        html.Hr()
    ], className="mb-4")


def create_tab_container(tabs: List[Dict[str, Any]], 
                        active_tab: str = None,
                        tab_container_id: str = "tab-container") -> html.Div:
    """
    Crea contenedor de pestañas
    
    Args:
        tabs: Lista de pestañas con formato:
              [{"id": "tab1", "label": "Tab 1", "content": html.Div(...)}]
        active_tab: ID de la pestaña activa
        tab_container_id: ID del contenedor
    """
    
    if not tabs:
        return html.Div("No hay pestañas disponibles")
    
    # Si no se especifica pestaña activa, usar la primera
    if not active_tab:
        active_tab = tabs[0]['id']
    
    # Crear pestañas
    tab_items = []
    for tab in tabs:
        tab_items.append(
            dbc.Tab(
                label=tab['label'],
                tab_id=tab['id'],
                active_tab_style={"textTransform": "none"}
            )
        )
    
    # Crear contenido de pestañas
    tab_contents = []
    for tab in tabs:
        tab_contents.append(
            dbc.TabPane(
                tab['content'],
                tab_id=tab['id']
            )
        )
    
    return html.Div([
        dbc.Tabs(
            tab_items,
            id=f"{tab_container_id}-tabs",
            active_tab=active_tab,
            className="mb-3"
        ),
        html.Div(
            tab_contents,
            id=f"{tab_container_id}-content"
        )
    ])


def create_modal(modal_id: str,
                title: str,
                body_content: html.Component,
                footer_buttons: Optional[List[html.Component]] = None,
                size: str = "lg") -> dbc.Modal:
    """
    Crea modal reutilizable
    
    Args:
        modal_id: ID del modal
        title: Título del modal
        body_content: Contenido del cuerpo
        footer_buttons: Lista de botones para el footer
        size: Tamaño del modal (sm, lg, xl)
    """
    
    footer = None
    if footer_buttons:
        footer = dbc.ModalFooter(footer_buttons)
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(title)),
        dbc.ModalBody(body_content),
        footer
    ], id=modal_id, size=size, is_open=False)


def create_offcanvas_menu(menu_id: str,
                         title: str,
                         menu_items: List[Dict[str, Any]],
                         placement: str = "start") -> dbc.Offcanvas:
    """
    Crea menú offcanvas para móviles
    
    Args:
        menu_id: ID del menú
        title: Título del menú
        menu_items: Lista de elementos del menú
        placement: Posición (start, end, top, bottom)
    """
    
    nav_items = []
    for item in menu_items:
        nav_items.append(
            dbc.NavItem(
                dbc.NavLink(
                    item.get('icon', '') + " " + item['label'],
                    href=item.get('href', '#'),
                    className="py-2"
                )
            )
        )
    
    return dbc.Offcanvas([
        dbc.Nav(nav_items, vertical=True)
    ], id=menu_id, title=title, placement=placement, is_open=False)


def create_responsive_layout(main_content: html.Component,
                           sidebar_content: Optional[html.Component] = None,
                           use_sidebar: bool = True) -> html.Div:
    """
    Crea layout responsivo con sidebar opcional
    
    Args:
        main_content: Contenido principal
        sidebar_content: Contenido de la barra lateral
        use_sidebar: Si usar barra lateral
    """
    
    if use_sidebar and sidebar_content:
        # Layout con sidebar
        return html.Div([
            # Sidebar
            html.Div(
                sidebar_content,
                className="d-none d-lg-block",
                style={
                    "width": settings.ui.sidebar_width,
                    "position": "fixed",
                    "height": "100vh",
                    "overflowY": "auto"
                }
            ),
            
            # Contenido principal
            html.Div(
                main_content,
                style={
                    "marginLeft": settings.ui.sidebar_width,
                    "padding": "20px"
                },
                className="d-none d-lg-block"
            ),
            
            # Vista móvil (sin sidebar)
            html.Div(
                main_content,
                className="d-lg-none p-3"
            )
        ])
    else:
        # Layout sin sidebar
        return html.Div(
            main_content,
            className="container-fluid p-4"
        )


def create_footer() -> html.Footer:
    """Crea footer del sitio"""
    return html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P([
                        "© 2025 Visor de Servicios Consulares. ",
                        "Desarrollado con ",
                        html.A("Plotly Dash", href="https://dash.plotly.com/", target="_blank"),
                        "."
                    ], className="mb-0 text-muted")
                ], className="text-center")
            ])
        ])
    ], className="bg-light py-3 mt-5")


def create_status_indicator(status: str, 
                           text: Optional[str] = None,
                           indicator_id: str = "status-indicator") -> html.Div:
    """
    Crea indicador de estado
    
    Args:
        status: Estado (success, warning, danger, info)
        text: Texto del indicador
        indicator_id: ID del componente
    """
    
    status_colors = {
        'success': 'success',
        'warning': 'warning', 
        'danger': 'danger',
        'info': 'info',
        'loading': 'primary'
    }
    
    status_icons = {
        'success': '✅',
        'warning': '⚠️',
        'danger': '❌',
        'info': 'ℹ️',
        'loading': '🔄'
    }
    
    color = status_colors.get(status, 'secondary')
    icon = status_icons.get(status, '●')
    
    return dbc.Badge([
        icon,
        " " + (text or status.title())
    ], color=color, id=indicator_id, className="me-2")