"""
Gestor de base de datos optimizado para servicios consulares
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import logging
from contextlib import contextmanager

from ..config.settings import settings
from ..config.constants import DB_COLUMNS, HTML_COLUMN_MAPPING


class DatabaseManager:
    """Gestor optimizado de base de datos SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database.path
        self.logger = logging.getLogger(__name__)
        self._ensure_database()
    
    def _ensure_database(self):
        """Crea la base de datos y tablas si no existen"""
        with self.get_connection() as conn:
            # Tabla principal de datos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consular_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servicio TEXT NOT NULL,
                    categoria TEXT,
                    costo_unitario REAL,
                    num_tramites INTEGER DEFAULT 0,
                    ingresos_totales REAL DEFAULT 0,
                    fecha_emision DATE NOT NULL,
                    formas_canceladas INTEGER DEFAULT 0,
                    archivo_origen TEXT,
                    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(servicio, fecha_emision, categoria)
                )
            """)
            
            # Tabla de control de archivos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archivos_cargados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_archivo TEXT UNIQUE NOT NULL,
                    ruta_archivo TEXT,
                    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    registros_insertados INTEGER DEFAULT 0,
                    registros_duplicados INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'exitoso'
                )
            """)
            
            # Índices para optimización
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha_emision ON consular_data(fecha_emision)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_servicio ON consular_data(servicio)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_categoria ON consular_data(categoria)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_archivo_origen ON consular_data(archivo_origen)")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones de BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error en base de datos: {e}")
            raise
        finally:
            conn.close()
    
    def load_data(self, start_date: Optional[str] = None, 
                  end_date: Optional[str] = None) -> pd.DataFrame:
        """Carga datos de la BD con filtros opcionales de fecha"""
        query = "SELECT * FROM consular_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND fecha_emision >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND fecha_emision <= ?"
            params.append(end_date)
        
        query += " ORDER BY fecha_emision DESC"
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
                df['fecha_carga'] = pd.to_datetime(df['fecha_carga'])
        
        return df
    
    def insert_data(self, df: pd.DataFrame, archivo_origen: str) -> Dict[str, int]:
        """Inserta datos con control de duplicados"""
        if df.empty:
            return {'insertados': 0, 'duplicados': 0}
        
        # Preparar datos
        df_clean = df.copy()
        df_clean['archivo_origen'] = archivo_origen
        df_clean['fecha_carga'] = datetime.now()
        
        insertados = 0
        duplicados = 0
        
        with self.get_connection() as conn:
            for _, row in df_clean.iterrows():
                try:
                    # Convertir timestamp a string para SQLite
                    fecha_emision = row['fecha_emision']
                    if hasattr(fecha_emision, 'strftime'):
                        fecha_emision = fecha_emision.strftime('%Y-%m-%d')
                    elif pd.isna(fecha_emision):
                        fecha_emision = None
                    
                    fecha_carga = row['fecha_carga']
                    if hasattr(fecha_carga, 'strftime'):
                        fecha_carga = fecha_carga.strftime('%Y-%m-%d %H:%M:%S')
                    
                    conn.execute("""
                        INSERT INTO consular_data 
                        (servicio, categoria, costo_unitario, num_tramites, 
                         ingresos_totales, fecha_emision, formas_canceladas, 
                         archivo_origen, fecha_carga)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['servicio'], row['categoria'], row['costo_unitario'],
                        row['num_tramites'], row['ingresos_totales'], 
                        fecha_emision, row['formas_canceladas'],
                        row['archivo_origen'], fecha_carga
                    ))
                    insertados += 1
                except sqlite3.IntegrityError:
                    duplicados += 1
            
            # Registrar carga de archivo
            conn.execute("""
                INSERT OR REPLACE INTO archivos_cargados 
                (nombre_archivo, ruta_archivo, registros_insertados, registros_duplicados)
                VALUES (?, ?, ?, ?)
            """, (Path(archivo_origen).name, archivo_origen, insertados, duplicados))
        
        return {'insertados': insertados, 'duplicados': duplicados}
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas resumen de la BD"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) FROM consular_data")
            total_registros = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(ingresos_totales) FROM consular_data")
            ingresos_totales = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(num_tramites) FROM consular_data")
            tramites_totales = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT categoria) FROM consular_data")
            categorias_unicas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT servicio) FROM consular_data")
            servicios_unicos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT archivo_origen) FROM consular_data")
            archivos_cargados = cursor.fetchone()[0]
        
        return {
            'total_registros': total_registros,
            'ingresos_totales': ingresos_totales,
            'tramites_totales': tramites_totales,
            'categorias_unicas': categorias_unicas,
            'servicios_unicos': servicios_unicos,
            'archivos_cargados': archivos_cargados
        }
    
    def get_date_range(self) -> Dict[str, Any]:
        """Obtiene rango de fechas disponible"""
        with self.get_connection() as conn:
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
    
    def get_services_list(self) -> List[str]:
        """Obtiene lista de servicios únicos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT servicio FROM consular_data ORDER BY servicio")
            return [row[0] for row in cursor.fetchall()]
    
    def get_categories_list(self) -> List[str]:
        """Obtiene lista de categorías únicas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT categoria FROM consular_data ORDER BY categoria")
            return [row[0] for row in cursor.fetchall() if row[0]]
    
    def get_file_history(self) -> pd.DataFrame:
        """Obtiene historial de archivos cargados"""
        with self.get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT * FROM archivos_cargados 
                ORDER BY fecha_carga DESC
            """, conn)
            
            if not df.empty:
                df['fecha_carga'] = pd.to_datetime(df['fecha_carga'])
        
        return df
    
    def delete_by_file(self, archivo_origen: str) -> int:
        """Elimina registros por archivo origen"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contar registros a eliminar
            cursor.execute("SELECT COUNT(*) FROM consular_data WHERE archivo_origen = ?", 
                          (archivo_origen,))
            count = cursor.fetchone()[0]
            
            # Eliminar registros
            cursor.execute("DELETE FROM consular_data WHERE archivo_origen = ?", 
                          (archivo_origen,))
            
            # Eliminar registro de archivo
            cursor.execute("DELETE FROM archivos_cargados WHERE ruta_archivo = ?", 
                          (archivo_origen,))
        
        return count
    
    def backup_database(self) -> str:
        """Crea backup de la base de datos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = Path(settings.database.backup_dir) / f"backup_{timestamp}.db"
        
        # Asegurar que el directorio existe
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Crear backup
        with self.get_connection() as conn:
            backup_conn = sqlite3.connect(str(backup_path))
            conn.backup(backup_conn)
            backup_conn.close()
        
        return str(backup_path)
    
    def cleanup_old_backups(self, days: int = None):
        """Limpia backups antiguos"""
        days = days or settings.database.backup_retention_days
        cutoff_date = datetime.now() - timedelta(days=days)
        
        backup_dir = Path(settings.database.backup_dir)
        if not backup_dir.exists():
            return
        
        for backup_file in backup_dir.glob("backup_*.db"):
            try:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    self.logger.info(f"Backup eliminado: {backup_file}")
            except Exception as e:
                self.logger.error(f"Error eliminando backup {backup_file}: {e}")
    
    def get_temporal_data(self, grouping: str = 'mensual', 
                         service: Optional[str] = None) -> pd.DataFrame:
        """Obtiene datos agrupados temporalmente"""
        df = self.load_data()
        
        if df.empty:
            return pd.DataFrame()
        
        # Filtrar por servicio si se especifica
        if service:
            df = df[df['servicio'] == service]
        
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        
        # Agrupar según el tipo especificado
        if grouping == 'diario':
            df['periodo'] = df['fecha_emision'].dt.date
        elif grouping == 'semanal':
            df['periodo'] = df['fecha_emision'].dt.to_period('W')
        elif grouping == 'mensual':
            df['periodo'] = df['fecha_emision'].dt.to_period('M')
        elif grouping == 'trimestral':
            df['periodo'] = df['fecha_emision'].dt.to_period('Q')
        elif grouping == 'anual':
            df['periodo'] = df['fecha_emision'].dt.year
        else:
            df['periodo'] = df['fecha_emision'].dt.date
        
        # Agrupar y sumar
        result = df.groupby('periodo').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index()
        
        result['periodo'] = result['periodo'].astype(str)
        
        return result