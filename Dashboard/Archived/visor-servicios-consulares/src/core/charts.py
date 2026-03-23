"""
Factory de gráficas reutilizables optimizadas
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import logging

from ..config.settings import settings
from ..config.constants import CHART_LAYOUTS, NUMBER_FORMATS


class ChartFactory:
    """Factory para crear gráficas estandarizadas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.colors = settings.charts.default_colors
        self.base_layout = settings.get_chart_style()
    
    def create_line_chart(self, data: pd.DataFrame, 
                         x_col: str, y_col: str,
                         title: str = "",
                         color: Optional[str] = None,
                         show_markers: bool = True,
                         **kwargs) -> go.Figure:
        """Crea gráfica de líneas estándar"""
        
        if data.empty:
            return self._create_empty_chart("No hay datos disponibles")
        
        color = color or self.colors['primary']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers' if show_markers else 'lines',
            line=dict(
                color=color, 
                width=settings.charts.line_width
            ),
            marker=dict(
                size=settings.charts.marker_size,
                color=color
            ),
            name=title,
            hovertemplate=f'<b>%{{x}}</b><br>{y_col}: %{{y:,.2f}}<extra></extra>'
        ))
        
        # Aplicar layout base y personalizaciones
        layout_updates = {
            'title': title,
            'xaxis_title': x_col.replace('_', ' ').title(),
            'yaxis_title': y_col.replace('_', ' ').title(),
            **self.base_layout,
            **CHART_LAYOUTS['line'],
            **kwargs
        }
        
        fig.update_layout(**layout_updates)
        
        return fig
    
    def create_bar_chart(self, data: pd.DataFrame,
                        x_col: str, y_col: str,
                        title: str = "",
                        orientation: str = 'v',
                        color_col: Optional[str] = None,
                        **kwargs) -> go.Figure:
        """Crea gráfica de barras estándar"""
        
        if data.empty:
            return self._create_empty_chart("No hay datos disponibles")
        
        if orientation == 'h':
            # Barras horizontales
            fig = px.bar(
                data, 
                x=y_col, 
                y=x_col,
                orientation='h',
                title=title,
                color=color_col or y_col,
                color_continuous_scale='viridis'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        else:
            # Barras verticales
            fig = px.bar(
                data,
                x=x_col,
                y=y_col, 
                title=title,
                color=color_col or y_col,
                color_continuous_scale='viridis'
            )
        
        # Aplicar layout base
        layout_updates = {
            **self.base_layout,
            **CHART_LAYOUTS['bar'],
            **kwargs
        }
        
        fig.update_layout(**layout_updates)
        
        return fig
    
    def create_multi_line_chart(self, data_series: List[Dict[str, Any]],
                               x_col: str,
                               title: str = "",
                               **kwargs) -> go.Figure:
        """Crea gráfica con múltiples líneas"""
        
        fig = go.Figure()
        colors = settings.get_color_palette(len(data_series))
        
        for i, series in enumerate(data_series):
            data = series['data']
            y_col = series['y_col']
            name = series.get('name', f'Serie {i+1}')
            color = series.get('color', colors[i % len(colors)])
            
            if not data.empty:
                fig.add_trace(go.Scatter(
                    x=data[x_col],
                    y=data[y_col],
                    mode='lines+markers',
                    line=dict(color=color, width=settings.charts.line_width),
                    marker=dict(size=settings.charts.marker_size),
                    name=name,
                    hovertemplate=f'<b>{name}</b><br>%{{x}}<br>%{{y:,.2f}}<extra></extra>'
                ))
        
        if not fig.data:
            return self._create_empty_chart("No hay datos disponibles")
        
        layout_updates = {
            'title': title,
            'xaxis_title': x_col.replace('_', ' ').title(),
            **self.base_layout,
            **CHART_LAYOUTS['line'],
            'showlegend': True,
            **kwargs
        }
        
        fig.update_layout(**layout_updates)
        
        return fig
    
    def create_kpi_chart(self, kpis: Dict[str, float],
                        title: str = "Indicadores Principales") -> go.Figure:
        """Crea gráfica de KPIs como tarjetas"""
        
        # Convertir KPIs a formato para subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=list(kpis.keys())[:4],
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        kpi_items = list(kpis.items())[:4]  # Tomar primeros 4 KPIs
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for i, (key, value) in enumerate(kpi_items):
            if i < len(positions):
                row, col = positions[i]
                
                # Formatear valor según el tipo
                if 'ingreso' in key.lower() or 'costo' in key.lower():
                    formatted_value = NUMBER_FORMATS['currency'].format(value)
                elif 'tramite' in key.lower() and 'promedio' not in key.lower():
                    formatted_value = NUMBER_FORMATS['integer'].format(int(value))
                else:
                    formatted_value = NUMBER_FORMATS['decimal'].format(value)
                
                fig.add_trace(
                    go.Indicator(
                        mode="number",
                        value=value,
                        number={'valueformat': '.2f' if isinstance(value, float) else 'd'},
                        title={"text": key.replace('_', ' ').title()},
                        domain={'row': row-1, 'column': col-1}
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            title=title,
            height=400,
            **self.base_layout
        )
        
        return fig
    
    def create_comparison_chart(self, comparison_data: Dict[str, Any],
                              metric: str = 'ingresos_totales',
                              grouping: str = 'mensual') -> go.Figure:
        """Crea gráfica de comparación entre períodos"""
        
        fig = go.Figure()
        colors = settings.get_color_palette()
        
        for i, (period_name, period_data) in enumerate(comparison_data.items()):
            temporal_data = period_data.get('temporal_data', pd.DataFrame())
            
            if not temporal_data.empty and metric in temporal_data.columns:
                color = colors[i % len(colors)]
                
                fig.add_trace(go.Scatter(
                    x=temporal_data['periodo_str'],
                    y=temporal_data[metric],
                    mode='lines+markers',
                    line=dict(color=color, width=settings.charts.line_width),
                    marker=dict(size=settings.charts.marker_size),
                    name=period_name,
                    hovertemplate=f'<b>{period_name}</b><br>%{{x}}<br>%{{y:,.2f}}<extra></extra>'
                ))
        
        if not fig.data:
            return self._create_empty_chart("No hay datos para comparar")
        
        # Título dinámico basado en la métrica
        metric_labels = {
            'ingresos_totales': 'Ingresos',
            'num_tramites': 'Número de Trámites',
            'ingreso_por_tramite': 'Ingreso por Trámite'
        }
        
        metric_label = metric_labels.get(metric, metric.replace('_', ' ').title())
        title = f'Comparación de {metric_label} - Vista {grouping.title()}'
        
        fig.update_layout(
            title=title,
            xaxis_title=f'Período ({grouping})',
            yaxis_title=metric_label,
            **self.base_layout,
            **CHART_LAYOUTS['line'],
            showlegend=True
        )
        
        return fig
    
    def create_service_distribution_chart(self, data: pd.DataFrame,
                                        chart_type: str = 'pie') -> go.Figure:
        """Crea gráfica de distribución de servicios"""
        
        if data.empty:
            return self._create_empty_chart("No hay datos de servicios")
        
        # Obtener top servicios para evitar gráficas sobrecargadas
        top_data = data.nlargest(10, 'ingresos_totales') if len(data) > 10 else data
        
        if chart_type == 'pie':
            fig = px.pie(
                top_data,
                values='ingresos_totales',
                names='servicio',
                title='Distribución de Ingresos por Servicio (Top 10)'
            )
        else:
            # Treemap como alternativa
            fig = px.treemap(
                top_data,
                values='ingresos_totales',
                path=['servicio'],
                title='Distribución de Ingresos por Servicio (Top 10)'
            )
        
        fig.update_layout(**self.base_layout)
        
        return fig
    
    def create_weekly_heatmap(self, weekly_data: pd.DataFrame) -> go.Figure:
        """Crea heatmap de actividad semanal"""
        
        if weekly_data.empty:
            return self._create_empty_chart("No hay datos semanales")
        
        # Preparar datos para heatmap
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        # Asegurar que tenemos todos los días
        for day in days:
            if day not in weekly_data['dia_semana_es'].values:
                new_row = pd.DataFrame({
                    'dia_semana_es': [day],
                    'ingresos_totales': [0],
                    'num_tramites': [0]
                })
                weekly_data = pd.concat([weekly_data, new_row], ignore_index=True)
        
        # Ordenar por días de la semana
        weekly_data['dia_orden'] = weekly_data['dia_semana_es'].map(
            {day: i for i, day in enumerate(days)}
        )
        weekly_data = weekly_data.sort_values('dia_orden')
        
        fig = go.Figure(data=go.Heatmap(
            z=[weekly_data['ingresos_totales'].values],
            x=weekly_data['dia_semana_es'],
            y=['Ingresos Promedio'],
            colorscale='viridis',
            showscale=True,
            hovertemplate='<b>%{x}</b><br>Ingresos: $%{z:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Actividad por Día de la Semana',
            xaxis_title='Día de la Semana',
            **self.base_layout,
            height=200
        )
        
        return fig
    
    def _create_empty_chart(self, message: str = "No hay datos") -> go.Figure:
        """Crea gráfica vacía con mensaje"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            **self.base_layout,
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        
        return fig
    
    def apply_responsive_layout(self, fig: go.Figure, 
                              mobile: bool = False) -> go.Figure:
        """Aplica layout responsivo a la gráfica"""
        
        if mobile:
            # Configuración para móviles
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                font=dict(size=10),
                title=dict(font=dict(size=12))
            )
        else:
            # Configuración para escritorio
            fig.update_layout(
                height=settings.ui.chart_height,
                margin=dict(l=50, r=50, t=50, b=50)
            )
        
        return fig