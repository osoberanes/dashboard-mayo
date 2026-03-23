import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
import logging
from pathlib import Path
from data_processor import MayoDataProcessor
from database_manager import DatabaseManager
from robust_data_processor import RobustDataProcessor

class FileManager:
    """
    Gestor de archivos para carga y validación de datos consulares.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.supported_extensions = ['.xls', '.xlsx', '.html', '.htm']
        
    def get_available_files(self, directory: str = ".") -> List[Dict[str, Any]]:
        """
        Busca archivos con estructura similar a mayo.xls en el directorio.
        
        Args:
            directory: Directorio a buscar
            
        Returns:
            Lista de diccionarios con información de archivos encontrados
        """
        files_info = []
        
        try:
            for file_path in Path(directory).rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    file_info = {
                        'nombre': file_path.name,
                        'ruta_completa': str(file_path),
                        'ruta_relativa': str(file_path.relative_to(Path(directory))),
                        'tamaño': file_path.stat().st_size,
                        'fecha_modificacion': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'extension': file_path.suffix.lower(),
                        'ya_cargado': self._is_file_loaded(file_path.name)
                    }
                    files_info.append(file_info)
                    
        except Exception as e:
            logging.error(f"Error buscando archivos: {e}")
            
        return sorted(files_info, key=lambda x: x['fecha_modificacion'], reverse=True)
    
    def _is_file_loaded(self, filename: str) -> bool:
        """Verifica si un archivo ya fue cargado en la base de datos"""
        history = self.db_manager.get_files_history()
        return filename in history['nombre_archivo'].values
    
    def validate_file_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Valida que el archivo tenga la estructura esperada.
        
        Args:
            file_path: Ruta del archivo a validar
            
        Returns:
            Diccionario con resultado de validación
        """
        result = {
            'is_valid': False,
            'error_message': '',
            'warnings': [],
            'preview_data': None,
            'columns_found': [],
            'rows_count': 0
        }
        
        try:
            # Usar el procesador robusto para validación
            robust_processor = RobustDataProcessor(file_path)
            validation_result = robust_processor.validate_structure()
            
            # Copiar todos los resultados
            result['is_valid'] = validation_result['is_valid']
            result['error_message'] = validation_result['error_message']
            result['warnings'] = validation_result.get('warnings', [])
            result['preview_data'] = validation_result.get('preview_data', None)
            result['columns_found'] = validation_result.get('columns_found', [])
            result['rows_count'] = validation_result.get('rows_count', 0)
            
        except Exception as e:
            result['error_message'] = f'Error al validar archivo: {str(e)}'
            
        return result
    
    def load_file_to_database(self, file_path: str, 
                             overwrite_duplicates: bool = False) -> Dict[str, Any]:
        """
        Carga un archivo validado a la base de datos.
        
        Args:
            file_path: Ruta del archivo a cargar
            overwrite_duplicates: Si True, sobrescribe duplicados existentes
            
        Returns:
            Diccionario con resultado de la carga
        """
        result = {
            'success': False,
            'message': '',
            'stats': {},
            'error_details': None
        }
        
        try:
            # Usar el procesador robusto
            robust_processor = RobustDataProcessor(file_path)
            
            # Validar archivo primero
            validation = robust_processor.validate_structure()
            if not validation['is_valid']:
                result['message'] = f'Archivo no válido: {validation["error_message"]}'
                return result
            
            # Cargar y limpiar datos en una operación
            df = robust_processor.load_and_clean_data()
            
            if df is None or df.empty:
                result['message'] = 'No se pudieron procesar los datos del archivo'
                return result
            
            # Si hay duplicados en base de datos y no queremos sobrescribir
            if not overwrite_duplicates:
                filename = Path(file_path).name
                if self._is_file_loaded(filename):
                    result['message'] = f'El archivo {filename} ya fue cargado. Use la opción de sobrescribir si desea actualizarlo.'
                    return result
            
            # Cargar a base de datos
            filename = Path(file_path).name
            stats = self.db_manager.insert_data_from_dataframe(df, filename)
            
            result['success'] = True
            result['stats'] = stats
            result['message'] = f'''Archivo cargado exitosamente:
                - {stats['inserted']} registros insertados
                - {stats['duplicates']} registros duplicados omitidos
                - {stats['errors']} errores
                - {stats['total_processed']} registros procesados'''
            
        except Exception as e:
            result['message'] = f'Error al cargar archivo: {str(e)}'
            result['error_details'] = str(e)
            logging.error(f"Error cargando archivo {file_path}: {e}")
            
        return result
    
    def batch_load_files(self, file_paths: List[str], 
                        overwrite_duplicates: bool = False) -> Dict[str, Any]:
        """
        Carga múltiples archivos en lote.
        
        Args:
            file_paths: Lista de rutas de archivos
            overwrite_duplicates: Si True, sobrescribe duplicados existentes
            
        Returns:
            Diccionario con resultados de la carga en lote
        """
        results = {
            'successful_files': [],
            'failed_files': [],
            'total_stats': {
                'inserted': 0,
                'duplicates': 0,
                'errors': 0,
                'total_processed': 0
            },
            'summary_message': ''
        }
        
        for file_path in file_paths:
            filename = Path(file_path).name
            load_result = self.load_file_to_database(file_path, overwrite_duplicates)
            
            if load_result['success']:
                results['successful_files'].append({
                    'filename': filename,
                    'stats': load_result['stats']
                })
                
                # Acumular estadísticas
                for key in results['total_stats']:
                    results['total_stats'][key] += load_result['stats'].get(key, 0)
                    
            else:
                results['failed_files'].append({
                    'filename': filename,
                    'error': load_result['message']
                })
        
        # Crear mensaje resumen
        successful_count = len(results['successful_files'])
        failed_count = len(results['failed_files'])
        
        results['summary_message'] = f'''Carga en lote completada:
            ✅ {successful_count} archivos cargados exitosamente
            ❌ {failed_count} archivos fallaron
            📊 Total: {results['total_stats']['inserted']} registros insertados
        '''
        
        return results
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del estado actual de la base de datos"""
        return {
            'stats': self.db_manager.get_summary_stats(),
            'date_range': self.db_manager.get_date_range(),
            'files_history': self.db_manager.get_files_history()
        }
    
    def delete_file_data(self, filename: str) -> Dict[str, Any]:
        """
        Elimina datos de un archivo específico de la base de datos.
        
        Args:
            filename: Nombre del archivo a eliminar
            
        Returns:
            Diccionario con resultado de la eliminación
        """
        try:
            deleted_count = self.db_manager.delete_data_by_file(filename)
            return {
                'success': True,
                'message': f'Se eliminaron {deleted_count} registros del archivo {filename}',
                'deleted_count': deleted_count
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al eliminar datos: {str(e)}',
                'deleted_count': 0
            }
    
    def export_data_to_excel(self, output_path: str, 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Exporta datos de la base de datos a Excel.
        
        Args:
            output_path: Ruta del archivo Excel a crear
            start_date: Fecha inicio del filtro (opcional)
            end_date: Fecha fin del filtro (opcional)
            
        Returns:
            Diccionario con resultado de la exportación
        """
        try:
            df = self.db_manager.get_all_data(start_date, end_date)
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'No hay datos para exportar'
                }
            
            df.to_excel(output_path, index=False)
            
            return {
                'success': True,
                'message': f'Datos exportados exitosamente a {output_path}',
                'records_exported': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al exportar datos: {str(e)}'
            }