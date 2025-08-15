import sqlite3
import pandas as pd
from typing import Dict, List, Tuple, Any
from database_manager import DatabaseManager
import re

class ServiceGroupingManager:
    """
    Gestor para agrupar servicios similares en categorías más generales.
    Permite crear agrupaciones como RCM → 'Expedición Diaria' y PASAPORTES ORDINARIOS → 'Pasaportes Ordinarios'
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.grouping_rules = {
            'RCM': {
                'grouped_name': 'RCM - Expedición Diaria',
                'pattern': r'RCM\s*-',
                'description': 'Agrupación de todos los trámites RCM por estado y tipo'
            },
            'PASAPORTES_ORDINARIOS': {
                'grouped_name': 'Pasaportes Ordinarios',
                'pattern': r'PASAPORTES?\s+(ORDINARIOS?|.*50\s*%)',
                'description': 'Agrupación de todos los pasaportes ordinarios y cobrados al 50%'
            }
        }
    
    def analyze_groupable_services(self) -> Dict[str, Any]:
        """
        Analiza los servicios que pueden ser agrupados según las reglas definidas.
        
        Returns:
            Diccionario con análisis detallado de cada grupo
        """
        df = self.db_manager.get_all_data()
        analysis = {}
        
        for group_key, rule in self.grouping_rules.items():
            # Buscar servicios que coincidan con el patrón
            pattern_mask = df['servicio'].str.contains(rule['pattern'], case=False, na=False, regex=True)
            matching_services = df[pattern_mask]
            
            if not matching_services.empty:
                # Análisis por servicio individual
                service_breakdown = matching_services.groupby('servicio').agg({
                    'num_tramites': 'sum',
                    'ingresos_totales': 'sum',
                    'formas_canceladas': 'sum',
                    'fecha_emision': ['min', 'max', 'count']
                }).round(2)
                
                # Aplanar columnas multi-nivel
                service_breakdown.columns = ['tramites_total', 'ingresos_total', 'canceladas_total', 
                                           'fecha_min', 'fecha_max', 'registros_count']
                
                # Totales agregados
                totals = {
                    'total_services': len(service_breakdown),
                    'total_records': len(matching_services),
                    'total_tramites': matching_services['num_tramites'].sum(),
                    'total_ingresos': matching_services['ingresos_totales'].sum(),
                    'total_canceladas': matching_services['formas_canceladas'].sum(),
                    'fecha_range': f"{matching_services['fecha_emision'].min()} a {matching_services['fecha_emision'].max()}"
                }
                
                analysis[group_key] = {
                    'rule': rule,
                    'breakdown': service_breakdown.reset_index(),
                    'totals': totals,
                    'sample_services': matching_services['servicio'].unique()[:10].tolist()
                }
        
        return analysis
    
    def create_grouped_services_table(self) -> bool:
        """
        Crea una tabla temporal con servicios agrupados para análisis.
        
        Returns:
            True si se creó exitosamente
        """
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Crear tabla temporal para servicios agrupados
                cursor.execute('''
                    CREATE TEMPORARY TABLE IF NOT EXISTS grouped_services_view AS
                    SELECT 
                        id,
                        CASE 
                            WHEN servicio LIKE '%RCM%' THEN 'RCM - Expedición Diaria'
                            WHEN servicio LIKE '%PASPORTE%ORDINARIO%' OR servicio LIKE '%PASAPORTES ORDINARIOS%' OR servicio LIKE '%50%' THEN 'Pasaportes Ordinarios'
                            ELSE servicio
                        END as servicio_agrupado,
                        servicio as servicio_original,
                        categoria,
                        costo_unitario,
                        num_tramites,
                        ingresos_totales,
                        fecha_emision,
                        formas_canceladas,
                        archivo_origen
                    FROM consular_data
                ''')
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error creando tabla de servicios agrupados: {e}")
            return False
    
    def get_grouped_data(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Obtiene datos con servicios agrupados.
        
        Args:
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            
        Returns:
            DataFrame con servicios agrupados
        """
        try:
            # Crear vista temporal
            self.create_grouped_services_table()
            
            query = '''
                SELECT 
                    servicio_agrupado as servicio,
                    servicio_original,
                    categoria,
                    SUM(num_tramites) as num_tramites,
                    SUM(ingresos_totales) as ingresos_totales,
                    SUM(formas_canceladas) as formas_canceladas,
                    fecha_emision,
                    COUNT(*) as registros_count
                FROM grouped_services_view
                WHERE 1=1
            '''
            
            params = []
            if start_date:
                query += " AND fecha_emision >= ?"
                params.append(start_date)
            if end_date:
                query += " AND fecha_emision <= ?"
                params.append(end_date)
            
            query += '''
                GROUP BY servicio_agrupado, fecha_emision, categoria
                ORDER BY fecha_emision DESC, ingresos_totales DESC
            '''
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                return pd.read_sql_query(query, conn, params=params)
                
        except Exception as e:
            print(f"Error obteniendo datos agrupados: {e}")
            return pd.DataFrame()
    
    def get_grouping_breakdown(self, group_name: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Obtiene el desglose detallado de un grupo específico.
        
        Args:
            group_name: Nombre del grupo ('RCM - Expedición Diaria' o 'Pasaportes Ordinarios')
            start_date: Fecha inicio
            end_date: Fecha fin
            
        Returns:
            DataFrame con desglose detallado
        """
        try:
            self.create_grouped_services_table()
            
            query = '''
                SELECT 
                    servicio_original as servicio,
                    categoria,
                    SUM(num_tramites) as num_tramites,
                    SUM(ingresos_totales) as ingresos_totales,
                    SUM(formas_canceladas) as formas_canceladas,
                    COUNT(DISTINCT fecha_emision) as dias_activo,
                    MIN(fecha_emision) as fecha_min,
                    MAX(fecha_emision) as fecha_max,
                    COUNT(*) as total_registros
                FROM grouped_services_view
                WHERE servicio_agrupado = ?
            '''
            
            params = [group_name]
            
            if start_date:
                query += " AND fecha_emision >= ?"
                params.append(start_date)
            if end_date:
                query += " AND fecha_emision <= ?"
                params.append(end_date)
            
            query += '''
                GROUP BY servicio_original, categoria
                ORDER BY ingresos_totales DESC
            '''
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                return pd.read_sql_query(query, conn, params=params)
                
        except Exception as e:
            print(f"Error obteniendo desglose de grupo {group_name}: {e}")
            return pd.DataFrame()
    
    def apply_permanent_grouping(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Aplica la agrupación permanentemente a la base de datos.
        PRECAUCIÓN: Esto modifica los datos originales.
        
        Args:
            confirm: Debe ser True para confirmar la operación
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not confirm:
            return {
                'success': False,
                'message': 'Operación requiere confirmación explícita',
                'changes_preview': self.get_grouping_preview()
            }
        
        try:
            updated_records = 0
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Actualizar servicios RCM
                cursor.execute('''
                    UPDATE consular_data 
                    SET servicio = 'RCM - Expedición Diaria'
                    WHERE servicio LIKE '%RCM%'
                ''')
                rcm_updated = cursor.rowcount
                
                # Actualizar servicios PASAPORTES ORDINARIOS (incluyendo 50%)
                cursor.execute('''
                    UPDATE consular_data 
                    SET servicio = 'Pasaportes Ordinarios'
                    WHERE servicio LIKE '%PASPORTE%ORDINARIO%' OR servicio LIKE '%PASAPORTES ORDINARIOS%' OR servicio LIKE '%50%'
                ''')
                pasaportes_updated = cursor.rowcount
                
                updated_records = rcm_updated + pasaportes_updated
                conn.commit()
            
            return {
                'success': True,
                'message': f'Agrupación aplicada exitosamente. {updated_records} registros actualizados.',
                'details': {
                    'rcm_updated': rcm_updated,
                    'pasaportes_updated': pasaportes_updated,
                    'total_updated': updated_records
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error aplicando agrupación: {str(e)}'
            }
    
    def get_grouping_preview(self) -> Dict[str, Any]:
        """
        Obtiene una vista previa de los cambios que se aplicarían con la agrupación.
        
        Returns:
            Diccionario con preview de cambios
        """
        df = self.db_manager.get_all_data()
        
        # Servicios RCM
        rcm_mask = df['servicio'].str.contains('RCM', case=False, na=False)
        rcm_services = df[rcm_mask]['servicio'].unique()
        rcm_count = len(df[rcm_mask])
        
        # Servicios PASAPORTES ORDINARIOS (incluyendo 50%)
        pasaporte_mask = df['servicio'].str.contains(r'PASPORTE.*(ORDINARIO|50\s*%)', case=False, na=False, regex=True)
        pasaporte_services = df[pasaporte_mask]['servicio'].unique()
        pasaporte_count = len(df[pasaporte_mask])
        
        return {
            'rcm_grouping': {
                'current_services': rcm_services.tolist(),
                'records_affected': rcm_count,
                'new_name': 'RCM - Expedición Diaria'
            },
            'pasaportes_grouping': {
                'current_services': pasaporte_services.tolist(),
                'records_affected': pasaporte_count,
                'new_name': 'Pasaportes Ordinarios'
            },
            'total_records_affected': rcm_count + pasaporte_count
        }