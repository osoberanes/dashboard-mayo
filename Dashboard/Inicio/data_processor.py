import pandas as pd
from datetime import datetime
import os

class MayoDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        
    def load_data(self):
        """Carga el archivo mayo.xls (que puede ser HTML o Excel)"""
        try:
            # Intentar con xlrd para archivos .xls antiguos
            self.df = pd.read_excel(self.file_path, engine='xlrd')
        except:
            try:
                # Fallback a openpyxl
                self.df = pd.read_excel(self.file_path, engine='openpyxl')
            except:
                try:
                    # Si falla Excel, intentar como HTML
                    self.df = pd.read_html(self.file_path)[0]  # Tomar la primera tabla
                except Exception as e:
                    raise Exception(f"Error al cargar el archivo: {str(e)}")
        
        return self.df
    
    def clean_data(self):
        """Limpia y procesa los datos"""
        if self.df is None:
            raise Exception("Primero debe cargar los datos")
            
        # Renombrar columnas para facilitar el trabajo
        # Columnas del HTML: ['Servicio', 'Concepto', 'Articulo', 'Derechos', 'No. de trámites', 'Importe USD', ...]
        # Concepto está vacío, usamos Articulo como categoría
        columns_map = {
            'Servicio': 'servicio',
            'Articulo': 'categoria',  # Cambio: usar Articulo en lugar de Concepto
            'Derechos': 'costo_unitario',
            'No. de trámites': 'num_tramites',
            'Importe USD': 'ingresos_totales',
            'Fecha recaudación': 'fecha_emision',
            'No. cancelados': 'formas_canceladas'
        }
        
        # Solo renombrar columnas que existen
        existing_columns_map = {k: v for k, v in columns_map.items() if k in self.df.columns}
        self.df = self.df.rename(columns=existing_columns_map)
        
        # Limpiar y convertir fechas
        self.df['fecha_emision'] = pd.to_datetime(
            self.df['fecha_emision'], 
            format='%d/%m/%Y', 
            errors='coerce'
        )
        
        # Convertir columnas numéricas
        numeric_cols = ['costo_unitario', 'num_tramites', 'ingresos_totales', 'formas_canceladas']
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Eliminar filas con fechas inválidas
        self.df = self.df.dropna(subset=['fecha_emision'])
        
        # Agregar columnas derivadas
        self.df['año'] = self.df['fecha_emision'].dt.year
        self.df['mes'] = self.df['fecha_emision'].dt.month
        self.df['mes_año'] = self.df['fecha_emision'].dt.to_period('M')
        
        return self.df
    
    def get_summary_stats(self):
        """Obtiene estadísticas resumen de los datos"""
        if self.df is None:
            return {}
            
        stats = {
            'total_registros': len(self.df),
            'fecha_inicio': self.df['fecha_emision'].min(),
            'fecha_fin': self.df['fecha_emision'].max(),
            'total_ingresos': self.df['ingresos_totales'].sum(),
            'total_tramites': self.df['num_tramites'].sum(),
            'total_formas_canceladas': self.df['formas_canceladas'].sum(),
            'categorias_unicas': self.df['categoria'].nunique(),
            'servicios_unicos': self.df['servicio'].nunique()
        }
        
        return stats
    
    def get_data_by_category(self):
        """Agrupa datos por categoría"""
        return self.df.groupby('categoria').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index()
    
    def get_data_by_service(self, categoria=None):
        """Agrupa datos por servicio, opcionalmente filtrado por categoría"""
        df_filtered = self.df
        if categoria:
            df_filtered = self.df[self.df['categoria'] == categoria]
            
        return df_filtered.groupby(['categoria', 'servicio']).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index()
    
    def get_temporal_data(self, group_by='mes'):
        """Obtiene datos agrupados temporalmente"""
        if group_by == 'mes':
            group_col = 'mes_año'
        elif group_by == 'año':
            group_col = 'año'
        else:
            group_col = 'fecha_emision'
            
        return self.df.groupby(group_col).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index()
    
    def filter_by_date(self, start_date, end_date):
        """Filtra datos por rango de fechas"""
        mask = (self.df['fecha_emision'] >= start_date) & (self.df['fecha_emision'] <= end_date)
        return self.df.loc[mask]
    
    def get_categories_list(self):
        """Obtiene lista de categorías únicas"""
        return sorted(self.df['categoria'].dropna().unique())
    
    def get_services_list(self, categoria=None):
        """Obtiene lista de servicios, opcionalmente filtrado por categoría"""
        df_filtered = self.df
        if categoria:
            df_filtered = self.df[self.df['categoria'] == categoria]
        return sorted(df_filtered['servicio'].dropna().unique())