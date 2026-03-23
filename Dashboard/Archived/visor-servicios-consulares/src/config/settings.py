"""
Configuraciones centralizadas del sistema
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent.parent


@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    path: str = str(BASE_DIR / "data" / "consular_data.db")
    backup_dir: str = str(BASE_DIR / "data" / "backups")
    backup_retention_days: int = 30


@dataclass
class AppConfig:
    """Configuración principal de la aplicación"""
    title: str = "Visor de Servicios Consulares"
    subtitle: str = "Consulmex Kansas City - Análisis de Documentación"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8050
    
    # Intervalos de actualización (milisegundos)
    chart_refresh_interval: int = 30000
    data_refresh_interval: int = 60000


@dataclass
class UIConfig:
    """Configuración de interfaz de usuario"""
    theme: str = "bootstrap"
    sidebar_width: str = "250px"
    chart_height: int = 400
    table_page_size: int = 50
    
    # Responsive breakpoints
    mobile_breakpoint: int = 768
    tablet_breakpoint: int = 1024


@dataclass
class ChartConfig:
    """Configuración de gráficas"""
    default_colors: Dict[str, str] = None
    line_width: int = 2
    marker_size: int = 6
    font_family: str = "Arial, sans-serif"
    title_font_size: int = 16
    
    def __post_init__(self):
        if self.default_colors is None:
            self.default_colors = {
                "primary": "#1f77b4",
                "secondary": "#ff7f0e", 
                "success": "#2ca02c",
                "danger": "#d62728",
                "warning": "#ff9f40",
                "info": "#17a2b8",
                "dark": "#343a40",
                "light": "#f8f9fa"
            }


@dataclass
class ExportConfig:
    """Configuración de exportación"""
    pdf_dpi: int = 300
    export_dir: str = str(BASE_DIR / "data" / "exports")
    chart_export_width: int = 800
    chart_export_height: int = 600


@dataclass
class AnalyticsConfig:
    """Configuración de análisis"""
    default_date_range_days: int = 365
    top_services_limit: int = 10
    prediction_days: int = 30
    
    # Servicios agrupables
    groupable_services: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.groupable_services is None:
            self.groupable_services = {
                "RCM": {
                    "pattern": r"RCM|MATRÍCULA|MATRICULA",
                    "grouped_name": "RCM - Expedición Diaria",
                    "case_sensitive": False
                },
                "PASAPORTES": {
                    "pattern": r"PASAPORTES.*ORDINARIOS",
                    "grouped_name": "Pasaportes Ordinarios",
                    "case_sensitive": False
                }
            }


class Settings:
    """Clase principal de configuraciones"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.app = AppConfig()
        self.ui = UIConfig()
        self.charts = ChartConfig()
        self.export = ExportConfig()
        self.analytics = AnalyticsConfig()
        
        # Cargar variables de entorno si existen
        self._load_environment_variables()
        
        # Crear directorios necesarios
        self._ensure_directories()
    
    def _load_environment_variables(self):
        """Carga configuraciones desde variables de entorno"""
        env_path = BASE_DIR / ".env"
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except ImportError:
                pass  # dotenv es opcional
        
        # Sobrescribir con variables de entorno
        self.database.path = os.getenv("DATABASE_PATH", self.database.path)
        self.app.debug = os.getenv("DEBUG", "True").lower() == "true"
        self.app.host = os.getenv("HOST", self.app.host)
        self.app.port = int(os.getenv("PORT", self.app.port))
    
    def _ensure_directories(self):
        """Crea directorios necesarios si no existen"""
        directories = [
            Path(self.database.backup_dir),
            Path(self.export.export_dir),
            BASE_DIR / "data",
            BASE_DIR / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_chart_style(self) -> Dict[str, Any]:
        """Retorna estilo base para gráficas"""
        return {
            "font": {"family": self.charts.font_family},
            "title": {"font": {"size": self.charts.title_font_size}},
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "height": self.ui.chart_height
        }
    
    def get_color_palette(self, n_colors: int = None) -> list:
        """Retorna paleta de colores para gráficas"""
        colors = list(self.charts.default_colors.values())
        if n_colors:
            # Repetir colores si necesitamos más
            while len(colors) < n_colors:
                colors.extend(colors)
            return colors[:n_colors]
        return colors


# Instancia global de configuraciones
settings = Settings()