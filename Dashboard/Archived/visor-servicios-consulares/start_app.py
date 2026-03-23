"""
Script de inicio simplificado del Visor de Servicios Consulares
"""
import sys
import os
import logging
from pathlib import Path

# Configurar el path ANTES de cualquier import
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal simplificada"""
    try:
        logger.info("Iniciando Visor de Servicios Consulares...")
        
        # Verificar dependencias críticas
        try:
            import dash
            import dash_bootstrap_components as dbc
            import plotly
            import pandas as pd
            logger.info("Dependencias verificadas correctamente")
        except ImportError as e:
            logger.error(f"Dependencia faltante: {e}")
            sys.exit(1)
        
        # Importar configuración
        try:
            from config.settings import settings
            logger.info(f"Configuración cargada: {settings.app.title}")
        except ImportError as e:
            logger.error(f"Error cargando configuración: {e}")
            sys.exit(1)
        
        # Crear aplicación Dash básica
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            title=settings.app.title
        )
        
        # Layout básico de prueba
        app.layout = dbc.Container([
            dbc.Alert([
                html.H1("🚀 Visor de Servicios Consulares", className="mb-3"),
                html.H4("Sistema funcionando correctamente", className="text-success"),
                html.P("La aplicación se ha iniciado exitosamente.", className="mb-2"),
                html.Hr(),
                html.P([
                    "📊 Configuración: ", html.Code(settings.app.title), html.Br(),
                    "🔧 Puerto: ", html.Code(f"{settings.app.host}:{settings.app.port}"), html.Br(),
                    "📁 Base de datos: ", html.Code(settings.database.path)
                ], className="mb-0")
            ], color="success", className="mt-4"),
            
            dbc.Card([
                dbc.CardBody([
                    html.H5("Próximos pasos:", className="mb-3"),
                    html.Ul([
                        html.Li("✅ Aplicación iniciada correctamente"),
                        html.Li("✅ Dependencias verificadas"),
                        html.Li("✅ Configuración cargada"),
                        html.Li("🔄 Cargar datos de prueba desde /data/mayo_test.xls"),
                        html.Li("🔄 Implementar páginas completas"),
                        html.Li("🔄 Conectar base de datos")
                    ])
                ])
            ], className="mt-4")
        ], className="py-4")
        
        # Iniciar servidor
        logger.info(f"Iniciando servidor en http://{settings.app.host}:{settings.app.port}")
        
        app.run(
            host=settings.app.host,
            port=settings.app.port,
            debug=settings.app.debug,
            dev_tools_hot_reload=settings.app.debug
        )
        
    except KeyboardInterrupt:
        logger.info("Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # Imports necesarios para el layout
    import dash
    import dash_bootstrap_components as dbc
    from dash import html
    
    main()