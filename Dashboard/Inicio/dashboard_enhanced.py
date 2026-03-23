import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from enhanced_data_processor import EnhancedDataProcessor
from file_upload_page import show_file_upload_page
from service_grouping_page import show_service_grouping_page
from period_comparison_page import show_period_comparison_page
from service_mapping_config_page import show_service_mapping_config_page
from monthly_report_page import show_monthly_report_page
from heatmap_page import show_heatmap_page
from service_name_mappings import get_short_service_name
from database_manager import DatabaseManager
from datetime import datetime, date
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Consular - Análisis Histórico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado — tema crema / papel
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

/* ── Variables ── */
:root {
    --bg-main:       #F7F5F0;
    --bg-surface:    #EDEBE6;
    --bg-elevated:   #FFFFFF;
    --border:        rgba(44, 74, 110, 0.18);
    --border-subtle: #E0DDD7;
    --accent:        #2C4A6E;
    --accent-dim:    rgba(44, 74, 110, 0.08);
    --accent-mid:    rgba(44, 74, 110, 0.55);
    --text-primary:  #1E2B3C;
    --text-secondary:#4A5568;
    --text-muted:    #8A9099;
    --success:       #2A7A4B;
    --danger:        #C0392B;
}

/* ── Fondo global ── */
.stApp, .main {
    background-color: var(--bg-main) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background-color: var(--bg-surface) !important;
}

/* ── Botones de navegación (sidebar) ── */
.stButton > button {
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    padding: 0.55rem 0.9rem !important;
    margin-bottom: 2px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background-color: var(--accent-dim) !important;
    color: var(--accent) !important;
    border-color: var(--border) !important;
}
/* Botón activo (primary) */
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[data-testid*="primary"] {
    background-color: var(--accent-dim) !important;
    color: var(--accent) !important;
    border-color: var(--border) !important;
    font-weight: 600 !important;
}

/* ── Área de contenido principal ── */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1300px !important;
}

/* ── Tipografía ── */
h1, h2, h3, h4, h5 {
    font-family: 'DM Serif Display', Georgia, serif !important;
    color: var(--text-primary) !important;
    font-weight: 400 !important;
}
h1 { font-size: 2.2rem !important; letter-spacing: -0.02em; line-height: 1.15; }
h2 { font-size: 1.5rem !important; }
h3 { font-size: 1.2rem !important; color: var(--text-secondary) !important; }
p, label, .stMarkdown p {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-secondary) !important;
    line-height: 1.65 !important;
}

/* ── Métricas (st.metric) ── */
[data-testid="metric-container"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-top: 2px solid var(--accent) !important;
    border-radius: 8px !important;
    padding: 1.1rem 1.2rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--text-muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', Georgia, serif !important;
    font-size: 1.7rem !important;
    color: var(--text-primary) !important;
}

/* ── Selectbox / inputs ── */
.stSelectbox > div > div,
.stDateInput > div > div,
.stTextInput > div > div {
    background-color: var(--bg-elevated) !important;
    border-color: var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox label, .stDateInput label, .stTextInput label,
.stRadio label, .stMultiSelect label {
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Radio buttons ── */
.stRadio > div {
    gap: 0.5rem !important;
}
.stRadio div[role="radiogroup"] label {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 5px !important;
    padding: 0.35rem 0.8rem !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    transition: all 0.18s ease !important;
}
.stRadio div[role="radiogroup"] label:has(input:checked) {
    background: var(--accent-dim) !important;
    border-color: var(--border) !important;
    color: var(--accent) !important;
    font-weight: 500 !important;
}

/* ── Divisores ── */
hr, .stMarkdown hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, var(--border-subtle), transparent) !important;
    margin: 1.8rem 0 !important;
}

/* ── Gráficas ── */
.js-plotly-plot {
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(30,43,60,0.07) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}

/* ── Dataframe / tablas ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}

/* ── Mensajes de alerta ── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb { background: var(--border-subtle); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal del dashboard"""
    
    # Barra lateral para navegación
    st.sidebar.markdown("""
    <div style="padding: 1.4rem 0.5rem 1.2rem; margin-bottom: 0.5rem;">
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.35rem;">
            <div style="width:3px; height:28px; background:#2C4A6E; border-radius:2px; flex-shrink:0;"></div>
            <span style="font-family:'DM Serif Display',Georgia,serif; font-size:1.15rem; color:#1E2B3C; line-height:1.2;">
                Consulmex<br><span style="font-size:0.75rem; font-family:'DM Sans',sans-serif; color:#8A9099; font-weight:400; letter-spacing:0.12em; text-transform:uppercase;">Kansas City</span>
            </span>
        </div>
        <div style="height:1px; background:linear-gradient(to right, rgba(44,74,110,0.3), transparent); margin-top:0.8rem;"></div>
        <p style="font-family:'DM Sans',sans-serif; font-size:0.72rem; color:#8A9099; margin:0.6rem 0 0; text-transform:uppercase; letter-spacing:0.1em;">
            Sistema de Análisis
        </p>
    </div>
    <div style="margin: 0 0 0.3rem; font-family:'DM Sans',sans-serif; font-size:0.68rem; color:#8A9099; text-transform:uppercase; letter-spacing:0.12em; padding: 0 0.3rem;">
        Análisis
    </div>
    """, unsafe_allow_html=True)
    
    # Navegación con botones individuales
    if st.sidebar.button("Análisis de Datos", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Análisis de Datos" else "secondary"):
        st.session_state.current_page = "Análisis de Datos"
        st.rerun()
    
    if st.sidebar.button("Comparación de Períodos", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Comparación de Períodos" else "secondary"):
        st.session_state.current_page = "Comparación de Períodos"
        st.rerun()

    if st.sidebar.button("Reporte Mensual", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Reporte Mensual" else "secondary"):
        st.session_state.current_page = "Reporte Mensual"
        st.rerun()

    if st.sidebar.button("Heatmap Calendario", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Heatmap Calendario" else "secondary"):
        st.session_state.current_page = "Heatmap Calendario"
        st.rerun()

    st.sidebar.markdown("""
    <div style="margin: 0.8rem 0 0.3rem; font-family:'DM Sans',sans-serif; font-size:0.68rem; color:#8A9099; text-transform:uppercase; letter-spacing:0.12em; padding: 0 0.3rem;">
        Configuración
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Agrupación de Servicios", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Agrupación de Servicios" else "secondary"):
        st.session_state.current_page = "Agrupación de Servicios"
        st.rerun()

    if st.sidebar.button("Nombres de Servicios", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Nombres de Servicios" else "secondary"):
        st.session_state.current_page = "Nombres de Servicios"
        st.rerun()

    st.sidebar.markdown("""
    <div style="margin: 0.8rem 0 0.3rem; font-family:'DM Sans',sans-serif; font-size:0.68rem; color:#8A9099; text-transform:uppercase; letter-spacing:0.12em; padding: 0 0.3rem;">
        Datos
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Gestión de Archivos", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Gestión de Archivos" else "secondary"):
        st.session_state.current_page = "Gestión de Archivos"
        st.rerun()

    if st.sidebar.button("Configuración", use_container_width=True, type="primary" if st.session_state.get('current_page') == "Configuración" else "secondary"):
        st.session_state.current_page = "Configuración"
        st.rerun()
    
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
    elif page == "Nombres de Servicios":
        show_service_mapping_config_page()
    elif page == "Comparación de Períodos":
        show_period_comparison_page()
    elif page == "Reporte Mensual":
        show_monthly_report_page()
    elif page == "Heatmap Calendario":
        show_heatmap_page()
    else:
        show_settings_page()

def show_analytics_page():
    """Página principal de análisis de datos - Nueva estructura"""
    
    # Header principal
    header_col1, header_col2 = st.columns([3, 1])
    
    with header_col1:
        st.markdown("""
        <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #E0DDD7;">
            <p style="font-family:'DM Sans',sans-serif; font-size:0.72rem; color:#2C4A6E; text-transform:uppercase; letter-spacing:0.15em; margin:0 0 0.4rem;">
                Consulado de México
            </p>
            <h1 style="font-family:'DM Serif Display',Georgia,serif; color:#1E2B3C; margin:0 0 0.3rem; font-size:2.1rem; font-weight:400; letter-spacing:-0.01em; line-height:1.1;">
                Kansas City
            </h1>
            <p style="font-family:'DM Sans',sans-serif; color:#8A9099; margin:0; font-size:0.85rem; letter-spacing:0.04em;">
                Sistema de análisis de documentación consular
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("Actualizar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Inicializar procesador
    processor = initialize_enhanced_processor()
    if processor is None:
        show_empty_state()
        return
    
    # Filtros de análisis
    st.markdown("### Filtros de análisis")
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
    
    st.markdown("---")
    
    # Estadísticas generales
    st.markdown("### Resumen general")
    show_main_kpis(processor)
    
    st.markdown("---")
    
    # Evolución de ingresos
    st.markdown("### Evolución de ingresos")
    
    # Control de agrupación temporal para gráfica de ingresos
    income_col1, income_col2 = st.columns([2, 1])
    with income_col2:
        income_grouping = st.selectbox(
            "Agrupación temporal",
            ["Diaria", "Mensual", "Anual"],
            index=1,  # Default a Mensual
            key="income_grouping"
        )
    
    with income_col1:
        create_income_line_chart(processor, income_grouping)
    
    st.markdown("---")
    
    # 5. GRÁFICAS DE PASAPORTES Y MATRÍCULAS (50% CADA UNA)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### Pasaportes")
        # Control de agrupación temporal para pasaportes
        passport_grouping = st.selectbox(
            "Agrupación",
            ["Diaria", "Mensual", "Anual"],
            index=1,  # Default a Mensual
            key="passport_grouping"
        )
        create_passport_chart(processor, passport_grouping)
    
    with chart_col2:
        st.markdown("### Matrículas")
        # Control de agrupación temporal para matrículas
        matricula_grouping = st.selectbox(
            "Agrupación",
            ["Diaria", "Mensual", "Anual"],
            index=1,  # Default a Mensual
            key="matricula_grouping"
        )
        create_matriculas_chart(processor, matricula_grouping)
    
    # 5.1 ESTADÍSTICAS ESPECÍFICAS DE PASAPORTES Y MATRÍCULAS
    st.markdown("---")
    
    # Estadísticas específicas por categoría
    stats_col1, stats_col2 = st.columns(2)
    
    with stats_col1:
        st.markdown("**Estadísticas de Pasaportes**")
        show_passport_specific_stats(processor)
    
    with stats_col2:
        st.markdown("**Estadísticas de Matrículas**")
        show_matricula_specific_stats(processor)
    
    st.markdown("---")
    
    # Análisis de servicio específico
    st.markdown("### Análisis de servicio específico")
    show_specific_service_analysis(processor)
    
    st.markdown("---")
    
    # Top servicios por producción
    st.markdown("### Top servicios por cantidad")
    create_top_services_horizontal_chart(processor)
    
    st.markdown("---")
    
    # 7.1 ANÁLISIS POR DÍA DE LA SEMANA (SIN RECUADRO)
    show_weekly_analysis_main(processor)
    
    st.markdown("---")
    
    # Exportar dashboard
    if st.button("Exportar a PDF", use_container_width=True):
        export_dashboard_pdf(processor)
    
    # Apartado de datos detallados eliminado por solicitud del usuario

def _render_kpi_card(label: str, value: str, sublabel: str = "") -> str:
    """Retorna HTML de una tarjeta KPI con el tema crema."""
    sub_html = f'<p style="font-family:\'DM Sans\',sans-serif; font-size:0.72rem; color:#8A9099; margin:0.4rem 0 0; letter-spacing:0.03em;">{sublabel}</p>' if sublabel else ""
    return f"""
    <div style="background:#FFFFFF; border:1px solid #E0DDD7; border-top:2px solid #2C4A6E;
                border-radius:8px; padding:1.1rem 1.2rem; box-shadow:0 1px 3px rgba(30,43,60,0.06);">
        <p style="font-family:'DM Sans',sans-serif; font-size:0.72rem; font-weight:500; text-transform:uppercase;
                  letter-spacing:0.09em; color:#8A9099; margin:0 0 0.5rem;">{label}</p>
        <p style="font-family:'DM Serif Display',Georgia,serif; font-size:1.75rem; color:#1E2B3C; margin:0; line-height:1.1;">{value}</p>
        {sub_html}
    </div>"""


def show_main_kpis(processor):
    """Muestra Indicadores principales: ingresos totales, trámites, promedio diario, desviación estándar diaria"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            df = processor.df.copy()
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])

            ingresos_diarios = df.groupby(df['fecha_emision'].dt.date)['ingresos_totales'].sum()

            total_ingresos = df['ingresos_totales'].sum()
            total_tramites = df['num_tramites'].sum()
            promedio_diario = ingresos_diarios.mean()
            desv_std_diaria = ingresos_diarios.std()

            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

            with kpi_col1:
                st.markdown(_render_kpi_card(
                    "Ingresos Totales", f"${total_ingresos:,.2f}",
                    "Suma del período"
                ), unsafe_allow_html=True)
            with kpi_col2:
                st.markdown(_render_kpi_card(
                    "Trámites", f"{total_tramites:,}",
                    "Documentos procesados"
                ), unsafe_allow_html=True)
            with kpi_col3:
                st.markdown(_render_kpi_card(
                    "Promedio Diario", f"${promedio_diario:,.2f}",
                    "Ingresos por día"
                ), unsafe_allow_html=True)
            with kpi_col4:
                st.markdown(_render_kpi_card(
                    "Desv. Estándar", f"${desv_std_diaria:,.2f}",
                    "Variabilidad diaria"
                ), unsafe_allow_html=True)
        else:
            st.warning("No hay datos disponibles para calcular Indicadores")

    except Exception as e:
        st.error(f"Error calculando Indicadores: {str(e)}")

def _apply_chart_theme(fig, height=400, title_size=15):
    """Aplica el tema crema/papel consistente a cualquier figura Plotly."""
    fig.update_layout(
        height=height,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#F7F5F0",
        font_family="'DM Sans', sans-serif",
        font_color="#4A5568",
        title_font_family="'DM Serif Display', Georgia, serif",
        title_font_color="#1E2B3C",
        title_font_size=title_size,
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#E0DDD7",
            borderwidth=1,
            font=dict(color="#4A5568", size=11),
        ),
        xaxis=dict(
            gridcolor="#EEECe8",
            linecolor="#E0DDD7",
            tickcolor="#E0DDD7",
            tickfont=dict(color="#8A9099", size=11),
            title_font=dict(color="#8A9099", size=11),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#EEECe8",
            linecolor="#E0DDD7",
            tickcolor="#E0DDD7",
            tickfont=dict(color="#8A9099", size=11),
            title_font=dict(color="#8A9099", size=11),
            zeroline=False,
        ),
        margin=dict(t=50, b=40, l=50, r=20),
    )
    return fig


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
            
            _apply_chart_theme(fig, height=400, title_size=15)
            fig.update_layout(showlegend=False, xaxis_title=x_label, yaxis_title="Ingresos USD")
            fig.update_traces(
                line_color='#2C4A6E',
                line_width=2.5,
                marker_size=5,
                marker_color='#2C4A6E',
                marker_line_color='#FFFFFF',
                marker_line_width=1.5,
                fill='tozeroy',
                fillcolor='rgba(44,74,110,0.07)',
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
            
            _apply_chart_theme(fig, height=300, title_size=13)
            fig.update_layout(showlegend=False, xaxis_title=x_label, yaxis_title="Pasaportes")
            fig.update_traces(
                line_color='#3A7CA5',
                line_width=2,
                marker_size=4,
                marker_color='#3A7CA5',
                marker_line_color='#FFFFFF',
                marker_line_width=1.5,
                fill='tozeroy',
                fillcolor='rgba(58,124,165,0.08)',
            )
            
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
            
            _apply_chart_theme(fig, height=300, title_size=13)
            fig.update_layout(showlegend=False, xaxis_title=x_label, yaxis_title="Matrículas")
            fig.update_traces(
                line_color='#2A7A4B',
                line_width=2,
                marker_size=4,
                marker_color='#2A7A4B',
                marker_line_color='#FFFFFF',
                marker_line_width=1.5,
                fill='tozeroy',
                fillcolor='rgba(42,122,75,0.08)',
            )
            
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
            
            # Crear lista para el selector con nombres cortos y mapeo inverso
            service_display_options = ["Seleccionar..."]
            service_mapping = {}  # mapeo de nombre_corto -> nombre_original
            
            for service in services_list[:20]:  # Limitar a 20 para mejor UX
                short_name = get_short_service_name(service)
                display_name = f"{short_name}" if short_name != service else service
                service_display_options.append(display_name)
                service_mapping[display_name] = service
            
            # Controles principales
            dropdown_col1, dropdown_col2 = st.columns(2)
            
            with dropdown_col1:
                selected_service_display = st.selectbox(
                    "Seleccionar servicio",
                    service_display_options,
                    key="servicio_especifico_new"
                )
                
                # Obtener el nombre original del servicio
                selected_service = service_mapping.get(selected_service_display, selected_service_display)
            
            with dropdown_col2:
                analysis_unit = st.selectbox(
                    "Métrica a analizar",
                    ["Cantidad", "Ingreso"],
                    key="unidad_analisis"
                )
            
            if selected_service == "Seleccionar...":
                st.info("Seleccione un servicio para ver el análisis")
                return
            
            # Evolución del servicio seleccionado
            st.markdown("**Evolución del servicio seleccionado**")
            
            # Control de agrupación temporal para servicio específico
            specific_col1, specific_col2 = st.columns([2, 1])
            with specific_col2:
                specific_grouping = st.selectbox(
                    "Agrupación",
                    ["Diaria", "Mensual", "Anual"],
                    index=1,  # Default a Mensual
                    key="specific_grouping"
                )
            
            with specific_col1:
                create_specific_service_chart(processor, selected_service, analysis_unit, specific_grouping)
            
            # Estadísticas del servicio específico
            st.markdown("**Estadísticas del servicio específico**")
            show_service_specific_stats(processor, selected_service)
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
            
            # Crear gráfica con nombre corto en el título
            service_short_name = get_short_service_name(service_name)
            fig = px.line(
                service_temporal,
                x='periodo',
                y=y_column,
                title=f'{analysis_unit} - {service_short_name} (Vista {title_suffix})',
                markers=True
            )
            
            _apply_chart_theme(fig, height=350, title_size=13)
            fig.update_layout(showlegend=False, xaxis_title=x_label, yaxis_title=y_label)
            fig.update_traces(
                line_color='#7B5EA7',
                line_width=2,
                marker_size=5,
                marker_color='#7B5EA7',
                marker_line_color='#FFFFFF',
                marker_line_width=1.5,
                fill='tozeroy',
                fillcolor='rgba(123,94,167,0.08)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles")
            
    except Exception as e:
        st.error(f"Error creando gráfica de servicio específico: {str(e)}")

def show_passport_specific_stats(processor):
    """Muestra estadísticas específicas de pasaportes"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            # Filtrar datos de pasaportes
            passport_data = processor.df[processor.df['categoria'].str.contains('PASAPORTES', na=False)].copy()
            
            if passport_data.empty:
                st.info("Sin datos de pasaportes")
                return
            
            passport_data['fecha_emision'] = pd.to_datetime(passport_data['fecha_emision'])
            
            # Calcular estadísticas específicas de pasaportes basadas en trámites
            ingresos_diarios = passport_data.groupby(passport_data['fecha_emision'].dt.date)['ingresos_totales'].sum()
            tramites_diarios = passport_data.groupby(passport_data['fecha_emision'].dt.date)['num_tramites'].sum()
            
            total_ingresos = passport_data['ingresos_totales'].sum()
            total_tramites = passport_data['num_tramites'].sum()
            promedio_diario_tramites = tramites_diarios.mean()
            desv_std_diaria_tramites = tramites_diarios.std()
            
            # Mostrar estadísticas en formato limpio
            cols = st.columns(4)
            with cols[0]:
                st.metric("Ingresos totales", f"${total_ingresos:,.0f}")
            with cols[1]:
                st.metric("Trámites totales", f"{total_tramites:,}")
            with cols[2]:
                st.metric("Promedio diario", f"{promedio_diario_tramites:,.1f}")
            with cols[3]:
                st.metric("Desv. Std.", f"{desv_std_diaria_tramites:,.1f}")
        else:
            st.warning("No hay datos disponibles para estadísticas de pasaportes")
            
    except Exception as e:
        st.error(f"Error calculando estadísticas de pasaportes: {str(e)}")

def show_matricula_specific_stats(processor):
    """Muestra estadísticas específicas de matrículas"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            # Filtrar datos de matrículas (RCM)
            matricula_data = processor.df[
                processor.df['servicio'].str.contains('RCM|MATRÍCULA|MATRICULA', na=False, case=False)
            ].copy()
            
            if matricula_data.empty:
                st.info("Sin datos de matrículas")
                return
            
            matricula_data['fecha_emision'] = pd.to_datetime(matricula_data['fecha_emision'])
            
            # Calcular estadísticas específicas de matrículas basadas en trámites
            ingresos_diarios = matricula_data.groupby(matricula_data['fecha_emision'].dt.date)['ingresos_totales'].sum()
            tramites_diarios = matricula_data.groupby(matricula_data['fecha_emision'].dt.date)['num_tramites'].sum()
            
            total_ingresos = matricula_data['ingresos_totales'].sum()
            total_tramites = matricula_data['num_tramites'].sum()
            promedio_diario_tramites = tramites_diarios.mean()
            desv_std_diaria_tramites = tramites_diarios.std()
            
            # Mostrar estadísticas en formato limpio
            cols = st.columns(4)
            with cols[0]:
                st.metric("Ingresos totales", f"${total_ingresos:,.0f}")
            with cols[1]:
                st.metric("Trámites totales", f"{total_tramites:,}")
            with cols[2]:
                st.metric("Promedio diario", f"{promedio_diario_tramites:,.1f}")
            with cols[3]:
                st.metric("Desv. Std.", f"{desv_std_diaria_tramites:,.1f}")
        else:
            st.warning("No hay datos disponibles para estadísticas de matrículas")
            
    except Exception as e:
        st.error(f"Error calculando estadísticas de matrículas: {str(e)}")

def show_service_specific_stats(processor, service_name):
    """Muestra estadísticas específicas del servicio seleccionado"""
    try:
        if hasattr(processor, 'df') and processor.df is not None:
            # Filtrar datos del servicio
            service_data = processor.df[processor.df['servicio'] == service_name]
            
            if service_data.empty:
                st.warning("No hay datos para calcular estadísticas del servicio")
                return
            
            service_data['fecha_emision'] = pd.to_datetime(service_data['fecha_emision'])
            
            # Calcular estadísticas específicas del servicio basadas en trámites
            ingresos_diarios = service_data.groupby(service_data['fecha_emision'].dt.date)['ingresos_totales'].sum()
            tramites_diarios = service_data.groupby(service_data['fecha_emision'].dt.date)['num_tramites'].sum()
            
            total_ingresos = service_data['ingresos_totales'].sum()
            total_tramites = service_data['num_tramites'].sum()
            promedio_diario_tramites = tramites_diarios.mean()
            desv_std_diaria_tramites = tramites_diarios.std()
            
            # Mostrar estadísticas en formato limpio
            cols = st.columns(4)
            with cols[0]:
                st.metric("Ingresos totales", f"${total_ingresos:,.0f}")
            with cols[1]:
                st.metric("Trámites totales", f"{total_tramites:,}")
            with cols[2]:
                st.metric("Promedio diario", f"{promedio_diario_tramites:,.1f}")
            with cols[3]:
                st.metric("Desv. Std.", f"{desv_std_diaria_tramites:,.1f}")
        else:
            st.warning("No hay datos disponibles para estadísticas del servicio")
            
    except Exception as e:
        st.error(f"Error calculando estadísticas del servicio: {str(e)}")

def create_top_services_horizontal_chart(processor):
    """Crea gráfica de barras horizontales para top servicios con nombres cortos"""
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
            
            # Aplicar nombres cortos para visualización
            top_services_data['servicio_display'] = top_services_data['servicio'].apply(get_short_service_name)
            
            # Crear gráfica de barras horizontales
            fig = px.bar(
                top_services_data,
                x='num_tramites',
                y='servicio_display',
                orientation='h',
                title='Top 10 Servicios por Cantidad de Trámites',
                color='num_tramites',
                color_continuous_scale=[[0, '#D6E4F0'], [0.5, '#3A7CA5'], [1, '#2C4A6E']],
                hover_data={'servicio': True, 'servicio_display': False}  # Mostrar nombre original en hover
            )
            
            _apply_chart_theme(fig, height=500, title_size=15)
            fig.update_layout(showlegend=False, xaxis_title="Trámites", yaxis_title="",
                              coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0)
            
            # Ordenar de mayor a menor
            fig.update_yaxes(categoryorder="total ascending")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para top servicios")
        
    except Exception as e:
        st.error(f"Error en gráfica de top servicios: {str(e)}")

# Función show_detailed_data_section eliminada por solicitud del usuario

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
    
    # Indicadores principales
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
    """Muestra los Indicadores principales"""
    stats = processor.get_summary_stats()
    
    st.markdown("<h3 style='text-align: center;'>Indicadores del Período Seleccionado</h3>", unsafe_allow_html=True)
    
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
        # Eliminar métricas de mayor/menor actividad según solicitud
        
        # Tabla detallada por día de la semana
        st.markdown("**Estadísticas por día de la semana**")
        
        df_weekly = pd.DataFrame(weekly_stats['full_table'])
        df_weekly = df_weekly.round(2)
        
        # Ordenar por ingresos de mayor a menor
        df_weekly = df_weekly.sort_values('Ingresos Promedio', ascending=False)
        
        # Formatear columnas
        df_weekly['Ingresos Promedio'] = df_weekly['Ingresos Promedio'].apply(lambda x: f"${x:,.2f}")
        df_weekly['Trámites Promedio'] = df_weekly['Trámites Promedio'].apply(lambda x: f"{x:,.1f}")
        
        st.dataframe(
            df_weekly,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Día de la Semana": st.column_config.TextColumn("Día de la Semana", width="medium"),
                "Ingresos Promedio": st.column_config.TextColumn("Ingresos Promedio", width="medium"),
                "Trámites Promedio": st.column_config.TextColumn("Trámites Promedio", width="medium")
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
    st.markdown("# Configuración del Sistema")
    st.markdown("---")
    
    st.markdown("### Información del Sistema")
    
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
    st.markdown("### Acciones de Mantenimiento")
    
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

def export_dashboard_pdf(processor):
    """Exporta el dashboard principal a PDF con gráficas y estadísticas completas"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        import io
        from datetime import datetime
        import tempfile
        import plotly.io as pio
        import plotly.express as px
        import os
        
        # Configurar kaleido para plotly
        pio.kaleido.scope.mathjax = None
        
        # Lista para rastrear archivos temporales
        temp_files_to_cleanup = []
        
        # Crear buffer en memoria
        buffer = io.BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centro
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=1  # Centro
        )
        
        # Contenido del PDF
        story = []
        
        # Título en dos líneas
        story.append(Paragraph("Consulmex Kansas City", title_style))
        story.append(Paragraph("Estadísticas de documentación", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Fecha de generación
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        story.append(Paragraph(f"Generado el: {fecha_generacion}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if hasattr(processor, 'df') and processor.df is not None:
            df = processor.df.copy()
            df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
            
            # === INDICADORES GENERALES ===
            story.append(Paragraph("Indicadores Generales", styles['Heading2']))
            
            # Calcular métricas generales
            ingresos_diarios = df.groupby(df['fecha_emision'].dt.date)['ingresos_totales'].sum()
            total_ingresos = df['ingresos_totales'].sum()
            total_tramites = df['num_tramites'].sum()
            promedio_diario = ingresos_diarios.mean()
            desv_std_diaria = ingresos_diarios.std()
            
            # Tabla de Indicadores Generales
            general_data = [
                ['Métrica', 'Valor'],
                ['Ingresos Totales', f'${total_ingresos:,.2f}'],
                ['Trámites Totales', f'{total_tramites:,}'],
                ['Promedio Diario', f'${promedio_diario:.2f}'],
                ['Desv. Std. Diaria', f'${desv_std_diaria:.2f}']
            ]
            
            general_table = Table(general_data, colWidths=[2.5*inch, 2.5*inch])
            general_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(general_table)
            story.append(Spacer(1, 20))
            
            # === GRÁFICA DE INGRESOS ===
            story.append(Paragraph("Evolución de Ingresos", styles['Heading2']))
            
            # Crear gráfica de ingresos (mensual)
            df['year_month'] = df['fecha_emision'].dt.to_period('M')
            temporal_data = df.groupby('year_month').agg({
                'ingresos_totales': 'sum'
            }).reset_index()
            temporal_data['year_month'] = temporal_data['year_month'].astype(str)
            
            fig_ingresos = px.line(
                temporal_data,
                x='year_month',
                y='ingresos_totales',
                title='Evolución de Ingresos Mensual',
                markers=True
            )
            
            fig_ingresos.update_layout(
                width=600,
                height=400,
                showlegend=False,
                xaxis_title="Mes",
                yaxis_title="Ingresos USD",
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_x=0.5
            )
            
            fig_ingresos.update_traces(line_color='#1f77b4', line_width=2)
            
            # Guardar gráfica como imagen
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_filename = tmp_file.name
                    temp_files_to_cleanup.append(tmp_filename)
                
                pio.write_image(fig_ingresos, tmp_filename, format='png', width=600, height=400, scale=2)
                story.append(RLImage(tmp_filename, width=5*inch, height=3.33*inch))
            except Exception as e:
                st.warning(f"No se pudo generar gráfica de ingresos: {str(e)}")
            
            story.append(Spacer(1, 20))
            
            # === ESTADÍSTICAS ESPECÍFICAS LADO A LADO ===
            story.append(Paragraph("Estadísticas Específicas", styles['Heading2']))
            
            # Preparar datos para tabla combinada
            combined_stats_data = [
                ['Métrica', 'Pasaportes', 'Matrículas'],
            ]
            
            # Filtrar y calcular estadísticas de pasaportes
            passport_data = df[df['categoria'].str.contains('PASAPORTES', na=False)].copy()
            passport_stats = ['Sin datos', 'Sin datos', 'Sin datos', 'Sin datos']
            if not passport_data.empty:
                passport_tramites_diarios = passport_data.groupby(passport_data['fecha_emision'].dt.date)['num_tramites'].sum()
                passport_stats = [
                    f"${passport_data['ingresos_totales'].sum():,.2f}",
                    f"{passport_data['num_tramites'].sum():,}",
                    f"{passport_tramites_diarios.mean():,.1f} trámites/día",
                    f"{passport_tramites_diarios.std():,.1f} trámites"
                ]
            
            # Filtrar y calcular estadísticas de matrículas
            matricula_data = df[df['servicio'].str.contains('RCM|MATRÍCULA|MATRICULA', na=False, case=False)].copy()
            matricula_stats = ['Sin datos', 'Sin datos', 'Sin datos', 'Sin datos']
            if not matricula_data.empty:
                matricula_tramites_diarios = matricula_data.groupby(matricula_data['fecha_emision'].dt.date)['num_tramites'].sum()
                matricula_stats = [
                    f"${matricula_data['ingresos_totales'].sum():,.2f}",
                    f"{matricula_data['num_tramites'].sum():,}",
                    f"{matricula_tramites_diarios.mean():,.1f} trámites/día",
                    f"{matricula_tramites_diarios.std():,.1f} trámites"
                ]
            
            # Agregar filas a la tabla combinada
            metrics = ['Ingresos totales', 'Trámites totales', 'Promedio diario', 'Desv Std diaria']
            for i, metric in enumerate(metrics):
                combined_stats_data.append([metric, passport_stats[i], matricula_stats[i]])
            
            # Crear tabla combinada
            combined_table = Table(combined_stats_data, colWidths=[2*inch, 2*inch, 2*inch])
            combined_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(combined_table)
            story.append(Spacer(1, 20))
            
            
            # === GRÁFICAS DE PASAPORTES Y MATRÍCULAS (STACKED) ===
            story.append(Paragraph("Evolución de Pasaportes y Matrículas", styles['Heading2']))
            
            # Crear gráfica de pasaportes (mensual)
            passport_data = df[df['categoria'].str.contains('PASAPORTES', na=False)].copy()
            if not passport_data.empty:
                passport_data['year_month'] = passport_data['fecha_emision'].dt.to_period('M')
                passport_monthly = passport_data.groupby('year_month')['num_tramites'].sum().reset_index()
                passport_monthly['year_month'] = passport_monthly['year_month'].astype(str)
                
                fig_passport = px.line(
                    passport_monthly,
                    x='year_month',
                    y='num_tramites',
                    title='Número de Pasaportes (Mensual)',
                    markers=True
                )
                
                fig_passport.update_layout(
                    width=600,
                    height=350,
                    showlegend=False,
                    xaxis_title="Mes",
                    yaxis_title="Número de Trámites",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    title_x=0.5
                )
                
                fig_passport.update_traces(line_color='#1f77b4', line_width=2)
                
                # Guardar gráfica de pasaportes
                try:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_filename = tmp_file.name
                        temp_files_to_cleanup.append(tmp_filename)
                    
                    pio.write_image(fig_passport, tmp_filename, format='png', width=600, height=350, scale=2)
                    story.append(RLImage(tmp_filename, width=5*inch, height=2.92*inch))
                except Exception as e:
                    st.warning(f"No se pudo generar gráfica de pasaportes: {str(e)}")
                
                story.append(Spacer(1, 15))
            
            # Crear gráfica de matrículas (mensual)
            matricula_data = df[df['servicio'].str.contains('RCM|MATRÍCULA|MATRICULA', na=False, case=False)].copy()
            if not matricula_data.empty:
                matricula_data['year_month'] = matricula_data['fecha_emision'].dt.to_period('M')
                matricula_monthly = matricula_data.groupby('year_month')['num_tramites'].sum().reset_index()
                matricula_monthly['year_month'] = matricula_monthly['year_month'].astype(str)
                
                fig_matricula = px.line(
                    matricula_monthly,
                    x='year_month',
                    y='num_tramites',
                    title='Número de Matrículas (Mensual)',
                    markers=True
                )
                
                fig_matricula.update_layout(
                    width=600,
                    height=350,
                    showlegend=False,
                    xaxis_title="Mes",
                    yaxis_title="Número de Trámites",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    title_x=0.5
                )
                
                fig_matricula.update_traces(line_color='#ff7f0e', line_width=2)
                
                # Guardar gráfica de matrículas
                try:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_filename = tmp_file.name
                        temp_files_to_cleanup.append(tmp_filename)
                    
                    pio.write_image(fig_matricula, tmp_filename, format='png', width=600, height=350, scale=2)
                    story.append(RLImage(tmp_filename, width=5*inch, height=2.92*inch))
                except Exception as e:
                    st.warning(f"No se pudo generar gráfica de matrículas: {str(e)}")
                
                story.append(Spacer(1, 20))
            
            # === ANÁLISIS DE SERVICIO ESPECÍFICO ===
            # Solo incluir si hay un servicio seleccionado
            selected_service_display = st.session_state.get('servicio_especifico_new')
            analysis_unit = st.session_state.get('unidad_analisis', 'Cantidad')
            
            if selected_service_display and selected_service_display != "Seleccionar...":
                story.append(Paragraph("Análisis de Servicio Específico", styles['Heading2']))
                
                # Encontrar el servicio original desde el display name
                # Buscar en todos los servicios disponibles cuál coincide con el display name
                selected_service_original = None
                services_list = sorted(df['servicio'].unique().tolist())
                
                for service in services_list:
                    short_name = get_short_service_name(service)
                    display_name = f"{short_name}" if short_name != service else service
                    if display_name == selected_service_display:
                        selected_service_original = service
                        break
                
                # Si no encontramos mapeo, usar el display name directamente
                if not selected_service_original:
                    selected_service_original = selected_service_display
                
                # Filtrar datos del servicio específico usando el nombre original
                service_data = df[df['servicio'] == selected_service_original].copy()
                
                if not service_data.empty:
                    # Estadísticas del servicio específico
                    service_ingresos_diarios = service_data.groupby(service_data['fecha_emision'].dt.date)['ingresos_totales'].sum()
                    service_tramites_diarios = service_data.groupby(service_data['fecha_emision'].dt.date)['num_tramites'].sum()
                    
                    service_total_ingresos = service_data['ingresos_totales'].sum()
                    service_total_tramites = service_data['num_tramites'].sum()
                    service_promedio_diario_tramites = service_tramites_diarios.mean()
                    service_desv_std_diaria_tramites = service_tramites_diarios.std()
                    
                    # Información del servicio
                    service_short_name = get_short_service_name(selected_service_original)
                    story.append(Paragraph(f"Servicio analizado: <b>{service_short_name}</b>", styles['Normal']))
                    if service_short_name != selected_service_original:
                        story.append(Paragraph(f"Nombre completo: <i>{selected_service_original}</i>", styles['Normal']))
                    story.append(Paragraph(f"Unidad de análisis: <b>{analysis_unit}</b>", styles['Normal']))
                    story.append(Spacer(1, 10))
                    
                    # Tabla de estadísticas del servicio específico
                    service_stats_data = [
                        ['Métrica', 'Valor'],
                        ['Ingresos totales', f'${service_total_ingresos:,.2f}'],
                        ['Trámites totales', f'{service_total_tramites:,}'],
                        ['Promedio diario', f'{service_promedio_diario_tramites:,.1f} trámites/día'],
                        ['Desv Std diaria', f'{service_desv_std_diaria_tramites:,.1f} trámites']
                    ]
                    
                    service_stats_table = Table(service_stats_data, colWidths=[2.5*inch, 2.5*inch])
                    service_stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(service_stats_table)
                    story.append(Spacer(1, 15))
                    
                    # Crear gráfica del servicio específico (mensual)
                    service_data['year_month'] = service_data['fecha_emision'].dt.to_period('M')
                    service_temporal = service_data.groupby('year_month').agg({
                        'num_tramites': 'sum',
                        'ingresos_totales': 'sum'
                    }).reset_index()
                    service_temporal['year_month'] = service_temporal['year_month'].astype(str)
                    
                    # Elegir la columna según la unidad de análisis
                    y_column = 'num_tramites' if analysis_unit == 'Cantidad' else 'ingresos_totales'
                    y_label = 'Número de Trámites' if analysis_unit == 'Cantidad' else 'Ingresos USD'
                    
                    fig_service = px.line(
                        service_temporal,
                        x='year_month',
                        y=y_column,
                        title=f'{analysis_unit} - {service_short_name} (Vista Mensual)',
                        markers=True
                    )
                    
                    fig_service.update_layout(
                        width=600,
                        height=350,
                        showlegend=False,
                        xaxis_title="Mes",
                        yaxis_title=y_label,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        title_x=0.5
                    )
                    
                    fig_service.update_traces(line_color='#d62728', line_width=2)
                    
                    # Guardar gráfica del servicio específico
                    try:
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                            tmp_filename = tmp_file.name
                            temp_files_to_cleanup.append(tmp_filename)
                        
                        pio.write_image(fig_service, tmp_filename, format='png', width=600, height=350, scale=2)
                        story.append(RLImage(tmp_filename, width=5*inch, height=2.92*inch))
                    except Exception as e:
                        st.warning(f"No se pudo generar gráfica del servicio específico: {str(e)}")
                    
                    story.append(Spacer(1, 20))
                else:
                    story.append(Paragraph(f"No hay datos disponibles para el servicio: <b>{selected_service_display}</b>", styles['Normal']))
                    story.append(Spacer(1, 20))
            
            # === ESTADÍSTICAS SEMANALES ===
            weekly_stats = calculate_weekly_statistics_main(processor)
            if weekly_stats:
                story.append(Paragraph("Análisis por Día de la Semana", styles['Heading2']))
                
                # Tabla semanal
                weekly_table_data = [['Día de la Semana', 'Ingresos Promedio', 'Trámites Promedio']]
                
                # Ordenar por ingresos de mayor a menor
                sorted_weekly_data = sorted(weekly_stats['full_table'], key=lambda x: x['Ingresos Promedio'], reverse=True)
                
                for row in sorted_weekly_data:
                    weekly_table_data.append([
                        row['Día de la Semana'],
                        f"${row['Ingresos Promedio']:,.2f}",
                        f"{row['Trámites Promedio']:,.1f}"
                    ])
                
                weekly_table = Table(weekly_table_data, colWidths=[2*inch, 2*inch, 2*inch])
                weekly_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(weekly_table)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar descarga
        buffer.seek(0)
        pdf_filename = f"dashboard_consular_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        st.success("✅ PDF completo generado exitosamente")
        
        # Verificar si se incluyó análisis de servicio específico
        selected_service = st.session_state.get('servicio_especifico_new')
        if selected_service and selected_service != "Seleccionar...":
            st.info(f"El PDF incluye: Indicadores generales, gráfica de ingresos, estadísticas específicas de pasaportes/matrículas, evolución de pasaportes y matrículas, **análisis de servicio específico ({selected_service})**, y análisis semanal")
        else:
            st.info("El PDF incluye: Indicadores generales, gráfica de ingresos, estadísticas específicas de pasaportes/matrículas, evolución de pasaportes y matrículas, y análisis semanal")
        st.download_button(
            label="⬇️ Descargar PDF Completo",
            data=buffer.getvalue(),
            file_name=pdf_filename,
            mime="application/pdf"
        )
        
        # Limpiar archivos temporales creados para este PDF
        for temp_file in temp_files_to_cleanup:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except (PermissionError, FileNotFoundError, OSError):
                # Si no se puede eliminar, continuar sin error
                # Los archivos temporales se limpiarán automáticamente por el SO
                pass
        
    except Exception as e:
        st.error(f"Error generando PDF completo: {str(e)}")
        
        # Verificar si es un error de archivos temporales
        if "WinError 32" in str(e) or "PermissionError" in str(e):
            st.info("💡 Error de archivos temporales detectado. El PDF puede haberse generado correctamente.")
            st.info("Si el problema persiste, intente cerrar otros programas que puedan estar usando archivos temporales.")
        else:
            import traceback
            st.error(f"Detalles: {traceback.format_exc()}")
            st.info("Verifique que las dependencias estén instaladas: reportlab, matplotlib, kaleido")

if __name__ == "__main__":
    main()