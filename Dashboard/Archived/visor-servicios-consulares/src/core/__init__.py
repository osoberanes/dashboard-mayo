"""
Módulos core del sistema
"""
import os
import sys

# Manejar importaciones relativas cuando se ejecuta como script
try:
    from .database import DatabaseManager
    from .analytics import AnalyticsEngine
    from .charts import ChartFactory
except ImportError:
    # Importaciones absolutas para testing
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.database import DatabaseManager
    from core.analytics import AnalyticsEngine
    from core.charts import ChartFactory

__all__ = ['DatabaseManager', 'AnalyticsEngine', 'ChartFactory']