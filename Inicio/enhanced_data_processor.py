import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
from database_manager import DatabaseManager
from data_processor import MayoDataProcessor

class EnhancedDataProcessor:
    """
    Procesador de datos mejorado que integra la base de datos local
    para análisis históricos y gestión centralizada de datos.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.df = None
        self._cached_data = None
        
    def initialize_from_database(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> bool:
        """
        Inicializa el procesador con datos de la base de datos.
        
        Args:
            start_date: Fecha inicio en formato YYYY-MM-DD
            end_date: Fecha fin en formato YYYY-MM-DD
            
        Returns:
            True si se cargaron datos exitosamente
        """
        try:
            self.df = self.db_manager.get_all_data(start_date, end_date)
            
            if not self.df.empty:
                # Aplicar filtros de exclusión y agrupación
                self._apply_service_filters_and_grouping()
                # Procesar fechas y columnas adicionales
                self._process_temporal_columns()
                self._cached_data = None  # Limpiar cache
                return True
            
            return False
            
        except Exception as e:
            print(f"Error inicializando desde base de datos: {e}")
            return False
    
    def _apply_service_filters_and_grouping(self):
        """Aplica filtros de exclusión y agrupación de servicios"""
        if self.df is None or self.df.empty:
            return
            
        # Excluir servicios COMPULSA
        self.df = self.df[~self.df['servicio'].str.contains('COMPULSA', case=False, na=False)]
        
        # Aplicar agrupación de servicios
        self.df['servicio'] = self.df['servicio'].apply(self._group_service_name)
    
    def _group_service_name(self, service_name: str) -> str:
        """Agrupa nombres de servicios según reglas definidas"""
        if pd.isna(service_name):
            return service_name
            
        service_upper = str(service_name).upper()
        
        # Agrupar RCM
        if 'RCM' in service_upper:
            return 'RCM - Expedición Diaria'
        
        # Agrupar PASAPORTES ORDINARIOS (incluyendo los cobrados al 50%)
        if 'PASAPORTE' in service_upper and ('ORDINARIO' in service_upper or '50%' in service_upper or '50 %' in service_upper):
            return 'Pasaportes Ordinarios'
        
        return service_name
    
    def _process_temporal_columns(self):
        """Agrega columnas temporales derivadas"""
        if self.df is None or self.df.empty:
            return
            
        # Convertir fecha si es necesario
        if 'fecha_emision' in self.df.columns:
            self.df['fecha_emision'] = pd.to_datetime(self.df['fecha_emision'])
            
            # Agregar columnas derivadas
            self.df['año'] = self.df['fecha_emision'].dt.year
            self.df['mes'] = self.df['fecha_emision'].dt.month
            self.df['mes_año'] = self.df['fecha_emision'].dt.to_period('M')
            self.df['dia_semana'] = self.df['fecha_emision'].dt.day_name()
            self.df['trimestre'] = self.df['fecha_emision'].dt.quarter
    
    def get_summary_stats(self, filtered_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas resumen, con opción de usar datos filtrados.
        
        Args:
            filtered_data: DataFrame filtrado opcional
            
        Returns:
            Diccionario con estadísticas resumen
        """
        df = filtered_data if filtered_data is not None else self.df
        
        if df is None or df.empty:
            return {
                'total_registros': 0,
                'fecha_inicio': None,
                'fecha_fin': None,
                'total_ingresos': 0.0,
                'total_tramites': 0,
                'categorias_unicas': 0,
                'servicios_unicos': 0,
                'archivos_origen': 0,
                'ingreso_diario_promedio': 0.0,
                'ingreso_diario_std': 0.0
            }
        
        # Calcular métricas de ingresos diarios
        ingreso_diario_promedio = 0.0
        ingreso_diario_std = 0.0
        
        if 'fecha_emision' in df.columns and 'ingresos_totales' in df.columns:
            ingresos_diarios = df.groupby('fecha_emision')['ingresos_totales'].sum()
            if len(ingresos_diarios) > 0:
                ingreso_diario_promedio = ingresos_diarios.mean()
                ingreso_diario_std = ingresos_diarios.std() if len(ingresos_diarios) > 1 else 0.0
        
        stats = {
            'total_registros': len(df),
            'fecha_inicio': df['fecha_emision'].min() if 'fecha_emision' in df.columns else None,
            'fecha_fin': df['fecha_emision'].max() if 'fecha_emision' in df.columns else None,
            'total_ingresos': df['ingresos_totales'].sum() if 'ingresos_totales' in df.columns else 0.0,
            'total_tramites': df['num_tramites'].sum() if 'num_tramites' in df.columns else 0,
            'categorias_unicas': df['categoria'].nunique() if 'categoria' in df.columns else 0,
            'servicios_unicos': df['servicio'].nunique() if 'servicio' in df.columns else 0,
            'archivos_origen': df['archivo_origen'].nunique() if 'archivo_origen' in df.columns else 0,
            'ingreso_diario_promedio': ingreso_diario_promedio,
            'ingreso_diario_std': ingreso_diario_std
        }
        
        return stats
    
    def get_data_by_category(self, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """Agrupa datos por categoría con filtros opcionales de fecha"""
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        return df.groupby('categoria').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum',
            'id': 'count'  # Contar registros
        }).rename(columns={'id': 'registros'}).reset_index()
    
    def get_data_by_service(self, categoria: Optional[str] = None,
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> pd.DataFrame:
        """Agrupa datos por servicio con filtros opcionales"""
        df = self._get_filtered_data(start_date, end_date)
        
        if categoria:
            df = df[df['categoria'] == categoria]
        
        if df.empty:
            return pd.DataFrame()
        
        return df.groupby(['categoria', 'servicio']).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'registros'}).reset_index()
    
    def get_temporal_data(self, group_by: str = 'mes',
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Obtiene datos agrupados temporalmente.
        
        Args:
            group_by: 'dia', 'mes', 'trimestre', 'año'
            start_date: Fecha inicio
            end_date: Fecha fin
        """
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Mapeo de agrupación temporal
        group_mapping = {
            'dia': 'fecha_emision',
            'mes': 'mes_año',
            'trimestre': 'trimestre',
            'año': 'año'
        }
        
        group_col = group_mapping.get(group_by, 'mes_año')
        
        if group_col not in df.columns:
            return pd.DataFrame()
        
        result = df.groupby(group_col).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'registros'}).reset_index()
        
        # Ordenar por fecha
        if group_by == 'mes':
            result = result.sort_values('mes_año')
        elif group_by == 'año':
            result = result.sort_values('año')
        elif group_by == 'dia':
            result = result.sort_values('fecha_emision')
        
        return result
    
    def get_comparative_analysis(self, compare_by: str = 'mes',
                               periods: int = 12) -> Dict[str, pd.DataFrame]:
        """
        Análisis comparativo entre períodos.
        
        Args:
            compare_by: 'mes', 'trimestre', 'año'
            periods: Número de períodos a comparar
            
        Returns:
            Diccionario con DataFrames de análisis comparativo
        """
        temporal_data = self.get_temporal_data(compare_by)
        
        if temporal_data.empty or len(temporal_data) < 2:
            return {}
        
        # Tomar los últimos N períodos
        recent_data = temporal_data.tail(periods)
        
        # Calcular cambios período a período
        recent_data = recent_data.copy()
        recent_data['ingresos_cambio'] = recent_data['ingresos_totales'].pct_change() * 100
        recent_data['tramites_cambio'] = recent_data['num_tramites'].pct_change() * 100
        
        # Análisis de tendencias
        ingresos_trend = 'creciente' if recent_data['ingresos_totales'].iloc[-1] > recent_data['ingresos_totales'].iloc[0] else 'decreciente'
        tramites_trend = 'creciente' if recent_data['num_tramites'].iloc[-1] > recent_data['num_tramites'].iloc[0] else 'decreciente'
        
        return {
            'temporal_data': recent_data,
            'trends': {
                'ingresos': ingresos_trend,
                'tramites': tramites_trend
            },
            'averages': {
                'ingresos_promedio': recent_data['ingresos_totales'].mean(),
                'tramites_promedio': recent_data['num_tramites'].mean(),
                'cancelaciones_promedio': recent_data['formas_canceladas'].mean()
            }
        }
    
    def get_top_services(self, by: str = 'ingresos', top_n: int = 10,
                        start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Obtiene los top N servicios por criterio especificado.
        
        Args:
            by: 'ingresos', 'tramites'
            top_n: Número de servicios a retornar
            start_date, end_date: Filtros de fecha
        """
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Mapeo de criterios
        criteria_mapping = {
            'ingresos': 'ingresos_totales',
            'tramites': 'num_tramites'
        }
        
        sort_column = criteria_mapping.get(by, 'ingresos_totales')
        
        services_data = df.groupby(['servicio', 'categoria']).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        }).reset_index()
        
        return services_data.nlargest(top_n, sort_column)
    
    def get_services_count_over_time(self, group_by: str = 'mes',
                                   start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Obtiene el número de servicios únicos a lo largo del tiempo.
        
        Args:
            group_by: 'dia', 'mes', 'trimestre', 'año'
            start_date: Fecha inicio
            end_date: Fecha fin
        """
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Mapeo de agrupación temporal
        group_mapping = {
            'dia': 'fecha_emision',
            'mes': 'mes_año',
            'trimestre': 'trimestre',
            'año': 'año'
        }
        
        group_col = group_mapping.get(group_by, 'mes_año')
        
        if group_col not in df.columns:
            return pd.DataFrame()
        
        # Contar servicios únicos por período
        result = df.groupby(group_col)['servicio'].nunique().reset_index()
        result.columns = [group_col, 'servicios_unicos']
        
        # Ordenar por fecha
        if group_by == 'mes':
            result = result.sort_values('mes_año')
        elif group_by == 'año':
            result = result.sort_values('año')
        elif group_by == 'dia':
            result = result.sort_values('fecha_emision')
        
        return result
    
    def get_service_temporal_data(self, service_name: str, group_by: str = 'mes',
                                start_date: Optional[str] = None, 
                                end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Obtiene datos temporales para un servicio específico.
        
        Args:
            service_name: Nombre del servicio
            group_by: 'dia', 'mes', 'trimestre', 'año'
            start_date: Fecha inicio
            end_date: Fecha fin
        """
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filtrar por servicio específico
        df_service = df[df['servicio'] == service_name]
        
        if df_service.empty:
            return pd.DataFrame()
        
        # Mapeo de agrupación temporal
        group_mapping = {
            'dia': 'fecha_emision',
            'mes': 'mes_año',
            'trimestre': 'trimestre',
            'año': 'año'
        }
        
        group_col = group_mapping.get(group_by, 'mes_año')
        
        if group_col not in df_service.columns:
            return pd.DataFrame()
        
        result = df_service.groupby(group_col).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'registros'}).reset_index()
        
        # Ordenar por fecha
        if group_by == 'mes':
            result = result.sort_values('mes_año')
        elif group_by == 'año':
            result = result.sort_values('año')
        elif group_by == 'dia':
            result = result.sort_values('fecha_emision')
        
        return result
    
    def get_period_timeline_data(self, metric: str, group_by: str = 'dia',
                               start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Obtiene datos de línea temporal para un período específico.
        
        Args:
            metric: 'ingresos_totales', 'num_tramites', 'servicios_unicos'
            group_by: 'dia', 'mes', 'trimestre', 'año'
            start_date: Fecha inicio
            end_date: Fecha fin
        """
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Mapeo de agrupación temporal
        group_mapping = {
            'dia': 'fecha_emision',
            'mes': 'mes_año',
            'trimestre': 'trimestre',
            'año': 'año'
        }
        
        group_col = group_mapping.get(group_by, 'dia')
        
        if group_col not in df.columns:
            return pd.DataFrame()
        
        if metric == 'servicios_unicos':
            # Para servicios únicos, contar servicios distintos por período
            result = df.groupby(group_col)['servicio'].nunique().reset_index()
            result.columns = [group_col, 'value']
        else:
            # Para ingresos y trámites, sumar valores
            result = df.groupby(group_col)[metric].sum().reset_index()
            result.columns = [group_col, 'value']
        
        # Ordenar por fecha
        if group_by == 'mes':
            result = result.sort_values('mes_año')
        elif group_by == 'año':
            result = result.sort_values('año')
        elif group_by == 'dia':
            result = result.sort_values('fecha_emision')
        
        # Convertir fechas para mejor visualización
        if group_by == 'dia':
            result['date_label'] = pd.to_datetime(result[group_col]).dt.strftime('%Y-%m-%d')
        elif group_by == 'mes':
            result['date_label'] = result[group_col].astype(str)
        else:
            result['date_label'] = result[group_col].astype(str)
        
        return result
    
    def get_efficiency_metrics(self, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> Dict[str, Any]:
        """Calcula métricas de eficiencia y rendimiento (sin cancelaciones)"""
        df = self._get_filtered_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        total_tramites = df['num_tramites'].sum()
        total_ingresos = df['ingresos_totales'].sum()
        
        # Evitar división por cero
        ingreso_promedio_por_tramite = total_ingresos / max(total_tramites, 1)
        
        # Calcular métricas de ingresos diarios
        ingreso_diario_promedio = 0.0
        ingreso_diario_std = 0.0
        
        if 'fecha_emision' in df.columns:
            ingresos_diarios = df.groupby('fecha_emision')['ingresos_totales'].sum()
            if len(ingresos_diarios) > 0:
                ingreso_diario_promedio = ingresos_diarios.mean()
                ingreso_diario_std = ingresos_diarios.std() if len(ingresos_diarios) > 1 else 0.0
        
        # Eficiencia por servicio
        servicio_efficiency = df.groupby('servicio').agg({
            'num_tramites': 'sum',
            'ingresos_totales': 'sum'
        })
        
        servicio_efficiency['ingreso_por_tramite'] = (
            servicio_efficiency['ingresos_totales'] / 
            servicio_efficiency['num_tramites'].replace(0, 1)
        )
        
        return {
            'global_metrics': {
                'ingreso_promedio_por_tramite': ingreso_promedio_por_tramite,
                'ingreso_diario_promedio': ingreso_diario_promedio,
                'ingreso_diario_std': ingreso_diario_std,
                'total_tramites': total_tramites,
                'total_ingresos': total_ingresos
            },
            'servicio_metrics': servicio_efficiency.to_dict('index')
        }
    
    def _get_filtered_data(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> pd.DataFrame:
        """Obtiene datos filtrados por fecha"""
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        df = self.df.copy()
        
        if start_date:
            df = df[df['fecha_emision'] >= start_date]
        
        if end_date:
            df = df[df['fecha_emision'] <= end_date]
        
        return df
    
    def filter_by_date(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Filtra datos por rango de fechas (compatible con versión anterior)"""
        return self._get_filtered_data(start_date, end_date)
    
    def get_categories_list(self) -> List[str]:
        """Obtiene lista de categorías únicas desde la base de datos"""
        return self.db_manager.get_categories_list()
    
    def get_services_list(self, categoria: Optional[str] = None) -> List[str]:
        """Obtiene lista de servicios, con filtro opcional por categoría"""
        if categoria and self.df is not None:
            # Si tenemos datos cargados, filtrar localmente
            filtered_df = self.df[self.df['categoria'] == categoria]
            return sorted(filtered_df['servicio'].dropna().unique())
        
        return self.db_manager.get_services_list()
    
    def refresh_data(self):
        """Refresca los datos desde la base de datos"""
        self.initialize_from_database()
    
    def get_file_sources(self) -> pd.DataFrame:
        """Obtiene información de archivos fuente en los datos actuales"""
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        if 'archivo_origen' not in self.df.columns:
            return pd.DataFrame()
        
        file_stats = self.df.groupby('archivo_origen').agg({
            'id': 'count',
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'fecha_emision': ['min', 'max']
        }).reset_index()
        
        # Aplanar columnas multi-nivel
        file_stats.columns = ['archivo_origen', 'registros', 'ingresos_totales', 
                             'num_tramites', 'fecha_min', 'fecha_max']
        
        return file_stats
    
    def export_current_data(self, file_path: str, format: str = 'excel'):
        """
        Exporta los datos actuales a archivo.
        
        Args:
            file_path: Ruta del archivo destino
            format: 'excel', 'csv'
        """
        if self.df is None or self.df.empty:
            raise ValueError("No hay datos para exportar")
        
        if format.lower() == 'excel':
            self.df.to_excel(file_path, index=False)
        elif format.lower() == 'csv':
            self.df.to_csv(file_path, index=False)
        else:
            raise ValueError("Formato no soportado. Use 'excel' o 'csv'")