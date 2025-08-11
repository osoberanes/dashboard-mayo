import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import MayoDataProcessor
from datetime import datetime, date
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Mayo - Análisis de Trámites",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Análisis - Mayo.xls")

# Inicializar el procesador de datos
@st.cache_data
def load_and_process_data():
    """Carga y procesa los datos dely
     archivo Excel"""
    try:
        processor = MayoDataProcessor("Inicio/mayo.xls")
        df = processor.load_data()
        df = processor.clean_data()
        return processor, df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None, None

# Cargar datos
processor, df = load_and_process_data()

if df is not None and not df.empty:
    
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de fechas
    min_date = df['fecha_emision'].min().date()
    max_date = df['fecha_emision'].max().date()
    
    fecha_inicio = st.sidebar.date_input(
        "Fecha inicio:",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    fecha_fin = st.sidebar.date_input(
        "Fecha fin:",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de categorías
    categorias_disponibles = processor.get_categories_list()
    categorias_seleccionadas = st.sidebar.multiselect(
        "Seleccionar Categorías:",
        options=categorias_disponibles,
        default=categorias_disponibles
    )
    
    # Filtro de servicios (dinámico basado en categorías)
    servicios_disponibles = []
    for cat in categorias_seleccionadas:
        servicios_cat = processor.get_services_list(cat)
        servicios_disponibles.extend(servicios_cat)
    
    servicios_seleccionados = st.sidebar.multiselect(
        "Seleccionar Servicios:",
        options=sorted(set(servicios_disponibles)),
        default=sorted(set(servicios_disponibles))
    )
    
    # Filtrar datos según selecciones
    df_filtrado = df[
        (df['fecha_emision'].dt.date >= fecha_inicio) &
        (df['fecha_emision'].dt.date <= fecha_fin) &
        (df['categoria'].isin(categorias_seleccionadas)) &
        (df['servicio'].isin(servicios_seleccionados))
    ]
    
    # Métricas principales (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ingresos = df_filtrado['ingresos_totales'].sum()
        st.metric(
            "💰 Ingresos Totales",
            f"${total_ingresos:,.2f}"
        )
    
    with col2:
        total_tramites = df_filtrado['num_tramites'].sum()
        st.metric(
            "📋 Trámites Realizados",
            f"{total_tramites:,}"
        )
    
    with col3:
        total_canceladas = df_filtrado['formas_canceladas'].sum()
        st.metric(
            "❌ Formas Canceladas",
            f"{total_canceladas:,}"
        )
    
    with col4:
        promedio_costo = df_filtrado['costo_unitario'].mean() if len(df_filtrado) > 0 else 0
        st.metric(
            "💵 Costo Promedio",
            f"${promedio_costo:.2f}"
        )
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Series Temporales", "📊 Por Categoría", "🔍 Por Servicio", "📋 Datos Detallados"])
    
    with tab1:
        st.subheader("Análisis Temporal")
        
        # Agrupación temporal
        periodo = st.selectbox(
            "Agrupar por:",
            ["Diario", "Mensual", "Anual"],
            index=1
        )
        
        if periodo == "Diario":
            df_temporal = df_filtrado.groupby('fecha_emision').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).reset_index()
        elif periodo == "Mensual":
            df_temporal = df_filtrado.groupby('mes_año').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).reset_index()
            df_temporal['fecha'] = df_temporal['mes_año'].astype(str)
        else:  # Anual
            df_temporal = df_filtrado.groupby('año').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).reset_index()
            df_temporal['fecha'] = df_temporal['año'].astype(str)
        
        # Gráfico de series temporales
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Ingresos', 'Trámites Realizados', 'Formas Canceladas'),
            vertical_spacing=0.08
        )
        
        x_col = 'fecha_emision' if periodo == "Diario" else 'fecha'
        
        fig.add_trace(
            go.Scatter(x=df_temporal[x_col], y=df_temporal['ingresos_totales'],
                      mode='lines+markers', name='Ingresos', line=dict(color='green')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df_temporal[x_col], y=df_temporal['num_tramites'],
                      mode='lines+markers', name='Trámites', line=dict(color='blue')),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df_temporal[x_col], y=df_temporal['formas_canceladas'],
                      mode='lines+markers', name='Canceladas', line=dict(color='red')),
            row=3, col=1
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Análisis por Categoría")
        
        df_categorias = df_filtrado.groupby('categoria').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum',
            'formas_canceladas': 'sum'
        }).reset_index().sort_values('ingresos_totales', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ingresos = px.bar(
                df_categorias, 
                x='categoria', 
                y='ingresos_totales',
                title='Ingresos por Categoría',
                color='ingresos_totales',
                color_continuous_scale='Greens'
            )
            fig_ingresos.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_ingresos, use_container_width=True)
        
        with col2:
            fig_tramites = px.bar(
                df_categorias,
                x='categoria',
                y='num_tramites',
                title='Trámites por Categoría',
                color='num_tramites',
                color_continuous_scale='Blues'
            )
            fig_tramites.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tramites, use_container_width=True)
        
        # Pie chart para distribución de ingresos
        fig_pie = px.pie(
            df_categorias,
            values='ingresos_totales',
            names='categoria',
            title='Distribución de Ingresos por Categoría'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        st.subheader("Análisis por Servicio")
        
        # Selector de categoría para drill-down
        categoria_drill = st.selectbox(
            "Seleccionar categoría para detalle:",
            options=['Todas'] + categorias_seleccionadas
        )
        
        if categoria_drill == 'Todas':
            df_servicios = df_filtrado.groupby(['categoria', 'servicio']).agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).reset_index()
        else:
            df_servicios = df_filtrado[df_filtrado['categoria'] == categoria_drill].groupby('servicio').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).reset_index()
        
        df_servicios = df_servicios.sort_values('ingresos_totales', ascending=True).tail(20)
        
        fig_servicios = px.bar(
            df_servicios,
            x='ingresos_totales',
            y='servicio',
            orientation='h',
            title=f'Top 20 Servicios por Ingresos - {categoria_drill}',
            color='ingresos_totales',
            color_continuous_scale='Viridis'
        )
        fig_servicios.update_layout(height=600)
        st.plotly_chart(fig_servicios, use_container_width=True)
    
    with tab4:
        st.subheader("Datos Detallados")
        
        # Opciones de agrupación
        agrupacion = st.selectbox(
            "Nivel de agrupación:",
            ["Sin agrupar", "Por Categoría", "Por Servicio", "Por Fecha"]
        )
        
        if agrupacion == "Sin agrupar":
            df_mostrar = df_filtrado[['fecha_emision', 'categoria', 'servicio', 
                                    'costo_unitario', 'num_tramites', 'ingresos_totales', 
                                    'formas_canceladas']].copy()
        elif agrupacion == "Por Categoría":
            df_mostrar = df_filtrado.groupby('categoria').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum',
                'costo_unitario': 'mean'
            }).round(2).reset_index()
        elif agrupacion == "Por Servicio":
            df_mostrar = df_filtrado.groupby(['categoria', 'servicio']).agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum',
                'costo_unitario': 'mean'
            }).round(2).reset_index()
        else:  # Por Fecha
            df_mostrar = df_filtrado.groupby('fecha_emision').agg({
                'ingresos_totales': 'sum',
                'num_tramites': 'sum',
                'formas_canceladas': 'sum'
            }).round(2).reset_index()
        
        st.dataframe(df_mostrar, use_container_width=True)
        
        # Botón para descargar datos
        csv = df_mostrar.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos como CSV",
            data=csv,
            file_name=f'datos_mayo_{agrupacion.lower().replace(" ", "_")}.csv',
            mime='text/csv'
        )

else:
    st.error("No se pudo cargar el archivo mayo.xls. Asegúrate de que el archivo existe en el directorio actual.")
    st.info("Estructura esperada del archivo:")
    st.write("""
    - Columna A: Servicios
    - Columna C: Categorías
    - Columna D: Costo unitario
    - Columna E: Número de trámites
    - Columna F: Ingresos totales (D*E)
    - Columna J: Fecha de emisión (DD/MM/AAAA)
    - Columna M: Formas canceladas
    """)