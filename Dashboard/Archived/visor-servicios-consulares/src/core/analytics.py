"""
Motor de análisis y procesamiento de datos
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

from .database import DatabaseManager
from ..config.settings import settings
from ..config.constants import DIAS_SEMANA, TEMPORAL_GROUPINGS


class AnalyticsEngine:
    """Motor de análisis de datos consulares"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def get_kpis(self, start_date: Optional[str] = None, 
                 end_date: Optional[str] = None) -> Dict[str, float]:
        """Calcula KPIs principales del período"""
        df = self.db.load_data(start_date, end_date)
        
        if df.empty:
            return self._empty_kpis()
        
        # Calcular métricas diarias para promedios
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        daily_data = df.groupby(df['fecha_emision'].dt.date).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        })
        
        return {
            'total_ingresos': float(df['ingresos_totales'].sum()),
            'total_tramites': int(df['num_tramites'].sum()),
            'promedio_diario_ingresos': float(daily_data['ingresos_totales'].mean()),
            'desviacion_std_ingresos': float(daily_data['ingresos_totales'].std()),
            'promedio_diario_tramites': float(daily_data['num_tramites'].mean()),
            'ingreso_por_tramite': float(df['ingresos_totales'].sum() / max(df['num_tramites'].sum(), 1)),
            'dias_con_datos': len(daily_data)
        }
    
    def _empty_kpis(self) -> Dict[str, float]:
        """KPIs vacíos para casos sin datos"""
        return {
            'total_ingresos': 0.0,
            'total_tramites': 0,
            'promedio_diario_ingresos': 0.0,
            'desviacion_std_ingresos': 0.0,
            'promedio_diario_tramites': 0.0,
            'ingreso_por_tramite': 0.0,
            'dias_con_datos': 0
        }
    
    def get_temporal_analysis(self, grouping: str = 'mensual',
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """Análisis temporal con agrupación configurable"""
        df = self.db.load_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        
        # Aplicar agrupación temporal
        if grouping == 'diario':
            df['periodo'] = df['fecha_emision'].dt.date
            df['periodo_str'] = df['fecha_emision'].dt.strftime('%Y-%m-%d')
        elif grouping == 'semanal':
            df['periodo'] = df['fecha_emision'].dt.to_period('W')
            df['periodo_str'] = df['periodo'].astype(str)
        elif grouping == 'mensual':
            df['periodo'] = df['fecha_emision'].dt.to_period('M')
            df['periodo_str'] = df['fecha_emision'].dt.strftime('%Y-%m')
        elif grouping == 'trimestral':
            df['periodo'] = df['fecha_emision'].dt.to_period('Q')
            df['periodo_str'] = df['periodo'].astype(str)
        elif grouping == 'anual':
            df['periodo'] = df['fecha_emision'].dt.year
            df['periodo_str'] = df['periodo'].astype(str)
        else:
            # Default a mensual
            df['periodo'] = df['fecha_emision'].dt.to_period('M')
            df['periodo_str'] = df['fecha_emision'].dt.strftime('%Y-%m')
        
        # Agrupar y calcular métricas
        result = df.groupby(['periodo', 'periodo_str']).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index()
        
        # Calcular métricas derivadas
        result['ingreso_por_tramite'] = result['ingresos_totales'] / result['num_tramites'].replace(0, 1)
        result['tasa_cancelacion'] = result['formas_canceladas'] / result['num_tramites'].replace(0, 1)
        
        return result.sort_values('periodo')
    
    def get_service_analysis(self, service: str,
                           grouping: str = 'mensual',
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, Any]:
        """Análisis detallado de un servicio específico"""
        df = self.db.load_data(start_date, end_date)
        
        if df.empty:
            return {'error': 'No hay datos disponibles'}
        
        # Filtrar por servicio
        service_data = df[df['servicio'] == service].copy()
        
        if service_data.empty:
            return {'error': f'No hay datos para el servicio: {service}'}
        
        # Análisis temporal del servicio
        temporal_data = self.get_temporal_analysis(grouping, start_date, end_date)
        service_temporal = service_data.copy()
        service_temporal['fecha_emision'] = pd.to_datetime(service_temporal['fecha_emision'])
        
        # Estadísticas del servicio
        daily_service = service_data.groupby(
            pd.to_datetime(service_data['fecha_emision']).dt.date
        ).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        })
        
        stats = {
            'total_ingresos': float(service_data['ingresos_totales'].sum()),
            'total_tramites': int(service_data['num_tramites'].sum()),
            'promedio_diario_ingresos': float(daily_service['ingresos_totales'].mean()),
            'promedio_diario_tramites': float(daily_service['num_tramites'].mean()),
            'desviacion_std_tramites': float(daily_service['num_tramites'].std()),
            'costo_promedio': float(service_data['costo_unitario'].mean()),
            'dias_activo': len(daily_service)
        }
        
        return {
            'stats': stats,
            'temporal_data': service_temporal,
            'daily_data': daily_service.reset_index()
        }
    
    def get_top_services(self, by: str = 'ingresos', top_n: int = 10,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """Obtiene top servicios por criterio especificado"""
        df = self.db.load_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por servicio
        service_stats = df.groupby('servicio').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index()
        
        # Calcular métricas derivadas
        service_stats['ingreso_por_tramite'] = (
            service_stats['ingresos_totales'] / service_stats['num_tramites'].replace(0, 1)
        )
        service_stats['tasa_cancelacion'] = (
            service_stats['formas_canceladas'] / service_stats['num_tramites'].replace(0, 1)
        )
        
        # Ordenar según criterio
        if by == 'ingresos':
            column = 'ingresos_totales'
        elif by == 'tramites':
            column = 'num_tramites'
        elif by == 'ingreso_por_tramite':
            column = 'ingreso_por_tramite'
        else:
            column = 'ingresos_totales'
        
        return service_stats.nlargest(top_n, column)
    
    def get_weekly_analysis(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict[str, Any]:
        """Análisis por día de la semana"""
        df = self.db.load_data(start_date, end_date)
        
        if df.empty:
            return {'error': 'No hay datos disponibles'}
        
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        df['dia_semana_en'] = df['fecha_emision'].dt.strftime('%A')
        df['dia_semana_es'] = df['dia_semana_en'].map(DIAS_SEMANA)
        
        # Agrupar por día específico para obtener totales diarios
        daily_totals = df.groupby(['fecha_emision', 'dia_semana_es']).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        }).reset_index()
        
        # Calcular promedios por día de la semana
        weekly_averages = daily_totals.groupby('dia_semana_es').agg({
            'ingresos_totales': 'mean',
            'num_tramites': 'mean'
        }).reset_index()
        
        # Ordenar por días de la semana
        day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        weekly_averages['dia_semana_es'] = pd.Categorical(
            weekly_averages['dia_semana_es'], 
            categories=day_order, 
            ordered=True
        )
        weekly_averages = weekly_averages.sort_values('dia_semana_es').reset_index(drop=True)
        
        # Encontrar días de mayor y menor actividad
        max_ingresos_idx = weekly_averages['ingresos_totales'].idxmax()
        min_ingresos_idx = weekly_averages['ingresos_totales'].idxmin()
        max_tramites_idx = weekly_averages['num_tramites'].idxmax()
        min_tramites_idx = weekly_averages['num_tramites'].idxmin()
        
        return {
            'weekly_data': weekly_averages,
            'max_ingresos_dia': weekly_averages.loc[max_ingresos_idx, 'dia_semana_es'],
            'max_ingresos_valor': weekly_averages.loc[max_ingresos_idx, 'ingresos_totales'],
            'min_ingresos_dia': weekly_averages.loc[min_ingresos_idx, 'dia_semana_es'],
            'min_ingresos_valor': weekly_averages.loc[min_ingresos_idx, 'ingresos_totales'],
            'max_tramites_dia': weekly_averages.loc[max_tramites_idx, 'dia_semana_es'],
            'max_tramites_valor': weekly_averages.loc[max_tramites_idx, 'num_tramites'],
            'min_tramites_dia': weekly_averages.loc[min_tramites_idx, 'dia_semana_es'],
            'min_tramites_valor': weekly_averages.loc[min_tramites_idx, 'num_tramites']
        }
    
    def compare_periods(self, period_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compara múltiples períodos"""
        results = {}
        
        for i, config in enumerate(period_configs):
            period_name = config.get('name', f'Período {i+1}')
            start_date = config.get('start_date')
            end_date = config.get('end_date')
            
            # Obtener datos del período
            kpis = self.get_kpis(start_date, end_date)
            temporal_data = self.get_temporal_analysis(
                config.get('grouping', 'mensual'), 
                start_date, 
                end_date
            )
            
            results[period_name] = {
                'kpis': kpis,
                'temporal_data': temporal_data,
                'config': config
            }
        
        return results
    
    def get_service_grouping_analysis(self) -> Dict[str, Any]:
        """Análisis de servicios agrupables según configuración"""
        df = self.db.load_data()
        
        if df.empty:
            return {'error': 'No hay datos disponibles'}
        
        groupable_services = settings.analytics.groupable_services
        analysis = {}
        
        for group_name, config in groupable_services.items():
            pattern = config['pattern']
            case_sensitive = config.get('case_sensitive', False)
            
            # Filtrar servicios que coinciden con el patrón
            if case_sensitive:
                matching_services = df[df['servicio'].str.contains(pattern, na=False)]
            else:
                matching_services = df[df['servicio'].str.contains(pattern, na=False, case=False)]
            
            if not matching_services.empty:
                # Estadísticas del grupo
                unique_services = matching_services['servicio'].nunique()
                total_records = len(matching_services)
                total_ingresos = matching_services['ingresos_totales'].sum()
                total_tramites = matching_services['num_tramites'].sum()
                
                analysis[group_name] = {
                    'servicios_unicos': unique_services,
                    'registros_totales': total_records,
                    'ingresos_totales': total_ingresos,
                    'tramites_totales': total_tramites,
                    'servicios_detalle': matching_services['servicio'].value_counts().to_dict(),
                    'grouped_name': config['grouped_name']
                }
        
        return analysis
    
    def predict_next_period(self, service: Optional[str] = None,
                          periods: int = 3) -> Dict[str, Any]:
        """Predicción simple basada en tendencias históricas"""
        # Obtener datos históricos
        df = self.db.load_data()
        
        if df.empty:
            return {'error': 'No hay datos suficientes para predicción'}
        
        # Filtrar por servicio si se especifica
        if service:
            df = df[df['servicio'] == service]
            if df.empty:
                return {'error': f'No hay datos para el servicio: {service}'}
        
        # Análisis temporal mensual
        temporal_data = self.get_temporal_analysis('mensual')
        
        if len(temporal_data) < 3:
            return {'error': 'Se necesitan al menos 3 meses de datos para predicción'}
        
        # Predicción simple basada en tendencia lineal
        x = np.arange(len(temporal_data))
        y_ingresos = temporal_data['ingresos_totales'].values
        y_tramites = temporal_data['num_tramites'].values
        
        # Regresión lineal simple
        ingresos_trend = np.polyfit(x, y_ingresos, 1)
        tramites_trend = np.polyfit(x, y_tramites, 1)
        
        # Generar predicciones
        future_x = np.arange(len(temporal_data), len(temporal_data) + periods)
        predicted_ingresos = np.polyval(ingresos_trend, future_x)
        predicted_tramites = np.polyval(tramites_trend, future_x)
        
        # Asegurar valores no negativos
        predicted_ingresos = np.maximum(predicted_ingresos, 0)
        predicted_tramites = np.maximum(predicted_tramites, 0)
        
        return {
            'historical_data': temporal_data,
            'predictions': {
                'ingresos': predicted_ingresos.tolist(),
                'tramites': predicted_tramites.astype(int).tolist(),
                'periods': periods
            },
            'trends': {
                'ingresos_slope': float(ingresos_trend[0]),
                'tramites_slope': float(tramites_trend[0])
            }
        }