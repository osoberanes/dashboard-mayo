import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from service_grouping_manager import ServiceGroupingManager
from datetime import date, datetime

def show_service_grouping_page():
    """Página para gestionar y visualizar agrupaciones de servicios"""
    st.markdown("<h1 style='text-align: center;'>Agrupación de Servicios</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    manager = ServiceGroupingManager()
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "Análisis de Agrupaciones", 
        "Desglose Detallado", 
        "Aplicar Cambios",
        "Comparación"
    ])
    
    with tab1:
        show_grouping_analysis_tab(manager)
    
    with tab2:
        show_detailed_breakdown_tab(manager)
    
    with tab3:
        show_apply_changes_tab(manager)
    
    with tab4:
        show_comparison_tab(manager)

def show_grouping_analysis_tab(manager):
    """Tab de análisis general de agrupaciones"""
    st.markdown("<h2 style='text-align: center;'>Análisis de Servicios Agrupables</h2>", unsafe_allow_html=True)
    
    with st.spinner("Analizando servicios..."):
        analysis = manager.analyze_groupable_services()
    
    if not analysis:
        st.warning("No se encontraron servicios agrupables")
        return
    
    # Resumen general
    st.markdown("<h3 style='text-align: center;'>Resumen General</h3>", unsafe_allow_html=True)
    
    total_services_to_group = sum(data['totals']['total_services'] for data in analysis.values())
    total_records_to_group = sum(data['totals']['total_records'] for data in analysis.values())
    total_tramites_grouped = sum(data['totals']['total_tramites'] for data in analysis.values())
    total_ingresos_grouped = sum(data['totals']['total_ingresos'] for data in analysis.values())
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Servicios Únicos", total_services_to_group)
    with col2:
        st.metric("Registros Total", total_records_to_group)
    with col3:
        st.metric("Trámites", f"{total_tramites_grouped:,}")
    with col4:
        st.metric("Ingresos", f"${total_ingresos_grouped:,.2f}")
    
    # Análisis por grupo
    for group_key, data in analysis.items():
        rule = data['rule']
        totals = data['totals']
        
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: center;'>{rule['grouped_name']}</h3>", unsafe_allow_html=True)
        st.caption(rule['description'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Servicios Únicos",
                totals['total_services'],
                help="Cantidad de servicios diferentes que serán agrupados"
            )
        with col2:
            st.metric(
                "Trámites Totales",
                f"{totals['total_tramites']:,}",
                help="Total de trámites procesados"
            )
        with col3:
            st.metric(
                "Ingresos Totales",
                f"${totals['total_ingresos']:,.2f}",
                help="Ingresos generados por estos servicios"
            )
        
        # Gráfico de top servicios del grupo
        breakdown = data['breakdown'].nlargest(10, 'ingresos_total')
        
        if not breakdown.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top 10 por Ingresos**")
                fig_ingresos = px.bar(
                    breakdown,
                    x='ingresos_total',
                    y='servicio',
                    orientation='h',
                    title=f'Ingresos - {rule["grouped_name"]}',
                    labels={'ingresos_total': 'Ingresos ($)', 'servicio': 'Servicio'},
                    height=400
                )
                fig_ingresos.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_ingresos, use_container_width=True)
            
            with col2:
                st.markdown("**Top 10 por Trámites**")
                fig_tramites = px.bar(
                    breakdown,
                    x='tramites_total',
                    y='servicio',
                    orientation='h',
                    title=f'Trámites - {rule["grouped_name"]}',
                    labels={'tramites_total': 'Trámites', 'servicio': 'Servicio'},
                    color='tramites_total',
                    color_continuous_scale='Viridis',
                    height=400
                )
                fig_tramites.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_tramites, use_container_width=True)
        
        # Muestra de servicios
        st.markdown("**Ejemplos de Servicios a Agrupar:**")
        sample_services = data['sample_services'][:5]  # Mostrar solo los primeros 5
        for service in sample_services:
            st.write(f"• {service}")
        
        if len(data['sample_services']) > 5:
            with st.expander(f"Ver todos los {totals['total_services']} servicios"):
                for service in data['breakdown']['servicio']:
                    st.write(f"• {service}")

def show_detailed_breakdown_tab(manager):
    """Tab para desglose detallado de grupos específicos"""
    st.markdown("<h2 style='text-align: center;'>Desglose Detallado por Grupo</h2>", unsafe_allow_html=True)
    
    # Selector de grupo
    group_options = {
        'RCM - Expedición Diaria': 'RCM - Expedición Diaria',
        'Pasaportes Ordinarios': 'Pasaportes Ordinarios'
    }
    
    selected_group = st.selectbox(
        "Seleccionar grupo para análisis detallado:",
        options=list(group_options.keys()),
        key="detailed_group_selector"
    )
    
    if selected_group:
        group_name = group_options[selected_group]
        
        # Filtros de fecha
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("📅 Fecha inicio", key="breakdown_start")
        with col2:
            end_date = st.date_input("📅 Fecha fin", key="breakdown_end")
        
        # Obtener desglose
        start_str = start_date.strftime('%Y-%m-%d') if start_date else None
        end_str = end_date.strftime('%Y-%m-%d') if end_date else None
        
        with st.spinner(f"Analizando {selected_group}..."):
            breakdown_df = manager.get_grouping_breakdown(group_name, start_str, end_str)
        
        if breakdown_df.empty:
            st.warning(f"No se encontraron datos para {selected_group}")
            return
        
        # KPIs del grupo
        st.markdown(f"<h3 style='text-align: center;'>KPIs - {selected_group}</h3>", unsafe_allow_html=True)
        
        total_servicios = len(breakdown_df)
        total_tramites = breakdown_df['num_tramites'].sum()
        total_ingresos = breakdown_df['ingresos_totales'].sum()
        total_canceladas = breakdown_df['formas_canceladas'].sum()
        promedio_ingreso_servicio = total_ingresos / total_servicios if total_servicios > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Servicios", total_servicios)
        with col2:
            st.metric("Trámites", f"{total_tramites:,}")
        with col3:
            st.metric("Ingresos", f"${total_ingresos:,.2f}")
        with col4:
            st.metric("Canceladas", f"{total_canceladas:,}")
        with col5:
            st.metric("Promedio/Servicio", f"${promedio_ingreso_servicio:,.2f}")
        
        # Visualizaciones
        st.markdown("<h3 style='text-align: center;'>Visualizaciones</h3>", unsafe_allow_html=True)
        
        tab_viz1, tab_viz2, tab_viz3 = st.tabs(["Por Ingresos", "Por Trámites", "Temporal"])
        
        with tab_viz1:
            # Top servicios por ingresos
            top_ingresos = breakdown_df.nlargest(15, 'ingresos_totales')
            
            fig_tree = px.treemap(
                top_ingresos,
                path=['servicio'],
                values='ingresos_totales',
                title=f'Distribución de Ingresos - {selected_group}',
                color='ingresos_totales',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        
        with tab_viz2:
            # Top servicios por trámites
            top_tramites = breakdown_df.nlargest(15, 'num_tramites')
            
            fig_pie = px.pie(
                top_tramites,
                values='num_tramites',
                names='servicio',
                title=f'Distribución de Trámites - {selected_group}',
                height=600
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab_viz3:
            # Análisis temporal por días activos
            fig_temporal = px.scatter(
                breakdown_df,
                x='dias_activo',
                y='ingresos_totales',
                size='num_tramites',
                hover_data=['servicio', 'total_registros'],
                title=f'Días Activos vs Ingresos - {selected_group}',
                labels={
                    'dias_activo': 'Días Activo',
                    'ingresos_totales': 'Ingresos Totales ($)'
                }
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Tabla detallada
        st.subheader("Tabla Detallada")
        
        # Permitir filtrado de la tabla
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            min_ingresos = st.number_input("Ingresos mínimos ($)", min_value=0.0, value=0.0, key="min_ingresos_filter")
        with filter_col2:
            min_tramites = st.number_input("Trámites mínimos", min_value=0, value=0, key="min_tramites_filter")
        
        # Aplicar filtros
        filtered_df = breakdown_df[
            (breakdown_df['ingresos_totales'] >= min_ingresos) &
            (breakdown_df['num_tramites'] >= min_tramites)
        ].copy()
        
        # Agregar columnas calculadas
        filtered_df['ingreso_por_tramite'] = filtered_df['ingresos_totales'] / filtered_df['num_tramites']
        filtered_df['tasa_cancelacion'] = (filtered_df['formas_canceladas'] / filtered_df['num_tramites']) * 100
        
        # Formatear para visualización
        display_df = filtered_df[['servicio', 'num_tramites', 'ingresos_totales', 'formas_canceladas', 
                                'dias_activo', 'ingreso_por_tramite', 'tasa_cancelacion', 'total_registros']].copy()
        
        # Renombrar columnas para mejor visualización
        display_df.columns = ['Servicio', 'Trámites', 'Ingresos ($)', 'Canceladas', 
                             'Días Activo', 'Ingreso/Trámite ($)', 'Tasa Cancel. (%)', 'Registros']
        
        st.dataframe(
            display_df.round(2),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ingresos ($)": st.column_config.NumberColumn("Ingresos ($)", format="$%.2f"),
                "Ingreso/Trámite ($)": st.column_config.NumberColumn("Ingreso/Trámite ($)", format="$%.2f"),
                "Tasa Cancel. (%)": st.column_config.NumberColumn("Tasa Cancel. (%)", format="%.1f%%")
            }
        )
        
        st.caption(f"Mostrando {len(display_df)} de {len(breakdown_df)} servicios")

def show_apply_changes_tab(manager):
    """Tab para aplicar las agrupaciones a la base de datos"""
    st.markdown("<h2 style='text-align: center;'>Aplicar Agrupaciones a la Base de Datos</h2>", unsafe_allow_html=True)
    
    st.warning("**ATENCIÓN**: Esta operación modificará permanentemente los datos en la base de datos.")
    
    # Vista previa de cambios
    st.subheader("Vista Previa de Cambios")
    
    with st.spinner("Generando vista previa..."):
        preview = manager.get_grouping_preview()
    
    if preview:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Agrupación RCM**")
            rcm_info = preview['rcm_grouping']
            st.info(f"**Nuevo nombre**: {rcm_info['new_name']}")
            st.metric("Registros afectados", f"{rcm_info['records_affected']:,}")
            
            with st.expander(f"Ver {len(rcm_info['current_services'])} servicios RCM"):
                for service in rcm_info['current_services']:
                    st.write(f"• {service}")
        
        with col2:
            st.markdown("**Agrupación Pasaportes**")
            pass_info = preview['pasaportes_grouping']
            st.info(f"**Nuevo nombre**: {pass_info['new_name']}")
            st.metric("Registros afectados", f"{pass_info['records_affected']:,}")
            
            with st.expander(f"Ver {len(pass_info['current_services'])} servicios de Pasaportes"):
                for service in pass_info['current_services']:
                    st.write(f"• {service}")
        
        # Resumen total
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Resumen Total de Cambios</h3>", unsafe_allow_html=True)
        st.error(f"**TOTAL DE REGISTROS A MODIFICAR**: {preview['total_records_affected']:,}")
        
        # Controles de confirmación
        st.subheader("Confirmación de Aplicación")
        
        st.markdown("""
        **Antes de aplicar los cambios, asegúrese de:**
        1. Tener un backup de la base de datos
        2. Entender que esta operación es irreversible
        3. Haber revisado la vista previa de cambios
        """)
        
        # Checkboxes de confirmación
        confirm1 = st.checkbox("He revisado la vista previa de cambios")
        confirm2 = st.checkbox("Entiendo que esta operación es irreversible")
        confirm3 = st.checkbox("Tengo un backup de la base de datos")
        confirm4 = st.checkbox("Confirmo que quiero aplicar las agrupaciones")
        
        all_confirmed = all([confirm1, confirm2, confirm3, confirm4])
        
        # Botón de aplicación
        if all_confirmed:
            st.markdown("---")
            if st.button("**APLICAR AGRUPACIONES PERMANENTEMENTE**", type="primary"):
                with st.spinner("Aplicando agrupaciones..."):
                    result = manager.apply_permanent_grouping(confirm=True)
                
                if result['success']:
                    st.success(result['message'])
                    st.balloons()
                    
                    details = result['details']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("RCM Actualizados", details['rcm_updated'])
                    with col2:
                        st.metric("Pasaportes Actualizados", details['pasaportes_updated'])
                    with col3:
                        st.metric("Total Actualizados", details['total_updated'])
                    
                    st.info("Los cambios se han aplicado. Refresque el dashboard principal para ver los resultados.")
                else:
                    st.error(result['message'])
        else:
            st.info("Complete todas las confirmaciones para habilitar la aplicación de cambios")

def show_comparison_tab(manager):
    """Tab para comparar datos antes y después de agrupación"""
    st.markdown("<h2 style='text-align: center;'>Comparación: Original vs Agrupado</h2>", unsafe_allow_html=True)
    
    # Obtener datos originales
    original_data = manager.db_manager.get_all_data()
    
    # Obtener datos agrupados (vista temporal)
    grouped_data = manager.get_grouped_data()
    
    if original_data.empty or grouped_data.empty:
        st.warning("No se pueden generar comparaciones")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='text-align: center;'>Vista Original</h3>", unsafe_allow_html=True)
        
        # Top servicios originales
        original_services = original_data.groupby('servicio').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        }).nlargest(20, 'ingresos_totales').reset_index()
        
        st.metric("Servicios Únicos", original_data['servicio'].nunique())
        
        fig_original = px.bar(
            original_services.head(10),
            x='ingresos_totales',
            y='servicio',
            orientation='h',
            title='Top 10 Servicios (Original)',
            labels={'ingresos_totales': 'Ingresos ($)', 'servicio': 'Servicio'},
            height=500
        )
        fig_original.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_original, use_container_width=True)
    
    with col2:
        st.subheader("Vista Agrupada")
        
        # Top servicios agrupados
        grouped_services = grouped_data.groupby('servicio').agg({
            'ingresos_totales': 'sum',
            'num_tramites': 'sum'
        }).nlargest(20, 'ingresos_totales').reset_index()
        
        st.metric("Servicios Únicos", grouped_data['servicio'].nunique())
        
        fig_grouped = px.bar(
            grouped_services.head(10),
            x='ingresos_totales',
            y='servicio',
            orientation='h',
            title='Top 10 Servicios (Agrupado)',
            labels={'ingresos_totales': 'Ingresos ($)', 'servicio': 'Servicio'},
            color='ingresos_totales',
            color_continuous_scale='Viridis',
            height=500
        )
        fig_grouped.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_grouped, use_container_width=True)
    
    # Comparación estadística
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Estadísticas Comparativas</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        original_services_count = original_data['servicio'].nunique()
        grouped_services_count = grouped_data['servicio'].nunique()
        reduction = original_services_count - grouped_services_count
        st.metric(
            "Reducción de Servicios", 
            f"{reduction}",
            delta=f"-{(reduction/original_services_count)*100:.1f}%"
        )
    
    with col2:
        st.metric("Servicios Originales", original_services_count)
    
    with col3:
        st.metric("Servicios Agrupados", grouped_services_count)
    
    with col4:
        consolidation_rate = (reduction / original_services_count) * 100
        st.metric("Tasa Consolidación", f"{consolidation_rate:.1f}%")