import pandas as pd
from datetime import datetime
import os
from data_processor import MayoDataProcessor

class RobustDataProcessor:
    """
    Procesador de datos más robusto que maneja errores de carga mejor
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.original_processor = None
        
    def load_and_clean_data(self):
        """
        Carga y limpia datos en una sola operación más robusta
        """
        try:
            # Usar el procesador original
            self.original_processor = MayoDataProcessor(self.file_path)
            
            # Intentar cargar datos
            raw_df = self.original_processor.load_data()
            
            if raw_df is None or raw_df.empty:
                raise Exception(f"No se pudieron cargar datos del archivo: {self.file_path}")
            
            # Verificar que self.df esté asignado
            if self.original_processor.df is None:
                # Si por alguna razón no se asignó, asignarlo manualmente
                self.original_processor.df = raw_df
            
            # Limpiar datos
            cleaned_df = self.original_processor.clean_data()
            
            if cleaned_df is None or cleaned_df.empty:
                raise Exception("No se pudieron limpiar los datos del archivo")
            
            # Asignar a nuestra instancia también
            self.df = cleaned_df
            
            return cleaned_df
            
        except Exception as e:
            raise Exception(f"Error procesando archivo {self.file_path}: {str(e)}")
    
    def validate_structure(self):
        """
        Valida que el archivo tenga la estructura esperada
        """
        try:
            # Cargar solo para validación
            temp_processor = MayoDataProcessor(self.file_path)
            raw_df = temp_processor.load_data()
            
            if raw_df is None or raw_df.empty:
                return {
                    'is_valid': False,
                    'error_message': 'El archivo no contiene datos válidos',
                    'columns_found': [],
                    'rows_count': 0
                }
            
            # Validar columnas requeridas con flexibilidad para codificación
            required_patterns = {
                'Servicio': ['Servicio'],
                'Articulo': ['Articulo', 'Artículo'], 
                'Derechos': ['Derechos'],
                'Tramites': ['No. de trámites', 'No. de tramites', 'No. de tr�mites'],
                'Importe': ['Importe USD'],
                'Fecha': ['Fecha recaudación', 'Fecha recaudacion', 'Fecha recaudaci�n']
            }
            
            column_mapping = {}
            missing_columns = []
            
            for key, patterns in required_patterns.items():
                found = False
                for pattern in patterns:
                    if pattern in raw_df.columns:
                        column_mapping[key] = pattern
                        found = True
                        break
                if not found:
                    missing_columns.append(f'{key} (buscado: {", ".join(patterns)})')
            
            if missing_columns:
                return {
                    'is_valid': False,
                    'error_message': f'Columnas faltantes: {", ".join(missing_columns)}',
                    'columns_found': list(raw_df.columns),
                    'rows_count': len(raw_df)
                }
            
            # Intentar limpiar datos para validación completa
            try:
                if temp_processor.df is None:
                    temp_processor.df = raw_df
                    
                cleaned_df = temp_processor.clean_data()
                
                warnings = []
                
                # Verificar fechas válidas
                if 'fecha_emision' in cleaned_df.columns:
                    invalid_dates = cleaned_df[cleaned_df['fecha_emision'].isna()].shape[0]
                    if invalid_dates > 0:
                        warnings.append(f'{invalid_dates} registros con fechas inválidas')
                
                # Verificar duplicados internos
                duplicates = cleaned_df.duplicated(['servicio', 'fecha_emision', 'categoria']).sum()
                if duplicates > 0:
                    warnings.append(f'{duplicates} registros duplicados dentro del archivo')
                
                return {
                    'is_valid': True,
                    'error_message': '',
                    'warnings': warnings,
                    'preview_data': cleaned_df.head(10),
                    'columns_found': list(raw_df.columns),
                    'rows_count': len(raw_df)
                }
                
            except Exception as clean_error:
                return {
                    'is_valid': False,
                    'error_message': f'Error al limpiar datos: {str(clean_error)}',
                    'columns_found': list(raw_df.columns),
                    'rows_count': len(raw_df)
                }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error_message': f'Error al validar archivo: {str(e)}',
                'columns_found': [],
                'rows_count': 0
            }