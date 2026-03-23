"""
Tests para el módulo de base de datos
"""
import pytest
import pandas as pd
import tempfile
import os
from datetime import datetime, date

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager


@pytest.fixture
def temp_db():
    """Fixture para base de datos temporal"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db = DatabaseManager(db_path)
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_data():
    """Fixture con datos de ejemplo"""
    return pd.DataFrame({
        'servicio': ['Pasaporte Ordinario', 'RCM Expedición', 'Apostilla'],
        'categoria': ['PASAPORTES', 'RCM', 'NOTARIALES'],
        'costo_unitario': [165.0, 30.0, 50.0],
        'num_tramites': [10, 15, 5],
        'ingresos_totales': [1650.0, 450.0, 250.0],
        'fecha_emision': ['2025-01-01', '2025-01-02', '2025-01-03'],
        'formas_canceladas': [0, 1, 0]
    })


class TestDatabaseManager:
    """Tests para DatabaseManager"""
    
    def test_database_creation(self, temp_db):
        """Test creación de base de datos"""
        assert os.path.exists(temp_db.db_path)
        
        # Verificar tablas creadas
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
        assert 'consular_data' in tables
        assert 'archivos_cargados' in tables
    
    def test_insert_data(self, temp_db, sample_data):
        """Test inserción de datos"""
        result = temp_db.insert_data(sample_data, 'test_file.csv')
        
        assert result['insertados'] == 3
        assert result['duplicados'] == 0
        
        # Verificar datos insertados
        df = temp_db.load_data()
        assert len(df) == 3
        assert 'Pasaporte Ordinario' in df['servicio'].values
    
    def test_duplicate_handling(self, temp_db, sample_data):
        """Test manejo de duplicados"""
        # Insertar datos primera vez
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        # Insertar los mismos datos de nuevo
        result = temp_db.insert_data(sample_data, 'test_file2.csv')
        
        assert result['insertados'] == 0
        assert result['duplicados'] == 3
        
        # Verificar que no se duplicaron
        df = temp_db.load_data()
        assert len(df) == 3
    
    def test_load_data_with_filters(self, temp_db, sample_data):
        """Test carga de datos con filtros"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        # Filtrar por fecha
        df = temp_db.load_data('2025-01-01', '2025-01-01')
        assert len(df) == 1
        assert df.iloc[0]['servicio'] == 'Pasaporte Ordinario'
        
        # Filtrar rango
        df = temp_db.load_data('2025-01-01', '2025-01-02')
        assert len(df) == 2
    
    def test_summary_stats(self, temp_db, sample_data):
        """Test estadísticas resumen"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        stats = temp_db.get_summary_stats()
        
        assert stats['total_registros'] == 3
        assert stats['ingresos_totales'] == 2350.0
        assert stats['tramites_totales'] == 30
        assert stats['servicios_unicos'] == 3
        assert stats['categorias_unicas'] == 3
    
    def test_date_range(self, temp_db, sample_data):
        """Test rango de fechas"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        date_range = temp_db.get_date_range()
        
        assert date_range['fecha_min'] == '2025-01-01'
        assert date_range['fecha_max'] == '2025-01-03'
        assert date_range['total_registros'] == 3
    
    def test_services_list(self, temp_db, sample_data):
        """Test lista de servicios"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        services = temp_db.get_services_list()
        
        assert len(services) == 3
        assert 'Apostilla' in services
        assert 'Pasaporte Ordinario' in services
        assert 'RCM Expedición' in services
    
    def test_categories_list(self, temp_db, sample_data):
        """Test lista de categorías"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        categories = temp_db.get_categories_list()
        
        assert len(categories) == 3
        assert 'PASAPORTES' in categories
        assert 'RCM' in categories
        assert 'NOTARIALES' in categories
    
    def test_file_history(self, temp_db, sample_data):
        """Test historial de archivos"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        history = temp_db.get_file_history()
        
        assert len(history) == 1
        assert history.iloc[0]['nombre_archivo'] == 'test_file.csv'
        assert history.iloc[0]['registros_insertados'] == 3
        assert history.iloc[0]['registros_duplicados'] == 0
    
    def test_delete_by_file(self, temp_db, sample_data):
        """Test eliminación por archivo"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        # Verificar que hay datos
        df = temp_db.load_data()
        assert len(df) == 3
        
        # Eliminar por archivo
        deleted_count = temp_db.delete_by_file('test_file.csv')
        assert deleted_count == 3
        
        # Verificar que no hay datos
        df = temp_db.load_data()
        assert len(df) == 0
        
        # Verificar que se eliminó el registro de archivo
        history = temp_db.get_file_history()
        assert len(history) == 0
    
    def test_backup_database(self, temp_db, sample_data):
        """Test backup de base de datos"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        backup_path = temp_db.backup_database()
        
        assert os.path.exists(backup_path)
        assert backup_path.endswith('.db')
        
        # Verificar que el backup contiene datos
        backup_db = DatabaseManager(backup_path)
        df = backup_db.load_data()
        assert len(df) == 3
        
        # Cleanup
        os.unlink(backup_path)
    
    def test_temporal_data(self, temp_db, sample_data):
        """Test datos temporales agrupados"""
        temp_db.insert_data(sample_data, 'test_file.csv')
        
        # Test agrupación diaria
        temporal_data = temp_db.get_temporal_data('diario')
        assert len(temporal_data) == 3
        
        # Test agrupación mensual
        temporal_data = temp_db.get_temporal_data('mensual')
        assert len(temporal_data) == 1  # Todos en el mismo mes
        assert temporal_data.iloc[0]['ingresos_totales'] == 2350.0
        
        # Test con filtro por servicio
        temporal_data = temp_db.get_temporal_data('diario', 'Pasaporte Ordinario')
        assert len(temporal_data) == 1
        assert temporal_data.iloc[0]['ingresos_totales'] == 1650.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])