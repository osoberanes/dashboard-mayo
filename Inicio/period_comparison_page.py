import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from enhanced_data_processor import EnhancedDataProcessor
from datetime import date, datetime
import numpy as np
import plotly.io as pio
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import tempfile
import os
import calendar

def show_period_comparison_page():
    """Página para comparar mismos períodos de diferentes años"""
    st.markdown("<h1 style='text-align: center;'>Comparación de Períodos</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center;'>
    <h3>Análisis Comparativo por Años</h3>
    <p>Compara el <strong>mismo período</strong> de <strong>diferentes años</strong> para análisis estacional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar procesador
    processor = initialize_processor()
    
    if processor is None:
        st.error("No se pudieron cargar los datos. Verifique que existan datos en la base de datos.")
        return
    
    # Obtener años y períodos disponibles
    available_data = get_available_years_and_periods(processor)
    
    if not available_data:
        st.error("No se pudo obtener información de años y períodos disponibles")
        return
    
    # Configuración de comparación
    st.markdown("<h3 style='text-align: center;'>Configuración de Comparación</h3>", unsafe_allow_html=True)
    
    # Interfaz para seleccionar período y años
    comparison_config = configure_year_comparison(available_data)
    
    # Botón para ejecutar comparación
    if st.button("🔄 Ejecutar Comparación", type="primary"):
        if validate_year_comparison(comparison_config):
            with st.spinner("Procesando comparación..."):
                # Guardar datos en session_state para mantener persistencia
                st.session_state.year_comparison_data = execute_year_comparison(processor, comparison_config)
                st.session_state.comparison_config = comparison_config
        else:
            st.error("Por favor seleccione al menos 2 años para comparar")
    
    # Mostrar resultados si existen en session_state
    if 'year_comparison_data' in st.session_state and st.session_state.year_comparison_data:
        show_year_comparison_results(
            st.session_state.year_comparison_data, 
            st.session_state.comparison_config,
            processor
        )

@st.cache_data
def initialize_processor():
    """Inicializa el procesador de datos"""
    try:
        processor = EnhancedDataProcessor()
        if processor.initialize_from_database():
            return processor
        return None
    except Exception as e:
        st.error(f"Error inicializando procesador: {str(e)}")
        return None

def get_available_years_and_periods(processor):
    """Obtiene años y períodos disponibles en los datos"""
    try:
        if processor.df is not None and not processor.df.empty:
            df = processor.df.copy()
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
            
            # Obtener años disponibles (convertir a int para compatibilidad con Streamlit)
            years = sorted([int(year) for year in df['fecha_emision'].dt.year.unique()])
            
            # Obtener meses disponibles por año
            months_by_year = {}
            for year in years:
                year_data = df[df['fecha_emision'].dt.year == year]
                months = sorted(year_data['fecha_emision'].dt.month.unique())
                months_by_year[year] = months
            
            # Definir períodos disponibles
            periods = {
                'Año Completo': list(range(1, 13)),  # Todos los meses del año
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
                'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12,
                'Q1 (Ene-Mar)': [1, 2, 3], 'Q2 (Abr-Jun)': [4, 5, 6], 
                'Q3 (Jul-Sep)': [7, 8, 9], 'Q4 (Oct-Dic)': [10, 11, 12]
            }
            
            return {
                'years': years,
                'months_by_year': months_by_year,
                'periods': periods,
                'min_date': df['fecha_emision'].min().date(),
                'max_date': df['fecha_emision'].max().date()
            }
        return None
    except Exception as e:
        st.error(f"Error obteniendo años y períodos: {str(e)}")
        return None

def configure_year_comparison(available_data):
    """Configura la comparación por años del mismo período"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📅 Seleccionar Período")
        
        # Dropdown para seleccionar período
        period_options = list(available_data['periods'].keys())
        selected_period = st.selectbox(
            "Período a comparar:",
            options=period_options,
            key="selected_period"
        )
        
        # Mostrar información del período seleccionado
        period_value = available_data['periods'][selected_period]
        if isinstance(period_value, list):
            period_info = f"Meses: {', '.join([calendar.month_name[m] for m in period_value])}"
        else:
            period_info = f"Mes: {calendar.month_name[period_value]}"
        
        st.info(f"📊 {period_info}")
    
    with col2:
        st.markdown("#### 🗓️ Seleccionar Años")
        
        # Multiselect para años
        available_years = available_data['years']
        selected_years = st.multiselect(
            "Años a comparar:",
            options=available_years,
            default=available_years[:2] if len(available_years) >= 2 else available_years,
            key="selected_years"
        )
        
        st.info(f"📈 Se compararán {len(selected_years)} años")
    
    return {
        'period_name': selected_period,
        'period_value': period_value,
        'selected_years': selected_years,
        'available_data': available_data
    }

def get_year_color(year_idx):
    """Obtiene color para cada año"""
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    return colors[year_idx % len(colors)]

def validate_year_comparison(comparison_config):
    """Valida que al menos 2 años estén seleccionados"""
    return len(comparison_config['selected_years']) >= 2

def execute_year_comparison(processor, comparison_config):
    """Ejecuta la comparación entre años del mismo período"""
    
    year_data = {}
    period_value = comparison_config['period_value']
    
    for year in comparison_config['selected_years']:
        # Obtener datos para este año y período específico
        year_period_data = get_year_period_data(processor, year, period_value)
        if year_period_data:
            year_data[year] = year_period_data
    
    if len(year_data) < 2:
        st.error("No se pudieron obtener datos suficientes para comparar")
        return None
    
    return year_data

def get_year_period_data(processor, year, period_value):
    """Obtiene datos para un año y período específicos"""
    try:
        if processor.df is None or processor.df.empty:
            return None
        
        df = processor.df.copy()
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        
        # Filtrar por año
        year_data = df[df['fecha_emision'].dt.year == year]
        
        if year_data.empty:
            return None
        
        # Filtrar por período (mes o trimestre)
        if isinstance(period_value, list):
            # Es un trimestre
            period_data = year_data[year_data['fecha_emision'].dt.month.isin(period_value)]
        else:
            # Es un mes específico
            period_data = year_data[year_data['fecha_emision'].dt.month == period_value]
        
        if period_data.empty:
            return None
        
        # Calcular estadísticas básicas
        stats = {
            'total_ingresos': period_data['ingresos_totales'].sum(),
            'total_tramites': period_data['num_tramites'].sum(),
            'ingreso_diario_promedio': period_data.groupby(period_data['fecha_emision'].dt.date)['ingresos_totales'].sum().mean(),
            'tramite_diario_promedio': period_data.groupby(period_data['fecha_emision'].dt.date)['num_tramites'].sum().mean(),
            'num_dias': period_data['fecha_emision'].dt.date.nunique(),
            'num_servicios': period_data['servicio'].nunique()
        }
        
        return {
            'data': period_data,
            'stats': stats,
            'year': year,
            'period_value': period_value
        }
        
    except Exception as e:
        st.error(f"Error obteniendo datos del año {year}: {str(e)}")
        return None

def show_year_comparison_results(year_data, comparison_config, processor):
    """Muestra los resultados de la comparación por años"""
    
    st.markdown("<h2 style='text-align: center;'>📊 Resultados de la Comparación</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Información del período
    period_name = comparison_config['period_name']
    years_compared = list(year_data.keys())
    
    st.info(f"📅 **Período analizado:** {period_name} | 🗓️ **Años comparados:** {', '.join(map(str, years_compared))}")
    
    # KPIs comparativos
    show_year_comparative_kpis(year_data)
    
    st.markdown("---")
    
    # Controles y gráfica principal
    show_year_timeline_chart(year_data, comparison_config)
    
    st.markdown("---")
    
    # Botón de exportación PDF
    show_pdf_export_button(year_data, comparison_config)

def show_year_comparative_kpis(year_data):
    """Muestra KPIs comparativos por año"""
    st.markdown("<h3 style='text-align: center;'>📈 KPIs Comparativos por Año</h3>", unsafe_allow_html=True)
    
    # Preparar datos para métricas
    kpi_data = []
    years_list = sorted(year_data.keys())
    
    for year in years_list:
        stats = year_data[year]['stats']
        kpi_data.append({
            'año': year,
            'ingresos_totales': stats['total_ingresos'],
            'tramites_totales': stats['total_tramites'],
            'ingreso_diario_promedio': stats['ingreso_diario_promedio'],
            'tramite_diario_promedio': stats['tramite_diario_promedio']
        })
    
    df_kpis = pd.DataFrame(kpi_data)
    
    # Calcular variaciones respecto al primer año
    base_year = years_list[0]
    base_ingresos = df_kpis[df_kpis['año'] == base_year]['ingresos_totales'].iloc[0]
    base_tramites = df_kpis[df_kpis['año'] == base_year]['tramites_totales'].iloc[0]
    
    # Mostrar métricas en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<h4 style='text-align: center;'>💰 Ingresos Totales</h4>", unsafe_allow_html=True)
        for _, row in df_kpis.iterrows():
            if row['año'] == base_year:
                delta = None
            else:
                delta = f"${(row['ingresos_totales'] - base_ingresos):,.2f}"
            
            st.metric(
                f"{row['año']}",
                f"${row['ingresos_totales']:,.2f}",
                delta=delta
            )
    
    with col2:
        st.markdown("<h4 style='text-align: center;'>📄 Trámites Totales</h4>", unsafe_allow_html=True)
        for _, row in df_kpis.iterrows():
            if row['año'] == base_year:
                delta = None
            else:
                delta = f"{(row['tramites_totales'] - base_tramites):,}"
            
            st.metric(
                f"{row['año']}",
                f"{row['tramites_totales']:,}",
                delta=delta
            )
    
    with col3:
        st.markdown("<h4 style='text-align: center;'>📊 Ingreso/Día Promedio</h4>", unsafe_allow_html=True)
        for _, row in df_kpis.iterrows():
            st.metric(
                f"{row['año']}",
                f"${row['ingreso_diario_promedio']:,.2f}"
            )
    
    with col4:
        st.markdown("<h4 style='text-align: center;'>📋 Trámites/Día Promedio</h4>", unsafe_allow_html=True)
        for _, row in df_kpis.iterrows():
            st.metric(
                f"{row['año']}",
                f"{row['tramite_diario_promedio']:,.1f}"
            )

def show_year_timeline_chart(year_data, comparison_config):
    """Muestra gráfica consolidada con líneas por año"""
    st.markdown("<h3 style='text-align: center;'>📈 Comportamiento Temporal por Año</h3>", unsafe_allow_html=True)
    
    # Controles para las gráficas
    control_col1, control_col2 = st.columns(2)
    
    with control_col1:
        # Obtener servicios disponibles para el dropdown expandido
        all_services = set()
        for year_info in year_data.values():
            all_services.update(year_info['data']['servicio'].unique())
        
        metric_options = {
            'ingresos_totales': '💰 Ingresos Totales',
            'num_tramites': '📄 Número de Trámites Totales'
        }
        
        # Agregar servicios individuales al dropdown
        for service in sorted(all_services):
            metric_options[f'servicio_{service}'] = f'🔧 {service}'
        
        selected_metric = st.selectbox(
            "Elemento a revisar:",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key="year_timeline_metric"
        )
    
    with control_col2:
        grouping_options = {
            'dia': '📅 Diario',
            'semana': '📆 Semanal',
            'mes': '🗓️ Mensual'
        }
        
        selected_grouping = st.selectbox(
            "Agrupación temporal:",
            options=list(grouping_options.keys()),
            format_func=lambda x: grouping_options[x],
            key="year_timeline_grouping"
        )
    
    # Crear gráfica consolidada con líneas por año
    st.markdown("---")
    
    metric_label = metric_options[selected_metric]
    st.markdown(f"#### {metric_label} - Comparación por Años")
    
    # Guardar configuración de gráfica para exportación PDF
    if 'chart_config' not in st.session_state:
        st.session_state.chart_config = {}
    
    fig = create_year_comparison_chart(year_data, selected_metric, selected_grouping, metric_label, comparison_config)
    
    if fig:
        st.session_state.chart_config = {
            'figure': fig,
            'metric': selected_metric,
            'grouping': selected_grouping,
            'metric_label': metric_label
        }
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No se pudieron generar datos para la gráfica con la configuración seleccionada.")

def create_year_comparison_chart(year_data, metric, grouping, metric_label, comparison_config):
    """Crea una gráfica consolidada con líneas por año del mismo período"""
    
    fig = go.Figure()
    years_list = sorted(year_data.keys())
    
    for i, year in enumerate(years_list):
        year_info = year_data[year]
        df = year_info['data'].copy()
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        
        # Filtrar por servicio específico si se seleccionó
        if metric.startswith('servicio_'):
            service_name = metric.replace('servicio_', '')
            df = df[df['servicio'] == service_name]
            if df.empty:
                continue
        
        # Aplicar agrupación temporal
        if grouping == 'dia':
            df['periodo'] = df['fecha_emision'].dt.day
            df['periodo_label'] = df['fecha_emision'].dt.strftime('%d')
            x_title = 'Día del Período'
        elif grouping == 'semana':
            df['periodo'] = df['fecha_emision'].dt.isocalendar().week
            df['periodo_label'] = 'S' + df['fecha_emision'].dt.isocalendar().week.astype(str)
            x_title = 'Semana del Año'
        elif grouping == 'mes':
            df['periodo'] = df['fecha_emision'].dt.month
            df['periodo_label'] = df['fecha_emision'].dt.strftime('%b')
            x_title = 'Mes'
        else:
            continue
        
        # Agrupar datos según la métrica seleccionada
        if metric == 'ingresos_totales':
            grouped_data = df.groupby(['periodo', 'periodo_label'])['ingresos_totales'].sum().reset_index()
            y_column = 'ingresos_totales'
        elif metric == 'num_tramites':
            grouped_data = df.groupby(['periodo', 'periodo_label'])['num_tramites'].sum().reset_index()
            y_column = 'num_tramites'
        elif metric.startswith('servicio_'):
            # Para servicios específicos, usar ingresos totales
            grouped_data = df.groupby(['periodo', 'periodo_label'])['ingresos_totales'].sum().reset_index()
            y_column = 'ingresos_totales'
        else:
            continue
        
        if not grouped_data.empty:
            # Agregar línea para este año
            color = get_year_color(i)
            fig.add_trace(go.Scatter(
                x=grouped_data['periodo_label'],
                y=grouped_data[y_column],
                mode='lines+markers',
                name=f'{year}',
                line=dict(
                    color=color, 
                    width=3
                ),
                marker=dict(
                    size=8,
                    color=color
                ),
                hovertemplate=f'<b>{year}</b><br>' +
                             f'{x_title}: %{{x}}<br>' +
                             f'{metric_label}: %{{y:,.2f}}<extra></extra>'
            ))
    
    if fig.data:
        # Configurar layout de la gráfica
        period_name = comparison_config['period_name']
        fig.update_layout(
            title=f'{metric_label} - {period_name} por Año',
            xaxis_title=x_title,
            yaxis_title=metric_label,
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                title="Año"
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=True
        )
        
        # Mejorar aspecto visual
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        
        return fig
    
    return None


def show_pdf_export_button(year_data, comparison_config):
    """Muestra botón para exportar a PDF"""
    st.markdown("<h3 style='text-align: center;'>📄 Exportar Reporte</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📄 Generar y Descargar PDF", type="primary", use_container_width=True):
            with st.spinner("Generando reporte PDF..."):
                try:
                    pdf_buffer = create_pdf_report(year_data, comparison_config)
                    
                    if pdf_buffer:
                        # Generar nombre de archivo
                        period_name = comparison_config['period_name'].replace(' ', '_').replace('/', '-')
                        years_str = '_'.join(map(str, sorted(year_data.keys())))
                        filename = f"comparacion_{period_name}_{years_str}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                        
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_buffer,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.success("✅ PDF generado exitosamente")
                    else:
                        st.error("❌ Error al generar el PDF")
                        
                except Exception as e:
                    st.error(f"❌ Error generando PDF: {str(e)}")

def create_pdf_report(year_data, comparison_config):
    """Crea el reporte PDF completo"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centro
        )
        
        # Contenido del PDF
        story = []
        
        # Título
        period_name = comparison_config['period_name']
        years_list = sorted(year_data.keys())
        years_str = ', '.join(map(str, years_list))
        
        story.append(Paragraph(f"Comparación de Períodos: {period_name}", title_style))
        story.append(Paragraph(f"Años comparados: {years_str}", styles['Normal']))
        story.append(Paragraph(f"Fecha de reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # KPIs en tabla
        story.append(Paragraph("KPIs Comparativos por Año", styles['Heading2']))
        
        kpi_data = [['Año', 'Ingresos Totales', 'Trámites Totales', 'Ingreso/Día Promedio', 'Trámites/Día Promedio']]
        
        for year in years_list:
            stats = year_data[year]['stats']
            kpi_data.append([
                str(year),
                f"${stats['total_ingresos']:,.2f}",
                f"{stats['total_tramites']:,}",
                f"${stats['ingreso_diario_promedio']:,.2f}",
                f"{stats['tramite_diario_promedio']:,.1f}"
            ])
        
        kpi_table = Table(kpi_data)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(kpi_table)
        story.append(Spacer(1, 12))
        
        # Gráfica (si existe)
        if 'chart_config' in st.session_state and st.session_state.chart_config:
            story.append(Paragraph("Gráfica Comparativa", styles['Heading2']))
            
            try:
                fig = st.session_state.chart_config['figure']
                img_bytes = pio.to_image(fig, format="png", engine="kaleido", width=600, height=400)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(img_bytes)
                    tmp.flush()
                    
                    story.append(RLImage(tmp.name, width=6*inch, height=4*inch))
                    story.append(Spacer(1, 12))
                    
                    # Limpiar archivo temporal
                    os.unlink(tmp.name)
                    
            except Exception as e:
                story.append(Paragraph(f"Error incluyendo gráfica: {str(e)}", styles['Normal']))
        
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error creando PDF: {str(e)}")
        return None