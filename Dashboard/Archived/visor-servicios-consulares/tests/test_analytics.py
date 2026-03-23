"""
Tests para el módulo de analytics
"""
import pytest
import pandas as pd
import tempfile
import os
from datetime import datetime, date

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager
from src.core.analytics import AnalyticsEngine


@pytest.fixture
def analytics_setup():
    """Fixture para setup de analytics con datos de prueba"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db = DatabaseManager(db_path)
    analytics = AnalyticsEngine(db)
    
    # Datos de prueba con varios días
    sample_data = pd.DataFrame({
        'servicio': ['Pasaporte Ordinario'] * 5 + ['RCM Expedición'] * 5,
        'categoria': ['PASAPORTES'] * 5 + ['RCM'] * 5,
        'costo_unitario': [165.0] * 5 + [30.0] * 5,
        'num_tramites': [10, 15, 8, 12, 20] + [25, 30, 15, 18, 22],
        'ingresos_totales': [1650.0, 2475.0, 1320.0, 1980.0, 3300.0] + [750.0, 900.0, 450.0, 540.0, 660.0],
        'fecha_emision': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'] * 2,
        'formas_canceladas': [0, 1, 0, 2, 1] + [1, 0, 2, 1, 0]
    })
    
    db.insert_data(sample_data, 'test_analytics.csv')
    
    yield db, analytics
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


class TestAnalyticsEngine:
    """Tests para AnalyticsEngine"""
    
    def test_get_kpis(self, analytics_setup):
        """Test cálculo de KPIs"""
        db, analytics = analytics_setup
        
        kpis = analytics.get_kpis()
        
        assert kpis['total_ingresos'] == 13025.0  # Suma de todos los ingresos
        assert kpis['total_tramites'] == 175  # Suma de todos los trámites
        assert kpis['dias_con_datos'] == 5
        assert kpis['ingreso_por_tramite'] > 0
        assert kpis['promedio_diario_ingresos'] > 0
        assert kpis['desviacion_std_ingresos'] >= 0
    
    def test_get_kpis_with_filters(self, analytics_setup):
        """Test KPIs con filtros de fecha"""
        db, analytics = analytics_setup
        
        # Filtrar solo primer día
        kpis = analytics.get_kpis('2025-01-01', '2025-01-01')
        
        assert kpis['total_ingresos'] == 2400.0  # 1650 + 750
        assert kpis['total_tramites'] == 35  # 10 + 25
        assert kpis['dias_con_datos'] == 1
    
    def test_get_temporal_analysis(self, analytics_setup):
        """Test análisis temporal"""
        db, analytics = analytics_setup
        
        # Test agrupación diaria
        temporal_data = analytics.get_temporal_analysis('diario')
        
        assert len(temporal_data) == 5  # 5 días de datos
        assert 'ingresos_totales' in temporal_data.columns
        assert 'num_tramites' in temporal_data.columns
        assert 'ingreso_por_tramite' in temporal_data.columns
        assert 'tasa_cancelacion' in temporal_data.columns
        
        # Verificar cálculos
        day1_data = temporal_data[temporal_data['periodo_str'] == '2025-01-01'].iloc[0]
        assert day1_data['ingresos_totales'] == 2400.0
        assert day1_data['num_tramites'] == 35
    
    def test_get_temporal_analysis_groupings(self, analytics_setup):
        """Test diferentes agrupaciones temporales"""
        db, analytics = analytics_setup
        
        # Test mensual
        monthly_data = analytics.get_temporal_analysis('mensual')
        assert len(monthly_data) == 1  # Todo en el mismo mes
        assert monthly_data.iloc[0]['ingresos_totales'] == 13025.0
        
        # Test anual
        yearly_data = analytics.get_temporal_analysis('anual')
        assert len(yearly_data) == 1  # Todo en el mismo año
        assert yearly_data.iloc[0]['ingresos_totales'] == 13025.0
    
    def test_get_service_analysis(self, analytics_setup):
        """Test análisis de servicio específico"""
        db, analytics = analytics_setup
        
        # Analizar Pasaporte Ordinario
        service_analysis = analytics.get_service_analysis('Pasaporte Ordinario')
        
        assert 'stats' in service_analysis
        assert 'temporal_data' in service_analysis
        
        stats = service_analysis['stats']
        assert stats['total_ingresos'] == 10725.0  # Suma de pasaportes
        assert stats['total_tramites'] == 65
        assert stats['dias_activo'] == 5
        assert stats['costo_promedio'] == 165.0
    
    def test_get_service_analysis_nonexistent(self, analytics_setup):
        """Test análisis de servicio que no existe"""
        db, analytics = analytics_setup
        
        result = analytics.get_service_analysis('Servicio Inexistente')
        
        assert 'error' in result
        assert 'No hay datos para el servicio' in result['error']
    
    def test_get_top_services(self, analytics_setup):
        """Test top servicios"""
        db, analytics = analytics_setup
        
        # Top por ingresos
        top_ingresos = analytics.get_top_services(by='ingresos', top_n=5)
        
        assert len(top_ingresos) == 2  # Solo 2 servicios en datos
        assert 'Pasaporte Ordinario' in top_ingresos['servicio'].values
        assert 'RCM Expedición' in top_ingresos['servicio'].values
        
        # Verificar orden (pasaportes debe ser primero por ingresos)
        assert top_ingresos.iloc[0]['servicio'] == 'Pasaporte Ordinario'
        
        # Top por trámites
        top_tramites = analytics.get_top_services(by='tramites', top_n=5)
        assert len(top_tramites) == 2
    
    def test_get_weekly_analysis(self, analytics_setup):
        """Test análisis semanal"""
        db, analytics = analytics_setup
        
        weekly_analysis = analytics.get_weekly_analysis()
        
        assert 'weekly_data' in weekly_analysis
        assert 'max_ingresos_dia' in weekly_analysis
        assert 'min_ingresos_dia' in weekly_analysis
        
        weekly_data = weekly_analysis['weekly_data']
        assert len(weekly_data) <= 7  # Máximo 7 días de la semana
        assert 'dia_semana_es' in weekly_data.columns
        assert 'ingresos_totales' in weekly_data.columns
        assert 'num_tramites' in weekly_data.columns
    
    def test_get_weekly_analysis_empty(self, analytics_setup):
        """Test análisis semanal sin datos"""
        db, analytics = analytics_setup
        
        # Filtrar fecha sin datos
        weekly_analysis = analytics.get_weekly_analysis('2025-02-01', '2025-02-01')
        
        assert 'error' in weekly_analysis
    
    def test_compare_periods(self, analytics_setup):
        """Test comparación de períodos"""
        db, analytics = analytics_setup
        
        period_configs = [
            {
                'name': 'Período 1',
                'start_date': '2025-01-01',
                'end_date': '2025-01-02',
                'grouping': 'diario'
            },
            {
                'name': 'Período 2',
                'start_date': '2025-01-03',
                'end_date': '2025-01-04',
                'grouping': 'diario'
            }
        ]
        
        comparison = analytics.compare_periods(period_configs)
        
        assert 'Período 1' in comparison
        assert 'Período 2' in comparison
        
        # Verificar estructura
        periodo1 = comparison['Período 1']
        assert 'kpis' in periodo1
        assert 'temporal_data' in periodo1
        assert 'config' in periodo1
    
    def test_predict_next_period(self, analytics_setup):
        """Test predicción básica"""
        db, analytics = analytics_setup
        
        prediction = analytics.predict_next_period(periods=2)
        
        assert 'historical_data' in prediction
        assert 'predictions' in prediction
        assert 'trends' in prediction
        
        predictions = prediction['predictions']
        assert 'ingresos' in predictions
        assert 'tramites' in predictions
        assert len(predictions['ingresos']) == 2
        assert len(predictions['tramites']) == 2
        
        trends = prediction['trends']
        assert 'ingresos_slope' in trends
        assert 'tramites_slope' in trends
    
    def test_predict_next_period_insufficient_data(self, analytics_setup):
        """Test predicción con datos insuficientes"""
        db, analytics = analytics_setup
        
        # Usar servicio con pocos datos
        prediction = analytics.predict_next_period(service='Servicio Inexistente')
        
        assert 'error' in prediction
    
    def test_get_service_grouping_analysis(self, analytics_setup):
        """Test análisis de agrupación de servicios"""
        db, analytics = analytics_setup
        
        analysis = analytics.get_service_grouping_analysis()
        
        # Debe encontrar RCM en los datos
        if 'RCM' in analysis:
            rcm_analysis = analysis['RCM']
            assert 'servicios_unicos' in rcm_analysis
            assert 'registros_totales' in rcm_analysis
            assert 'ingresos_totales' in rcm_analysis
            assert 'tramites_totales' in rcm_analysis
            assert rcm_analysis['servicios_unicos'] == 1  # Solo 'RCM Expedición'
            assert rcm_analysis['registros_totales'] == 5
    
    def test_empty_kpis(self, analytics_setup):
        """Test KPIs con datos vacíos"""
        db, analytics = analytics_setup
        
        # Filtrar fechas sin datos
        kpis = analytics.get_kpis('2025-02-01', '2025-02-01')
        
        assert kpis['total_ingresos'] == 0.0
        assert kpis['total_tramites'] == 0
        assert kpis['dias_con_datos'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])