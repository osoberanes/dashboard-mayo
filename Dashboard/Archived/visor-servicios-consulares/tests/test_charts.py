"""
Tests para el módulo de gráficas
"""
import pytest
import pandas as pd
import plotly.graph_objects as go

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.charts import ChartFactory


@pytest.fixture
def chart_factory():
    """Fixture para ChartFactory"""
    return ChartFactory()


@pytest.fixture
def sample_data():
    """Fixture con datos de ejemplo para gráficas"""
    return pd.DataFrame({
        'fecha': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'ingresos_totales': [1000, 1500, 1200, 1800, 2000],
        'num_tramites': [10, 15, 12, 18, 20],
        'servicio': ['Pasaporte A', 'Pasaporte B', 'RCM A', 'RCM B', 'Apostilla'],
        'categoria': ['PASAPORTES', 'PASAPORTES', 'RCM', 'RCM', 'NOTARIALES']
    })


@pytest.fixture
def empty_data():
    """Fixture con DataFrame vacío"""
    return pd.DataFrame()


class TestChartFactory:
    """Tests para ChartFactory"""
    
    def test_create_line_chart(self, chart_factory, sample_data):
        """Test creación de gráfica de líneas"""
        fig = chart_factory.create_line_chart(
            data=sample_data,
            x_col='fecha',
            y_col='ingresos_totales',
            title='Test Line Chart'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatter'
        assert fig.data[0].mode == 'lines+markers'
        assert fig.layout.title.text == 'Test Line Chart'
    
    def test_create_line_chart_empty_data(self, chart_factory, empty_data):
        """Test gráfica de líneas con datos vacíos"""
        fig = chart_factory.create_line_chart(
            data=empty_data,
            x_col='fecha',
            y_col='ingresos_totales'
        )
        
        assert isinstance(fig, go.Figure)
        # Debe crear gráfica vacía con mensaje
        assert len(fig.layout.annotations) > 0
    
    def test_create_bar_chart_vertical(self, chart_factory, sample_data):
        """Test gráfica de barras verticales"""
        fig = chart_factory.create_bar_chart(
            data=sample_data,
            x_col='servicio',
            y_col='ingresos_totales',
            title='Test Bar Chart',
            orientation='v'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'
        assert fig.layout.title.text == 'Test Bar Chart'
    
    def test_create_bar_chart_horizontal(self, chart_factory, sample_data):
        """Test gráfica de barras horizontales"""
        fig = chart_factory.create_bar_chart(
            data=sample_data,
            x_col='servicio',
            y_col='ingresos_totales',
            title='Test Horizontal Bar Chart',
            orientation='h'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'
        assert fig.data[0].orientation == 'h'
    
    def test_create_multi_line_chart(self, chart_factory, sample_data):
        """Test gráfica con múltiples líneas"""
        # Crear series de datos
        series1 = sample_data[sample_data['categoria'] == 'PASAPORTES'].copy()
        series2 = sample_data[sample_data['categoria'] == 'RCM'].copy()
        
        data_series = [
            {
                'data': series1,
                'y_col': 'ingresos_totales',
                'name': 'Pasaportes'
            },
            {
                'data': series2,
                'y_col': 'ingresos_totales',
                'name': 'RCM'
            }
        ]
        
        fig = chart_factory.create_multi_line_chart(
            data_series=data_series,
            x_col='fecha',
            title='Test Multi Line Chart'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert fig.data[0].name == 'Pasaportes'
        assert fig.data[1].name == 'RCM'
        assert fig.layout.showlegend == True
    
    def test_create_multi_line_chart_empty_series(self, chart_factory, empty_data):
        """Test gráfica múltiple con series vacías"""
        data_series = [
            {
                'data': empty_data,
                'y_col': 'ingresos_totales',
                'name': 'Serie Vacía'
            }
        ]
        
        fig = chart_factory.create_multi_line_chart(
            data_series=data_series,
            x_col='fecha',
            title='Test Empty Multi Line'
        )
        
        assert isinstance(fig, go.Figure)
        # Debe crear gráfica vacía
        assert len(fig.layout.annotations) > 0
    
    def test_create_kpi_chart(self, chart_factory):
        """Test gráfica de KPIs"""
        kpis = {
            'total_ingresos': 10000.0,
            'total_tramites': 100,
            'promedio_diario': 500.0,
            'eficiencia': 100.0
        }
        
        fig = chart_factory.create_kpi_chart(kpis, title='Test KPIs')
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 4  # 4 indicadores
        assert fig.layout.title.text == 'Test KPIs'
        
        # Verificar que son indicadores
        for trace in fig.data:
            assert trace.type == 'indicator'
    
    def test_create_comparison_chart(self, chart_factory, sample_data):
        """Test gráfica de comparación"""
        comparison_data = {
            'Período 1': {
                'temporal_data': sample_data[['fecha', 'ingresos_totales']].rename(columns={'fecha': 'periodo_str'})
            },
            'Período 2': {
                'temporal_data': sample_data[['fecha', 'ingresos_totales']].rename(columns={'fecha': 'periodo_str'})
            }
        }
        
        fig = chart_factory.create_comparison_chart(
            comparison_data=comparison_data,
            metric='ingresos_totales',
            grouping='diario'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert fig.data[0].name == 'Período 1'
        assert fig.data[1].name == 'Período 2'
        assert 'Comparación de Ingresos' in fig.layout.title.text
    
    def test_create_comparison_chart_empty(self, chart_factory):
        """Test gráfica de comparación sin datos"""
        comparison_data = {}
        
        fig = chart_factory.create_comparison_chart(
            comparison_data=comparison_data,
            metric='ingresos_totales'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0  # Mensaje de "sin datos"
    
    def test_create_service_distribution_pie(self, chart_factory, sample_data):
        """Test gráfica de distribución de servicios (pie)"""
        fig = chart_factory.create_service_distribution_chart(
            data=sample_data,
            chart_type='pie'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'pie'
    
    def test_create_service_distribution_treemap(self, chart_factory, sample_data):
        """Test gráfica de distribución de servicios (treemap)"""
        fig = chart_factory.create_service_distribution_chart(
            data=sample_data,
            chart_type='treemap'
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'treemap'
    
    def test_create_weekly_heatmap(self, chart_factory):
        """Test heatmap semanal"""
        weekly_data = pd.DataFrame({
            'dia_semana_es': ['Lunes', 'Martes', 'Miércoles'],
            'ingresos_totales': [1000, 1500, 1200],
            'num_tramites': [10, 15, 12]
        })
        
        fig = chart_factory.create_weekly_heatmap(weekly_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'heatmap'
    
    def test_create_weekly_heatmap_empty(self, chart_factory, empty_data):
        """Test heatmap semanal con datos vacíos"""
        fig = chart_factory.create_weekly_heatmap(empty_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0  # Mensaje de error
    
    def test_apply_responsive_layout_mobile(self, chart_factory, sample_data):
        """Test layout responsivo para móviles"""
        fig = chart_factory.create_line_chart(
            data=sample_data,
            x_col='fecha',
            y_col='ingresos_totales'
        )
        
        responsive_fig = chart_factory.apply_responsive_layout(fig, mobile=True)
        
        assert responsive_fig.layout.height == 300
        assert responsive_fig.layout.font.size == 10
    
    def test_apply_responsive_layout_desktop(self, chart_factory, sample_data):
        """Test layout responsivo para escritorio"""
        fig = chart_factory.create_line_chart(
            data=sample_data,
            x_col='fecha',
            y_col='ingresos_totales'
        )
        
        responsive_fig = chart_factory.apply_responsive_layout(fig, mobile=False)
        
        assert responsive_fig.layout.height == chart_factory.base_layout['height']
    
    def test_empty_chart_creation(self, chart_factory):
        """Test creación de gráfica vacía"""
        fig = chart_factory._create_empty_chart("Mensaje de prueba")
        
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) == 1
        assert fig.layout.annotations[0].text == "Mensaje de prueba"
        assert fig.layout.xaxis.visible == False
        assert fig.layout.yaxis.visible == False
    
    def test_chart_colors_consistency(self, chart_factory):
        """Test consistencia de colores"""
        colors = chart_factory.colors
        
        assert 'primary' in colors
        assert 'secondary' in colors
        assert 'success' in colors
        assert 'danger' in colors
        
        # Verificar formato de colores hex
        for color in colors.values():
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB
    
    def test_base_layout_properties(self, chart_factory):
        """Test propiedades del layout base"""
        base_layout = chart_factory.base_layout
        
        assert 'font' in base_layout
        assert 'title' in base_layout
        assert 'plot_bgcolor' in base_layout
        assert 'paper_bgcolor' in base_layout
        assert 'height' in base_layout
        
        assert base_layout['plot_bgcolor'] == 'white'
        assert base_layout['paper_bgcolor'] == 'white'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])