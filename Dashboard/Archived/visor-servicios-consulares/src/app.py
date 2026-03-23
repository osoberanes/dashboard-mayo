"""
Aplicación principal del Visor de Servicios Consulares
Sistema completo en Plotly Dash con arquitectura modular
"""
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
import logging
from datetime import datetime
import sys
import os

# Configurar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from .config import settings
    from .components import create_navbar, create_footer, create_responsive_layout
    from .pages import dashboard_page, admin_page, reports_page
except ImportError:
    # Importaciones absolutas cuando se ejecuta directamente
    from config import settings
    from components import create_navbar, create_footer, create_responsive_layout
    from pages import dashboard_page, admin_page, reports_page


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VisorServiciosConsulares:
    """Aplicación principal del Visor de Servicios Consulares"""
    
    def __init__(self):
        # Inicializar aplicación Dash
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
            ],
            meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"},
                {"name": "description", "content": "Visor de Servicios Consulares - Análisis de datos consulares mexicanos"},
                {"name": "author", "content": "Claude Code Assistant"}
            ],
            title=settings.app.title,
            suppress_callback_exceptions=True,
            use_pages=False  # Manejo manual de páginas para mayor control
        )
        
        # Configurar aplicación
        self._setup_app()
        
        # Definir layout principal
        self.app.layout = self._create_main_layout()
        
        # Registrar callbacks principales
        self._register_main_callbacks()
        
        logger.info("Aplicación Visor de Servicios Consulares inicializada")
    
    def _setup_app(self):
        """Configura la aplicación Dash"""
        
        # Configuración del servidor
        self.app.server.config.update(
            SECRET_KEY=os.urandom(24),
            WTF_CSRF_ENABLED=False
        )
        
        # CSS personalizado
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    .sidebar {
                        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
                        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                    }
                    .main-content {
                        background-color: #f8f9fa;
                        min-height: 100vh;
                    }
                    .card {
                        border: none;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        border-radius: 10px;
                    }
                    .btn {
                        border-radius: 8px;
                        font-weight: 500;
                    }
                    .nav-pills .nav-link.active {
                        background: linear-gradient(45deg, #007bff, #0056b3);
                        border-radius: 8px;
                    }
                    @media (max-width: 768px) {
                        .sidebar {
                            transform: translateX(-100%);
                            transition: transform 0.3s ease;
                        }
                        .sidebar.show {
                            transform: translateX(0);
                        }
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
    
    def _create_main_layout(self) -> html.Div:
        """Crea el layout principal de la aplicación"""
        
        return html.Div([
            # URL para routing
            dcc.Location(id='url', refresh=False),
            
            # Barra de navegación superior
            create_navbar(settings.app.title),
            
            # Contenido principal con sidebar
            html.Div([
                # Sidebar de navegación
                html.Div(
                    self._create_sidebar(),
                    id="sidebar",
                    className="sidebar d-flex flex-column",
                    style={
                        "position": "fixed",
                        "top": "56px",  # Altura del navbar
                        "left": "0",
                        "width": settings.ui.sidebar_width,
                        "height": "calc(100vh - 56px)",
                        "zIndex": "1000",
                        "overflowY": "auto"
                    }
                ),
                
                # Contenido principal
                html.Div(
                    [
                        # Breadcrumb dinámico
                        html.Div(id="breadcrumb-container"),
                        
                        # Contenido de páginas
                        html.Div(id="page-content")
                    ],
                    className="main-content",
                    style={
                        "marginLeft": settings.ui.sidebar_width,
                        "padding": "20px",
                        "minHeight": "calc(100vh - 56px)"
                    }
                )
            ]),
            
            # Footer
            create_footer(),
            
            # Stores globales
            dcc.Store(id="global-app-store"),
            dcc.Store(id="user-preferences-store"),
            
            # Notificaciones toast
            html.Div(id="toast-container"),
            
            # Modal global para mensajes
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="global-modal-title")),
                dbc.ModalBody(id="global-modal-body"),
                dbc.ModalFooter([
                    dbc.Button("Cerrar", id="global-modal-close", color="secondary")
                ])
            ], id="global-modal", size="lg", is_open=False)
        ])
    
    def _create_sidebar(self) -> html.Div:
        """Crea la barra lateral de navegación"""
        
        return html.Div([
            # Logo y título
            html.Div([
                html.H4([
                    "📊 ",
                    html.Span(settings.app.title, style={"fontSize": "1rem"})
                ], className="text-white mb-0 px-3 py-3"),
                html.Hr(className="text-white-50 mx-3")
            ]),
            
            # Menú de navegación
            dbc.Nav([
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-chart-dashboard me-2"),
                        "Dashboard Principal"
                    ], href="/dashboard", id="nav-dashboard", className="text-white px-3 py-3")
                ]),
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-cog me-2"),
                        "Administración"
                    ], href="/admin", id="nav-admin", className="text-white px-3 py-3")
                ]),
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-chart-line me-2"),
                        "Reportes"
                    ], href="/reports", id="nav-reports", className="text-white px-3 py-3")
                ])
            ], vertical=True, pills=True, className="flex-column w-100"),
            
            # Información del sistema en la parte inferior
            html.Div([
                html.Hr(className="text-white-50 mx-3"),
                html.Div([
                    html.Small([
                        html.I(className="fas fa-info-circle me-1"),
                        "Sistema Modular v2.0"
                    ], className="text-white-50 d-block px-3"),
                    html.Small([
                        html.I(className="fas fa-code me-1"),
                        "Claude Code Assistant"
                    ], className="text-white-50 d-block px-3 mt-1"),
                    html.Small(
                        id="system-status",
                        className="text-success d-block px-3 mt-2"
                    )
                ], className="mb-3")
            ], className="mt-auto")
        ], className="d-flex flex-column h-100")
    
    def _register_main_callbacks(self):
        """Registra callbacks principales de la aplicación"""
        
        @self.app.callback(
            [Output('page-content', 'children'),
             Output('breadcrumb-container', 'children'),
             Output('nav-dashboard', 'active'),
             Output('nav-admin', 'active'),
             Output('nav-reports', 'active')],
            [Input('url', 'pathname')]
        )
        def display_page(pathname):
            """Controla la navegación entre páginas"""
            
            # Resetear estados activos
            nav_states = [False, False, False]
            breadcrumb = html.Div()
            
            try:
                if pathname == '/' or pathname == '/dashboard':
                    nav_states[0] = True
                    breadcrumb = dbc.Breadcrumb([
                        dbc.BreadcrumbItem("Inicio", href="/"),
                        dbc.BreadcrumbItem("Dashboard", active=True)
                    ])
                    return dashboard_page.get_layout(), breadcrumb, *nav_states
                
                elif pathname == '/admin':
                    nav_states[1] = True
                    breadcrumb = dbc.Breadcrumb([
                        dbc.BreadcrumbItem("Inicio", href="/"),
                        dbc.BreadcrumbItem("Administración", active=True)
                    ])
                    return admin_page.get_layout(), breadcrumb, *nav_states
                
                elif pathname == '/reports':
                    nav_states[2] = True
                    breadcrumb = dbc.Breadcrumb([
                        dbc.BreadcrumbItem("Inicio", href="/"),
                        dbc.BreadcrumbItem("Reportes", active=True)
                    ])
                    return reports_page.get_layout(), breadcrumb, *nav_states
                
                else:
                    # Página 404
                    nav_states[0] = True  # Default a dashboard
                    error_page = html.Div([
                        html.H1("404 - Página no encontrada", className="text-center"),
                        html.P("La página solicitada no existe.", className="text-center text-muted"),
                        dbc.Button("Ir al Dashboard", href="/dashboard", color="primary", className="mx-auto d-block")
                    ], className="text-center mt-5")
                    return error_page, breadcrumb, *nav_states
                    
            except Exception as e:
                logger.error(f"Error en navegación: {str(e)}")
                error_page = html.Div([
                    dbc.Alert(f"Error cargando página: {str(e)}", color="danger"),
                    dbc.Button("Ir al Dashboard", href="/dashboard", color="primary")
                ])
                return error_page, breadcrumb, *nav_states
        
        @self.app.callback(
            Output('system-status', 'children'),
            [Input('global-app-store', 'data')]
        )
        def update_system_status(app_data):
            """Actualiza estado del sistema en sidebar"""
            
            try:
                from .core import DatabaseManager
                db = DatabaseManager()
                stats = db.get_summary_stats()
                
                return [
                    html.I(className="fas fa-circle me-1"),
                    f"{stats.get('total_registros', 0):,} registros"
                ]
            except Exception:
                return [
                    html.I(className="fas fa-exclamation-triangle me-1"),
                    "Estado desconocido"
                ]
        
        @self.app.callback(
            Output('global-modal', 'is_open'),
            [Input('global-modal-close', 'n_clicks')],
            [State('global-modal', 'is_open')]
        )
        def toggle_global_modal(close_clicks, is_open):
            """Controla modal global"""
            if close_clicks:
                return False
            return is_open
        
        # Callback para responsive sidebar en móviles
        clientside_callback(
            """
            function(pathname) {
                // Auto-ocultar sidebar en móviles después de navegación
                if (window.innerWidth <= 768) {
                    const sidebar = document.getElementById('sidebar');
                    if (sidebar) {
                        sidebar.classList.remove('show');
                    }
                }
                return window.dash_clientside.no_update;
            }
            """,
            Output('sidebar', 'className'),
            [Input('url', 'pathname')]
        )
    
    def run_server(self, debug: bool = None, host: str = None, port: int = None):
        """Ejecuta el servidor de la aplicación"""
        
        debug = debug if debug is not None else settings.app.debug
        host = host or settings.app.host
        port = port or settings.app.port
        
        logger.info(f"Iniciando servidor en http://{host}:{port}")
        logger.info(f"Modo debug: {debug}")
        
        try:
            self.app.run_server(
                debug=debug,
                host=host,
                port=port,
                dev_tools_hot_reload=debug,
                dev_tools_ui=debug
            )
        except Exception as e:
            logger.error(f"Error iniciando servidor: {str(e)}")
            raise


# Crear instancia global de la aplicación
app_instance = VisorServiciosConsulares()

# Exponer la aplicación Dash para deployment
app = app_instance.app
server = app.server


def main():
    """Función principal para ejecutar la aplicación"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Visor de Servicios Consulares')
    parser.add_argument('--host', default=settings.app.host, help='Host para el servidor')
    parser.add_argument('--port', type=int, default=settings.app.port, help='Puerto para el servidor')
    parser.add_argument('--debug', action='store_true', help='Ejecutar en modo debug')
    parser.add_argument('--no-debug', action='store_true', help='Ejecutar en modo producción')
    
    args = parser.parse_args()
    
    # Determinar modo debug
    if args.no_debug:
        debug = False
    elif args.debug:
        debug = True
    else:
        debug = settings.app.debug
    
    # Ejecutar aplicación
    try:
        app_instance.run_server(
            debug=debug,
            host=args.host,
            port=args.port
        )
    except KeyboardInterrupt:
        logger.info("Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()