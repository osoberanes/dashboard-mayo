import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from enhanced_data_processor import EnhancedDataProcessor
from file_upload_page import show_file_upload_page
from service_grouping_page import show_service_grouping_page
from period_comparison_page import show_period_comparison_page
from database_manager import DatabaseManager
from datetime import datetime, date
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Consular - Análisis Histórico",
    page_icon="📊",
    layout="wide"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.success-card {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal del dashboard"""
    
    # Barra lateral para navegación
    st.sidebar.title("Dashboard Consular")
    st.sidebar.markdown("---")
    
    # Navegación con botones individuales
    if st.sidebar.button("📊 Análisis de datos", use_container_width=True):
        st.session_state.current_page = "Análisis de Datos"
    
    if st.sidebar.button("📈 Comparación de períodos", use_container_width=True):
        st.session_state.current_page = "Comparación de Períodos"
    
    if st.sidebar.button("🔧 Agrupación de servicios", use_container_width=True):
        st.session_state.current_page = "Agrupación de Servicios"
        
    if st.sidebar.button("📁 Carga de archivos", use_container_width=True):
        st.session_state.current_page = "Gestión de Archivos"
        
    if st.sidebar.button("⚙️ Configuración", use_container_width=True):
        st.session_state.current_page = "Configuración"
    
    # Inicializar página por defecto
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Análisis de Datos"
    
    page = st.session_state.current_page
    
    if page == "Análisis de Datos":
        show_analytics_page()
    elif page == "Gestión de Archivos":
        show_file_upload_page()
    elif page == "Agrupación de Servicios":
        show_service_grouping_page()
    elif page == "Comparación de Períodos":
        show_period_comparison_page()
    else:
        show_settings_page()

def show_analytics_page():
    """Página principal de análisis de datos - Nueva estructura"""
    
    # 1. TÍTULO CENTRADO Y BOTÓN ACTUALIZAR
    col_title, col_button = st.columns([4, 1])
    with col_title:
        st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Dashboard de Análisis Consular</h1>", unsafe_allow_html=True)
    with col_button:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Inicializar procesador
    processor = initialize_enhanced_processor()
    if processor is None:
        show_empty_state()
        return
    
    # 2. FILTROS DE ANÁLISIS (INICIO - FIN)
    st.markdown("#### Filtros de análisis")
    col_inicio, col_fin = st.columns(2)
    
    # Obtener rango de fechas disponible
    try:
        db_manager = DatabaseManager()
        date_range = db_manager.get_date_range()
        min_date = pd.to_datetime(date_range['fecha_min']).date()
        max_date = pd.to_datetime(date_range['fecha_max']).date()
    except:
        min_date = max_date = date.today()
    
    with col_inicio:
        fecha_inicio = st.date_input("Fecha Inicio:", value=min_date, key="fecha_inicio_new")
    with col_fin:
        fecha_fin = st.date_input("Fecha Fin:", value=max_date, key="fecha_fin_new")
    
    # Aplicar filtros al procesador
    processor.initialize_from_database(
        fecha_inicio.strftime('%Y-%m-%d'), 
        fecha_fin.strftime('%Y-%m-%d')
    )
    
    if processor.df is None or processor.df.empty:
        st.warning("⚠️ No hay datos para el período seleccionado")
        return
    
    st.markdown("---")
    
    # 3. KPIS DE INGRESOS
    show_main_kpis(processor)
    
    st.markdown("---")
    
    # 4. GRÁFICA DE LÍNEAS DE INGRESOS (ANCHO COMPLETO)
    st.markdown("#### Evolución de Ingresos")
    
    # Control de agrupación temporal para gráfica de ingresos
    income_col1, income_col2 = st.columns([3, 1])
    with income_col2:
        income_grouping = st.selectbox(
            "Agrupación:",
            ["Diaria", "Mensual", "Anual"],
            key="income_grouping",
            help="Seleccione el nivel de agrupación temporal"
        )
    
    with income_col1:
        create_income_line_chart(processor, income_grouping)
    
    st.markdown("---")
    
    # 5. GRÁFICAS DE PASAPORTES Y MATRÍCULAS (50% CADA UNA)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### Número de Pasaportes")
        # Control de agrupación temporal para pasaportes
        passport_grouping = st.selectbox(
            "Agrupación:",
            ["Diaria", "Mensual", "Anual"],
            key="passport_grouping",
            help="Seleccione el nivel de agrupación temporal"
        )
        create_passport_chart(processor, passport_grouping)
    
    with chart_col2:
        st.markdown("#### Número de Matrículas")
        # Control de agrupación temporal para matrículas
        matricula_grouping = st.selectbox(
            "Agrupación:",
            ["Diaria", "Mensual", "Anual"],
            key="matricula_grouping",
            help="Seleccione el nivel de agrupación temporal"
        )
        create_matriculas_chart(processor, matricula_grouping)
    
    st.markdown("---")
    
    # 6. ANÁLISIS DE SERVICIO ESPECÍFICO
    st.markdown("#### Análisis de Servicio Específico")
    show_specific_service_analysis(processor)
    
    st.markdown("---")
    
    # 7. TOP SERVICIOS POR PRODUCCIÓN (BARRAS HORIZONTALES)
    st.markdown("#### Top Servicios por Producción")
    create_top_services_horizontal_chart(processor)
    
    st.markdown("---")
    
    # 7.1 ANÁLISIS POR DÍA DE LA SEMANA (DESPUÉS DE TOP SERVICIOS)
    st.markdown("#### 📅 Análisis por Día de la Semana")
    show_weekly_analysis_main(processor)
    
    st.markdown("---")
    
    # 8. BOTÓN EXPORTAR PDF
    if st.button("📄 Exportar Dashboard a PDF", use_container_width=True):
        st.info("Funcionalidad de exportación PDF en desarrollo")
    
    st.markdown("---")
    
    # 9. DATOS DETALLADOS
    st.markdown("#### Datos Detallados")
    show_detailed_data_section(processor)

def show_main_kpis(processor):
    """Muestra KPIs principales: ingresos totales, trámites, promedio diario, desviación estándar diaria"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            df = processor.df.copy()
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
            
            # Calcular ingresos diarios agrupados
            ingresos_diarios = df.groupby(df['fecha_emision'].dt.date)['ingresos_totales'].sum()
            
            # Métricas principales
            total_ingresos = df['ingresos_totales'].sum()
            total_tramites = df['num_tramites'].sum()
            promedio_diario = ingresos_diarios.mean()
            desv_std_diaria = ingresos_diarios.std()
            
            # Mostrar KPIs en 4 columnas
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            
            with kpi_col1:
                st.metric(
                    "Ingresos Totales",
                    f"${total_ingresos:,.2f}",
                    help="Suma total de ingresos en el período"
                )
            
            with kpi_col2:
                st.metric(
                    "Trámites",
                    f"{total_tramites:,}",
                    help="Número total de trámites procesados"
                )
            
            with kpi_col3:
                st.metric(
                    "Promedio Diario",
                    f"${promedio_diario:.2f}",
                    help="Promedio de ingresos por día"
                )
            
            with kpi_col4:
                st.metric(
                    "Desv. Std. Diaria",
                    f"${desv_std_diaria:.2f}",
                    help="Desviación estándar de ingresos diarios"
                )
        else:
            st.warning("No hay datos disponibles para calcular KPIs")
                
    except Exception as e:
        st.error(f"Error calculando KPIs: {str(e)}")

def create_income_line_chart(processor, grouping="Diaria"):
    """Crea gráfica de líneas de ingresos con agrupación temporal configurable"""
    try:
        # Obtener datos directamente del DataFrame
        if hasattr(processor, 'df') and processor.df is not None:
            df = processor.df.copy()
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
            
            # Agrupar según la selección temporal
            if grouping == "Diaria":
                df['periodo'] = df['fecha_emision'].dt.date
                title_suffix = "Diaria"
                x_label = "Fecha"
            elif grouping == "Mensual":
                df['periodo'] = df['fecha_emision'].dt.to_period('M').astype(str)
                title_suffix = "Mensual"
                x_label = "Mes"
            elif grouping == "Anual":
                df['periodo'] = df['fecha_emision'].dt.year
                title_suffix = "Anual"
                x_label = "Año"
            
            # Agrupar por período
            temporal_data = df.groupby('periodo').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum'
            }).reset_index()
            
            if temporal_data.empty:
                st.info("Sin datos temporales para mostrar")
                return
            
            # Crear gráfica de línea
            fig = px.line(
                temporal_data,
                x='periodo',
                y='ingresos_totales',
                title=f'Evolución de Ingresos - Vista {title_suffix}',
                markers=True
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title=x_label,
                yaxis_title="Ingresos USD",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            fig.update_traces(
                line_color='#1f77b4',
                line_width=2,
                marker_size=4
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para la gráfica de ingresos")
        
    except Exception as e:
        st.error(f"Error creando gráfica de ingresos: {str(e)}")

def create_passport_chart(processor, grouping="Diaria"):
    """Crea gráfica de líneas de número de pasaportes con agrupación temporal"""
    try:
        # Filtrar datos de pasaportes
        if hasattr(processor, 'df') and processor.df is not None:
            passport_data = processor.df[processor.df['categoria'].str.contains('PASAPORTES', na=False)].copy()
            
            if passport_data.empty:
                st.info("Sin datos de pasaportes")
                return
            
            passport_data['fecha_emision'] = pd.to_datetime(passport_data['fecha_emision'])
            
            # Agrupar según la selección temporal
            if grouping == "Diaria":
                passport_data['periodo'] = passport_data['fecha_emision'].dt.date
                title_suffix = "Diaria"
                x_label = "Fecha"
            elif grouping == "Mensual":
                passport_data['periodo'] = passport_data['fecha_emision'].dt.to_period('M').astype(str)
                title_suffix = "Mensual"
                x_label = "Mes"
            elif grouping == "Anual":
                passport_data['periodo'] = passport_data['fecha_emision'].dt.year
                title_suffix = "Anual"
                x_label = "Año"
            
            # Agrupar por período
            passport_temporal = passport_data.groupby('periodo').agg({
                'num_tramites': 'sum'
            }).reset_index()
            
            # Crear gráfica
            fig = px.line(
                passport_temporal,
                x='periodo',
                y='num_tramites',
                title=f'Pasaportes - Vista {title_suffix}',
                markers=True
            )
            
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis_title=x_label,
                yaxis_title="Número de Pasaportes",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            fig.update_traces(line_color='#ff7f0e', line_width=2)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos disponibles para pasaportes")
            
    except Exception as e:
        st.error(f"Error creando gráfica de pasaportes: {str(e)}")

def create_matriculas_chart(processor, grouping="Diaria"):
    """Crea gráfica de líneas de número de matrículas con agrupación temporal"""
    try:
        # Buscar datos relacionados con matrículas (RCM)
        if hasattr(processor, 'df') and processor.df is not None:
            # Buscar servicios que contengan RCM o matrícula
            matricula_data = processor.df[
                processor.df['servicio'].str.contains('RCM|MATRÍCULA|MATRICULA', na=False, case=False)
            ].copy()
            
            if matricula_data.empty:
                st.info("Sin datos de matrículas")
                return
            
            matricula_data['fecha_emision'] = pd.to_datetime(matricula_data['fecha_emision'])
            
            # Agrupar según la selección temporal
            if grouping == "Diaria":
                matricula_data['periodo'] = matricula_data['fecha_emision'].dt.date
                title_suffix = "Diaria"
                x_label = "Fecha"
            elif grouping == "Mensual":
                matricula_data['periodo'] = matricula_data['fecha_emision'].dt.to_period('M').astype(str)
                title_suffix = "Mensual"
                x_label = "Mes"
            elif grouping == "Anual":
                matricula_data['periodo'] = matricula_data['fecha_emision'].dt.year
                title_suffix = "Anual"
                x_label = "Año"
            
            # Agrupar por período
            matricula_temporal = matricula_data.groupby('periodo').agg({
                'num_tramites': 'sum'
            }).reset_index()
            
            # Crear gráfica
            fig = px.line(
                matricula_temporal,
                x='periodo',
                y='num_tramites',
                title=f'Matrículas - Vista {title_suffix}',
                markers=True
            )
            
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis_title=x_label,
                yaxis_title="Número de Matrículas",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            fig.update_traces(line_color='#2ca02c', line_width=2)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos disponibles para matrículas")
            
    except Exception as e:
        st.error(f"Error creando gráfica de matrículas: {str(e)}")

def show_specific_service_analysis(processor):
    """Muestra análisis de servicio específico con 2 dropdowns y gráfica"""
    try:
        # Obtener lista de servicios disponibles directamente del DataFrame
        if hasattr(processor, 'df') and processor.df is not None:
            services_list = sorted(processor.df['servicio'].unique().tolist())
            
            # 2 DROPDOWNS: SERVICIO Y UNIDAD A ANALIZAR
            dropdown_col1, dropdown_col2 = st.columns(2)
            
            with dropdown_col1:
                selected_service = st.selectbox(
                    "Servicio:",
                    ["Seleccionar..."] + services_list[:20],  # Limitar a 20 para mejor UX
                    key="servicio_especifico_new"
                )
            
            with dropdown_col2:
                analysis_unit = st.selectbox(
                    "Unidad a analizar:",
                    ["Cantidad", "Ingreso"],
                    key="unidad_analisis"
                )
            
            if selected_service == "Seleccionar...":
                st.info("Seleccione un servicio para ver el análisis")
                return
            
            # GRÁFICA DE SERVICIO ESPECÍFICO (ANCHO COMPLETO)
            st.markdown("##### Evolución del Servicio Seleccionado")
            
            # Control de agrupación temporal para servicio específico
            specific_col1, specific_col2 = st.columns([3, 1])
            with specific_col2:
                specific_grouping = st.selectbox(
                    "Agrupación:",
                    ["Diaria", "Mensual", "Anual"],
                    key="specific_grouping",
                    help="Seleccione el nivel de agrupación temporal"
                )
            
            with specific_col1:
                create_specific_service_chart(processor, selected_service, analysis_unit, specific_grouping)
            
            # KPIS DE SERVICIO ESPECÍFICO
            st.markdown("##### KPIs del Servicio Específico")
            show_service_specific_kpis(processor, selected_service)
        else:
            st.warning("No hay datos disponibles para el análisis de servicios")
        
    except Exception as e:
        st.error(f"Error en análisis de servicio específico: {str(e)}")

def create_specific_service_chart(processor, service_name, analysis_unit, grouping="Diaria"):
    """Crea gráfica de líneas para servicio específico con agrupación temporal"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            # Filtrar datos del servicio específico
            service_data = processor.df[processor.df['servicio'] == service_name].copy()
            
            if service_data.empty:
                st.warning(f"No hay datos para el servicio: {service_name}")
                return
            
            service_data['fecha_emision'] = pd.to_datetime(service_data['fecha_emision'])
            
            # Definir columna y etiqueta según unidad de análisis
            y_column = 'num_tramites' if analysis_unit == 'Cantidad' else 'ingresos_totales'
            y_label = 'Número de Trámites' if analysis_unit == 'Cantidad' else 'Ingresos USD'
            
            # Agrupar según la selección temporal
            if grouping == "Diaria":
                service_data['periodo'] = service_data['fecha_emision'].dt.date
                title_suffix = "Diaria"
                x_label = "Fecha"
            elif grouping == "Mensual":
                service_data['periodo'] = service_data['fecha_emision'].dt.to_period('M').astype(str)
                title_suffix = "Mensual"
                x_label = "Mes"
            elif grouping == "Anual":
                service_data['periodo'] = service_data['fecha_emision'].dt.year
                title_suffix = "Anual"
                x_label = "Año"
            
            # Agrupar por período
            service_temporal = service_data.groupby('periodo').agg({
                y_column: 'sum'
            }).reset_index()
            
            # Crear gráfica
            fig = px.line(
                service_temporal,
                x='periodo',
                y=y_column,
                title=f'{analysis_unit} - {service_name} (Vista {title_suffix})',
                markers=True
            )
            
            fig.update_layout(
                height=350,
                showlegend=False,
                xaxis_title=x_label,
                yaxis_title=y_label,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            fig.update_traces(line_color='#d62728', line_width=2, marker_size=4)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles")
            
    except Exception as e:
        st.error(f"Error creando gráfica de servicio específico: {str(e)}")

def show_service_specific_kpis(processor, service_name):
    """Muestra KPIs específicos del servicio: #trámites, total ingresos, promedio, desviación estándar"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            # Filtrar datos del servicio
            service_data = processor.df[processor.df['servicio'] == service_name]
            
            if service_data.empty:
                st.warning("No hay datos para calcular KPIs del servicio")
                return
            
            # Calcular métricas
            total_tramites = service_data['num_tramites'].sum()
            total_ingresos = service_data['ingresos_totales'].sum()
            promedio_tramites = service_data['num_tramites'].mean()
            desv_std_tramites = service_data['num_tramites'].std()
            
            # Mostrar KPIs en 4 columnas
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            
            with kpi_col1:
                st.metric(
                    "# Trámites",
                    f"{total_tramites:,}",
                    help="Total de trámites del servicio"
                )
            
            with kpi_col2:
                st.metric(
                    "Total Ingresos",
                    f"${total_ingresos:,.2f}",
                    help="Ingresos totales del servicio"
                )
            
            with kpi_col3:
                st.metric(
                    "Promedio Trámites",
                    f"{promedio_tramites:.2f}",
                    help="Promedio de trámites por día"
                )
            
            with kpi_col4:
                st.metric(
                    "Desv. Std. Trámites",
                    f"{desv_std_tramites:.2f}",
                    help="Desviación estándar de trámites"
                )
        else:
            st.warning("No hay datos disponibles para KPIs del servicio")
            
    except Exception as e:
        st.error(f"Error calculando KPIs del servicio: {str(e)}")

def create_top_services_horizontal_chart(processor):
    """Crea gráfica de barras horizontales para top servicios (colores sólidos)"""
    try:
        # Obtener datos directamente del DataFrame y agrupar por servicio
        if hasattr(processor, 'df') and processor.df is not None:
            # Agrupar por servicio para obtener totales
            top_services_data = processor.df.groupby('servicio').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum'
            }).reset_index()
            
            # Ordenar por cantidad de trámites y tomar top 10
            top_services_data = top_services_data.nlargest(10, 'num_tramites')
            
            if top_services_data.empty:
                st.info("Sin datos para top servicios")
                return
            
            # Crear gráfica de barras horizontales
            fig = px.bar(
                top_services_data,
                x='num_tramites',
                y='servicio',
                orientation='h',
                title='Top 10 Servicios por Cantidad de Trámites',
                color='num_tramites',
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(
                height=500,
                showlegend=False,
                xaxis_title="Número de Trámites",
                yaxis_title="Servicio",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # Ordenar de mayor a menor
            fig.update_yaxes(categoryorder="total ascending")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para top servicios")
        
    except Exception as e:
        st.error(f"Error en gráfica de top servicios: {str(e)}")

def show_detailed_data_section(processor):
    """Muestra datos detallados con botón de exportar Excel"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            # Mostrar muestra de datos
            sample_data = processor.df.head(50).copy()
            
            # Formatear datos para mejor visualización
            display_data = sample_data.copy()
            
            # Formatear columnas monetarias
            if 'ingresos_totales' in display_data.columns:
                display_data['ingresos_totales'] = display_data['ingresos_totales'].apply(lambda x: f"${x:,.2f}")
            
            if 'costo_unitario' in display_data.columns:
                display_data['costo_unitario'] = display_data['costo_unitario'].apply(lambda x: f"${x:.2f}")
            
            # Seleccionar columnas principales
            main_columns = ['servicio', 'categoria', 'fecha_emision', 'num_tramites', 'ingresos_totales']
            available_columns = [col for col in main_columns if col in display_data.columns]
            
            st.dataframe(
                display_data[available_columns],
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"Mostrando los primeros 50 registros de {len(processor.df):,} total")
            
            # Botón exportar Excel
            if st.button("📊 Exportar Datos Detallados a Excel", use_container_width=True):
                st.info("Funcionalidad de exportación Excel en desarrollo")
        else:
            st.warning("No hay datos detallados disponibles")
            
    except Exception as e:
        st.error(f"Error mostrando datos detallados: {str(e)}")

@st.cache_data
def initialize_enhanced_processor():
    """Inicializa el procesador mejorado con datos de la base de datos"""
    try:
        processor = EnhancedDataProcessor()
        
        # Intentar cargar datos de la base de datos
        if processor.initialize_from_database():
            return processor
        
        # Si no hay datos en BD, intentar migrar desde archivo original
        if os.path.exists("Inicio/mayo.xls"):
            migrate_original_data()
            if processor.initialize_from_database():
                return processor
        
        return None
        
    except Exception as e:
        st.error(f"Error inicializando procesador: {str(e)}")
        return None

def migrate_original_data():
    """Migra datos del archivo original mayo.xls a la base de datos"""
    try:
        from data_processor import MayoDataProcessor
        from file_manager import FileManager
        
        # Usar el sistema de carga de archivos para migrar
        file_manager = FileManager()
        result = file_manager.load_file_to_database("Inicio/mayo.xls")
        
        if result['success']:
            st.success("Datos originales migrados a base de datos")
        else:
            st.warning(f"Error migrando datos: {result['message']}")
            
    except Exception as e:
        st.error(f"Error en migración: {str(e)}")

@st.cache_data
def get_database_summary():
    """Obtiene resumen de la base de datos"""
    try:
        db_manager = DatabaseManager()
        return db_manager.get_summary_stats()
    except Exception as e:
        st.error(f"Error obteniendo resumen de BD: {str(e)}")
        return {}

def show_database_status(db_summary):
    """Muestra el estado de la base de datos"""
    if not db_summary:
        return
    
    st.markdown("<h3 style='text-align: center;'>Estado de la Base de Datos</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Registros", 
            f"{db_summary.get('total_registros', 0):,}",
            help="Total de registros en la base de datos"
        )
    
    with col2:
        st.metric(
            "Ingresos Totales", 
            f"${db_summary.get('ingresos_totales', 0):,.2f}",
            help="Suma total de ingresos"
        )
    
    with col3:
        st.metric(
            "Trámites Totales", 
            f"{db_summary.get('tramites_totales', 0):,}",
            help="Total de trámites procesados"
        )
    
    with col4:
        st.metric(
            "Categorías", 
            f"{db_summary.get('categorias_unicas', 0)}",
            help="Número de categorías distintas"
        )
    
    with col5:
        st.metric(
            "Servicios", 
            f"{db_summary.get('servicios_unicos', 0)}",
            help="Número de servicios distintos"
        )
    
    st.markdown("---")

def show_main_filters(processor, db_summary):
    """Muestra filtros principales"""
    st.markdown("<h3 style='text-align: center;'>Filtros de Análisis</h3>", unsafe_allow_html=True)
    
    # Obtener rango de fechas disponible
    try:
        db_manager = DatabaseManager()
        date_range = db_manager.get_date_range()
        
        if date_range['total_registros'] > 0:
            min_date = pd.to_datetime(date_range['fecha_min']).date()
            max_date = pd.to_datetime(date_range['fecha_max']).date()
        else:
            min_date = max_date = date.today()
    except:
        min_date = max_date = date.today()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input(
            "Fecha inicio:",
            value=min_date,
            key="fecha_inicio",
            help="Seleccione fecha de inicio para el análisis"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Fecha fin:",
            value=max_date,
            key="fecha_fin",
            help="Seleccione fecha de fin para el análisis"
        )
    
    with col3:
        # Filtro por categoría
        categorias = processor.get_categories_list()
        categoria_seleccionada = st.selectbox(
            "Categoría:",
            options=["Todas"] + categorias,
            key="categoria_filter"
        )
    
    # Almacenar filtros en session_state
    st.session_state.filtros_activos = {
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'categoria': categoria_seleccionada if categoria_seleccionada != "Todas" else None
    }

def show_main_analysis(processor):
    """Muestra el análisis principal con los filtros aplicados"""
    filtros = st.session_state.get('filtros_activos', {})
    
    # Aplicar filtros al procesador
    start_date = filtros.get('fecha_inicio')
    end_date = filtros.get('fecha_fin')
    categoria = filtros.get('categoria')
    
    # Re-inicializar con filtros de fecha
    processor.initialize_from_database(start_date, end_date)
    
    # Aplicar filtro de categoría si existe
    if categoria and processor.df is not None:
        processor.df = processor.df[processor.df['categoria'] == categoria]
    
    # Verificar que tenemos datos
    if processor.df is None or processor.df.empty:
        st.warning("⚠️ No hay datos para el período seleccionado")
        return
    
    # KPIs principales
    show_kpis(processor)
    
    # Análisis temporal
    show_temporal_analysis(processor)
    
    # Análisis por servicio
    show_service_analysis(processor)
    
    # Análisis de eficiencia
    show_efficiency_analysis(processor)
    
    # Datos detallados
    show_detailed_data(processor)

def show_kpis(processor):
    """Muestra los KPIs principales"""
    stats = processor.get_summary_stats()
    
    st.markdown("<h3 style='text-align: center;'>KPIs del Período Seleccionado</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Ingresos Totales",
            f"${stats['total_ingresos']:,.2f}",
            help="Suma de todos los ingresos en el período"
        )
    
    with col2:
        st.metric(
            "Trámites Procesados",
            f"{stats['total_tramites']:,}",
            help="Total de trámites completados"
        )
    
    with col3:
        st.metric(
            "Ingreso Diario Promedio",
            f"${stats['ingreso_diario_promedio']:,.2f}",
            help="Promedio de ingresos por día"
        )
    
    with col4:
        st.metric(
            "Desviación Estándar",
            f"${stats['ingreso_diario_std']:,.2f}",
            help="Variabilidad de ingresos diarios"
        )

def show_temporal_analysis(processor):
    """Muestra análisis temporal"""
    st.markdown("<h3 style='text-align: center;'>Análisis Temporal</h3>", unsafe_allow_html=True)
    
    # Selector de agrupación temporal
    col1, col2 = st.columns([1, 3])
    
    with col1:
        group_by = st.selectbox(
            "Agrupar por:",
            options=['dia', 'mes', 'trimestre', 'año'],
            key="temporal_group"
        )
    
    # Gráfico de ingresos por período
    temporal_data = processor.get_temporal_data(group_by)
    
    if not temporal_data.empty:
        # Preparar datos para el gráfico
        x_col = temporal_data.columns[0]  # Primera columna es la temporal
        x_data = temporal_data[x_col].astype(str)
        
        # Gráfico de ingresos únicamente
        fig_ingresos = go.Figure()
        
        fig_ingresos.add_trace(
            go.Scatter(
                x=x_data,
                y=temporal_data['ingresos_totales'],
                name='Ingresos',
                line=dict(color='#1f77b4', width=3),
                hovertemplate='<b>%{x}</b><br>Ingresos: $%{y:,.2f}<extra></extra>'
            )
        )
        
        fig_ingresos.update_layout(
            title='Ingresos por Período',
            xaxis_title='Período',
            yaxis_title='Ingresos ($)',
            height=400,
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_ingresos, use_container_width=True)
    
    # Nueva sección: Análisis por servicio específico
    st.markdown("---")
    st.markdown("<h4 style='text-align: center;'>Análisis de Servicio Específico</h4>", unsafe_allow_html=True)
    
    # Obtener lista de servicios únicos
    if processor.df is not None and not processor.df.empty:
        services_list = sorted(processor.df['servicio'].dropna().unique())
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            selected_service = st.selectbox(
                "Seleccionar servicio:",
                options=services_list,
                key="service_selector"
            )
        
        with col2:
            service_group_by = st.selectbox(
                "Agrupar por:",
                options=['dia', 'mes', 'trimestre', 'año'],
                key="service_temporal_group"
            )
        
        if selected_service:
            service_data = processor.get_service_temporal_data(
                selected_service, 
                service_group_by
            )
            
            if not service_data.empty:
                # Preparar datos para el gráfico del servicio
                x_col_service = service_data.columns[0]
                x_data_service = service_data[x_col_service].astype(str)
                
                # Gráfico del servicio específico
                fig_service = go.Figure()
                
                fig_service.add_trace(
                    go.Scatter(
                        x=x_data_service,
                        y=service_data['num_tramites'],
                        name=f'{selected_service} - Trámites',
                        line=dict(color='#2ca02c', width=3),
                        hovertemplate=f'<b>%{{x}}</b><br>{selected_service}<br>Trámites: %{{y:,}}<extra></extra>'
                    )
                )
                
                fig_service.update_layout(
                    title=f'Número de Trámites - {selected_service}',
                    xaxis_title='Período',
                    yaxis_title='Número de Trámites',
                    height=400,
                    showlegend=False,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_service, use_container_width=True)
                
                # Mostrar estadísticas del servicio
                total_tramites_service = service_data['num_tramites'].sum()
                total_ingresos_service = service_data['ingresos_totales'].sum()
                promedio_tramites = service_data['num_tramites'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Trámites", f"{total_tramites_service:,}")
                with col2:
                    st.metric("Total Ingresos", f"${total_ingresos_service:,.2f}")
                with col3:
                    st.metric("Promedio por Período", f"{promedio_tramites:.1f}")
            else:
                st.info(f"No hay datos disponibles para {selected_service} en el período seleccionado")
    else:
        st.info("No hay datos suficientes para análisis temporal")


def show_service_analysis(processor):
    """Muestra análisis por servicio"""
    st.markdown("<h3 style='text-align: center;'>Análisis por Servicios</h3>", unsafe_allow_html=True)
    
    # Crear dos columnas para los gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='text-align: center;'>Top Servicios por Ingresos</h4>", unsafe_allow_html=True)
        top_services_ingresos = processor.get_top_services(by='ingresos', top_n=10)
        
        if not top_services_ingresos.empty:
            fig_ingresos = px.bar(
                top_services_ingresos,
                y='servicio',
                x='ingresos_totales',
                orientation='h',
                title='Top 10 Servicios por Ingresos Totales',
                labels={
                    'ingresos_totales': 'Ingresos ($)',
                    'servicio': 'Servicio'
                },
                color='ingresos_totales',
                color_continuous_scale='Viridis',
                height=500
            )
            
            fig_ingresos.update_layout(
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_ingresos, use_container_width=True)
    
    with col2:
        st.markdown("<h4 style='text-align: center;'>Top Servicios por Producción</h4>", unsafe_allow_html=True)
        top_services_tramites = processor.get_top_services(by='tramites', top_n=10)
        
        if not top_services_tramites.empty:
            fig_tramites = px.bar(
                top_services_tramites,
                y='servicio',
                x='num_tramites',
                orientation='h',
                title='Top 10 Servicios por Número de Trámites',
                labels={
                    'num_tramites': 'Trámites',
                    'servicio': 'Servicio'
                },
                color='num_tramites',
                color_continuous_scale='Oranges',
                height=500
            )
            
            fig_tramites.update_layout(
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_tramites, use_container_width=True)
    
    
    # Tabla resumen de todos los servicios
    st.markdown("<h4 style='text-align: center;'>Resumen de Todos los Servicios</h4>", unsafe_allow_html=True)
    
    all_services = processor.get_data_by_service()
    if not all_services.empty:
        # Calcular métricas adicionales
        all_services['ingreso_por_tramite'] = all_services['ingresos_totales'] / all_services['num_tramites']
        
        # Renombrar columnas para mejor visualización
        display_services = all_services[['categoria', 'servicio', 'num_tramites', 'ingresos_totales', 'ingreso_por_tramite', 'registros']].copy()
        display_services.columns = ['Categoría', 'Servicio', 'Trámites', 'Ingresos ($)', 'Ingreso/Trámite ($)', 'Registros']
        
        # Ordenar por ingresos descendente
        display_services = display_services.sort_values('Ingresos ($)', ascending=False)
        
        st.dataframe(
            display_services.round(2),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ingresos ($)": st.column_config.NumberColumn("Ingresos ($)", format="$%.2f"),
                "Ingreso/Trámite ($)": st.column_config.NumberColumn("Ingreso/Trámite ($)", format="$%.2f")
            }
        )

def show_weekly_analysis_main(processor):
    """Muestra análisis por día de la semana en análisis principal"""
    
    # Calcular estadísticas por día de la semana
    weekly_stats = calculate_weekly_statistics_main(processor)
    
    if weekly_stats:
        # Mostrar días de mayor y menor actividad
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "🔥 Día con MAYOR actividad promedio",
                weekly_stats['ingresos']['max_day'],
                f"${weekly_stats['ingresos']['max_value']:,.2f}/día"
            )
            
            st.metric(
                "🔥 Día con MÁS trámites promedio",
                weekly_stats['tramites']['max_day'],
                f"{weekly_stats['tramites']['max_value']:,.1f} trámites/día"
            )
        
        with col2:
            st.metric(
                "❄️ Día con MENOR actividad promedio",
                weekly_stats['ingresos']['min_day'],
                f"${weekly_stats['ingresos']['min_value']:,.2f}/día"
            )
            
            st.metric(
                "❄️ Día con MENOS trámites promedio",
                weekly_stats['tramites']['min_day'],
                f"{weekly_stats['tramites']['min_value']:,.1f} trámites/día"
            )
        
        st.markdown("---")
        
        # Tabla detallada por día de la semana
        st.markdown("##### 📊 Estadísticas Detalladas por Día de la Semana")
        
        df_weekly = pd.DataFrame(weekly_stats['full_table'])
        df_weekly = df_weekly.round(2)
        
        # Formatear columnas
        df_weekly['Ingresos Promedio'] = df_weekly['Ingresos Promedio'].apply(lambda x: f"${x:,.2f}")
        df_weekly['Trámites Promedio'] = df_weekly['Trámites Promedio'].apply(lambda x: f"{x:,.1f}")
        
        st.dataframe(
            df_weekly,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Día de la Semana": st.column_config.TextColumn("Día de la Semana", width="medium"),
                "Ingresos Promedio": st.column_config.TextColumn("💰 Ingresos Promedio", width="medium"),
                "Trámites Promedio": st.column_config.TextColumn("📄 Trámites Promedio", width="medium")
            }
        )
    else:
        st.warning("No se pudieron calcular estadísticas por día de la semana.")

def calculate_weekly_statistics_main(processor):
    """Calcula estadísticas por día de la semana para el procesador principal"""
    try:
        if processor.df is None or processor.df.empty:
            return None
            
        df = processor.df.copy()
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
        df['dia_semana_es'] = df['fecha_emision'].dt.strftime('%A').map({
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        })
        
        # Agrupar por día específico para obtener totales diarios
        daily_totals = df.groupby(['fecha_emision', 'dia_semana_es']).agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        }).reset_index()
        
        # Calcular promedios por día de la semana
        weekly_averages = daily_totals.groupby('dia_semana_es').agg({
            'ingresos_totales': 'mean',
            'num_tramites': 'mean'
        }).reset_index()
        
        # Ordenar por días de la semana
        day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        weekly_averages['dia_semana_es'] = pd.Categorical(
            weekly_averages['dia_semana_es'], 
            categories=day_order, 
            ordered=True
        )
        weekly_averages = weekly_averages.sort_values('dia_semana_es').reset_index(drop=True)
        
        # Encontrar días de mayor y menor actividad
        ingresos_max_idx = weekly_averages['ingresos_totales'].idxmax()
        ingresos_min_idx = weekly_averages['ingresos_totales'].idxmin()
        tramites_max_idx = weekly_averages['num_tramites'].idxmax()
        tramites_min_idx = weekly_averages['num_tramites'].idxmin()
        
        # Preparar tabla completa
        full_table = []
        for _, row in weekly_averages.iterrows():
            full_table.append({
                'Día de la Semana': row['dia_semana_es'],
                'Ingresos Promedio': row['ingresos_totales'],
                'Trámites Promedio': row['num_tramites']
            })
        
        return {
            'ingresos': {
                'max_day': weekly_averages.loc[ingresos_max_idx, 'dia_semana_es'],
                'max_value': weekly_averages.loc[ingresos_max_idx, 'ingresos_totales'],
                'min_day': weekly_averages.loc[ingresos_min_idx, 'dia_semana_es'],
                'min_value': weekly_averages.loc[ingresos_min_idx, 'ingresos_totales']
            },
            'tramites': {
                'max_day': weekly_averages.loc[tramites_max_idx, 'dia_semana_es'],
                'max_value': weekly_averages.loc[tramites_max_idx, 'num_tramites'],
                'min_day': weekly_averages.loc[tramites_min_idx, 'dia_semana_es'],
                'min_value': weekly_averages.loc[tramites_min_idx, 'num_tramites']
            },
            'full_table': full_table
        }
        
    except Exception as e:
        st.error(f"Error calculando estadísticas semanales: {str(e)}")
        return None

def show_efficiency_analysis(processor):
    """Muestra análisis de eficiencia"""
    st.markdown("<h3 style='text-align: center;'>Análisis de Eficiencia</h3>", unsafe_allow_html=True)
    
    efficiency_metrics = processor.get_efficiency_metrics()
    
    if efficiency_metrics:
        global_metrics = efficiency_metrics.get('global_metrics', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Ingreso por Trámite",
                f"${global_metrics.get('ingreso_promedio_por_tramite', 0):.2f}",
                help="Promedio de ingresos por trámite procesado"
            )
        
        with col2:
            st.metric(
                "Ingreso Diario Promedio",
                f"${global_metrics.get('ingreso_diario_promedio', 0):.2f}",
                help="Promedio de ingresos por día"
            )
        
        with col3:
            st.metric(
                "Desviación Estándar Diaria",
                f"${global_metrics.get('ingreso_diario_std', 0):.2f}",
                help="Variabilidad de ingresos diarios"
            )

def show_detailed_data(processor):
    """Muestra datos detallados con opciones de filtrado"""
    st.markdown("<h3 style='text-align: center;'>Datos Detallados</h3>", unsafe_allow_html=True)
    
    if processor.df is not None and not processor.df.empty:
        
        # Controles de visualización
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_rows = st.selectbox(
                "Mostrar filas:",
                options=[50, 100, 200, 500, "Todas"],
                key="show_rows"
            )
        
        with col2:
            if st.button("Exportar a CSV"):
                csv = processor.df.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"datos_consulares_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("Exportar a Excel"):
                # Crear archivo Excel temporal
                excel_filename = f"datos_consulares_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                processor.export_current_data(excel_filename, format='excel')
                
                with open(excel_filename, "rb") as file:
                    st.download_button(
                        label="Descargar Excel",
                        data=file.read(),
                        file_name=excel_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        # Mostrar datos
        display_df = processor.df.copy()
        
        if show_rows != "Todas":
            display_df = display_df.head(show_rows)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Mostrando {len(display_df)} de {len(processor.df)} registros")

def show_empty_state():
    """Muestra estado cuando no hay datos"""
    st.markdown("""
    <div style='text-align: center;'>
    <h3>No hay datos disponibles</h3>
    
    <p>Para comenzar a usar el dashboard:</p>
    
    <ol style='text-align: left; display: inline-block;'>
    <li><strong>Ir a Gestión de Archivos</strong> en el menú lateral</li>
    <li><strong>Buscar archivos</strong> con datos consulares (.xls, .xlsx, .html)</li>
    <li><strong>Cargar archivos</strong> a la base de datos</li>
    <li><strong>Regresar a esta página</strong> para ver los análisis</li>
    </ol>
    
    <p>El sistema creará automáticamente una base de datos local para almacenar<br>
    y gestionar todos sus datos consulares de forma centralizada.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ir a Gestión de Archivos"):
        st.session_state.page = "Gestión de Archivos"
        st.rerun()

def show_settings_page():
    """Página de configuración"""
    st.markdown("<h1 style='text-align: center;'>Configuración del Sistema</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h3 style='text-align: center;'>Información del Sistema</h3>", unsafe_allow_html=True)
    
    try:
        db_manager = DatabaseManager()
        db_path = db_manager.db_path
        
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            st.info(f"Base de datos: `{db_path}` ({db_size:.2f} MB)")
        else:
            st.warning("Base de datos no encontrada")
        
        # Estadísticas de la BD
        stats = db_manager.get_summary_stats()
        date_range = db_manager.get_date_range()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Estadísticas:**")
            st.write(f"- Registros totales: {stats.get('total_registros', 0):,}")
            st.write(f"- Categorías únicas: {stats.get('categorias_unicas', 0)}")
            st.write(f"- Servicios únicos: {stats.get('servicios_unicos', 0)}")
        
        with col2:
            st.markdown("**Rango de fechas:**")
            if date_range.get('total_registros', 0) > 0:
                st.write(f"- Desde: {date_range.get('fecha_min', 'N/A')}")
                st.write(f"- Hasta: {date_range.get('fecha_max', 'N/A')}")
            else:
                st.write("- Sin datos")
    
    except Exception as e:
        st.error(f"Error obteniendo información del sistema: {str(e)}")
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Acciones de Mantenimiento</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Limpiar Cache"):
            st.cache_data.clear()
            st.success("Cache limpiado")
    
    with col2:
        if st.button("Crear Backup BD"):
            try:
                db_manager = DatabaseManager()
                backup_path = db_manager.backup_database()
                st.success(f"Backup creado: {backup_path}")
            except Exception as e:
                st.error(f"Error creando backup: {str(e)}")

if __name__ == "__main__":
    main()