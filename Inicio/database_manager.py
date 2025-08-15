import sqlite3
import pandas as pd
from datetime import datetime
import os
from typing import List, Optional, Dict, Any
import logging

class DatabaseManager:
    def __init__(self, db_path: str = None):
        """
        Gestor de base de datos para el dashboard consular.
        
        Args:
            db_path: Ruta a la base de datos SQLite
        """
        if db_path is None:
            # Determinar la ruta correcta basada en el directorio actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, "consular_data.db")
        else:
            self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Crea las tablas necesarias si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla principal de datos consulares
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consular_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servicio TEXT NOT NULL,
                    categoria TEXT,
                    costo_unitario REAL,
                    num_tramites INTEGER,
                    ingresos_totales REAL,
                    fecha_emision DATE NOT NULL,
                    formas_canceladas INTEGER DEFAULT 0,
                    archivo_origen TEXT,
                    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(servicio, fecha_emision, categoria)
                )
            ''')
            
            # Tabla de archivos cargados para control
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS archivos_cargados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_archivo TEXT NOT NULL,
                    ruta_archivo TEXT NOT NULL,
                    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    registros_insertados INTEGER,
                    registros_duplicados INTEGER,
                    estado TEXT DEFAULT 'success'
                )
            ''')
            
            # Índices para mejor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha_emision ON consular_data(fecha_emision)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_categoria ON consular_data(categoria)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_servicio ON consular_data(servicio)')
            
            conn.commit()
            
    def insert_data_from_dataframe(self, df: pd.DataFrame, archivo_origen: str) -> Dict[str, int]:
        """
        Inserta datos desde un DataFrame validando duplicados.
        
        Args:
            df: DataFrame con los datos a insertar
            archivo_origen: Nombre del archivo origen
            
        Returns:
            Dict con estadísticas de inserción
        """
        inserted = 0
        duplicates = 0
        errors = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for _, row in df.iterrows():
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO consular_data 
                        (servicio, categoria, costo_unitario, num_tramites, 
                         ingresos_totales, fecha_emision, formas_canceladas, archivo_origen)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['servicio'],
                        row['categoria'],
                        row['costo_unitario'],
                        row['num_tramites'],
                        row['ingresos_totales'],
                        row['fecha_emision'].strftime('%Y-%m-%d') if pd.notna(row['fecha_emision']) else None,
                        row.get('formas_canceladas', 0),
                        archivo_origen
                    ))
                    
                    if cursor.rowcount > 0:
                        inserted += 1
                    else:
                        duplicates += 1
                        
                except Exception as e:
                    errors += 1
                    logging.error(f"Error insertando fila: {e}")
            
            conn.commit()
            
            # Registrar el archivo cargado
            cursor.execute('''
                INSERT INTO archivos_cargados 
                (nombre_archivo, ruta_archivo, registros_insertados, registros_duplicados)
                VALUES (?, ?, ?, ?)
            ''', (archivo_origen, archivo_origen, inserted, duplicates))
            conn.commit()
            
        return {
            'inserted': inserted,
            'duplicates': duplicates,
            'errors': errors,
            'total_processed': len(df)
        }
    
    def get_all_data(self, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Obtiene todos los datos con filtros opcionales de fecha.
        
        Args:
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            
        Returns:
            DataFrame con todos los datos
        """
        query = "SELECT * FROM consular_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND fecha_emision >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND fecha_emision <= ?"
            params.append(end_date)
            
        query += " ORDER BY fecha_emision DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_categories_list(self) -> List[str]:
        """Obtiene lista única de categorías"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT categoria FROM consular_data WHERE categoria IS NOT NULL ORDER BY categoria")
            return [row[0] for row in cursor.fetchall()]
    
    def get_services_list(self) -> List[str]:
        """Obtiene lista única de servicios"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT servicio FROM consular_data ORDER BY servicio")
            return [row[0] for row in cursor.fetchall()]
    
    def get_date_range(self) -> Dict[str, Any]:
        """Obtiene el rango de fechas disponible en la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    MIN(fecha_emision) as fecha_min,
                    MAX(fecha_emision) as fecha_max,
                    COUNT(*) as total_registros
                FROM consular_data
            """)
            result = cursor.fetchone()
            return {
                'fecha_min': result[0],
                'fecha_max': result[1],
                'total_registros': result[2]
            }
    
    def get_files_history(self) -> pd.DataFrame:
        """Obtiene el historial de archivos cargados"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("""
                SELECT nombre_archivo, fecha_carga, registros_insertados, 
                       registros_duplicados, estado
                FROM archivos_cargados 
                ORDER BY fecha_carga DESC
            """, conn)
    
    def delete_data_by_file(self, archivo_origen: str) -> int:
        """
        Elimina datos por archivo origen.
        
        Args:
            archivo_origen: Nombre del archivo a eliminar
            
        Returns:
            Número de registros eliminados
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM consular_data WHERE archivo_origen = ?", (archivo_origen,))
            deleted = cursor.rowcount
            
            # También eliminar de la tabla de archivos cargados
            cursor.execute("DELETE FROM archivos_cargados WHERE nombre_archivo = ?", (archivo_origen,))
            conn.commit()
            
        return deleted
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas resumen de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_registros,
                    SUM(ingresos_totales) as ingresos_totales,
                    SUM(num_tramites) as tramites_totales,
                    SUM(formas_canceladas) as canceladas_totales,
                    COUNT(DISTINCT categoria) as categorias_unicas,
                    COUNT(DISTINCT servicio) as servicios_unicos
                FROM consular_data
            """)
            
            stats = cursor.fetchone()
            
            return {
                'total_registros': stats[0] or 0,
                'ingresos_totales': stats[1] or 0.0,
                'tramites_totales': stats[2] or 0,
                'canceladas_totales': stats[3] or 0,
                'categorias_unicas': stats[4] or 0,
                'servicios_unicos': stats[5] or 0
            }
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        Crea un backup de la base de datos.
        
        Args:
            backup_path: Ruta del backup (opcional)
            
        Returns:
            Ruta del archivo de backup creado
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"Inicio/backup_consular_{timestamp}.db"
            
        # Copiar la base de datos
        with sqlite3.connect(self.db_path) as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)
                
        return backup_path