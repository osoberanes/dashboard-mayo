import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from enhanced_data_processor import EnhancedDataProcessor
from service_name_mappings import get_short_service_name
from datetime import datetime, timedelta
import calendar
import numpy as np
import plotly.io as pio
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import tempfile
import os

def show_monthly_report_page():
    """Página principal para generar reportes mensuales de expedición de documentos"""
    st.markdown("<h1 style='text-align: center;'>📊 Reporte Mensual de Expedición</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1.5rem;'>
        <h3 style='color: #2C3E50; margin-bottom: 0.5rem;'>Análisis Mensual de Servicios Consulares</h3>
        <p style='color: #7F8C8D; margin: 0;'>
            Genera reportes detallados con comparativas del mes anterior y mismo mes del año anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Inicializar procesador
    processor = initialize_processor()

    if processor is None:
        st.error("No se pudieron cargar los datos. Verifique que existan datos en la base de datos.")
        st.info("💡 Vaya a la página de 'Gestión de Archivos' para cargar datos.")
        return

    # Obtener meses y años disponibles
    available_periods = get_available_periods(processor)

    if not available_periods:
        st.error("No se pudieron obtener los períodos disponibles en la base de datos")
        return

    # Selector de período
    st.markdown("<h3 style='text-align: center;'>Seleccionar Período del Reporte</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        selected_month = st.selectbox(
            "Mes:",
            options=list(range(1, 13)),
            format_func=lambda x: calendar.month_name[x],
            index=datetime.now().month - 1,
            key="report_month"
        )

    with col2:
        selected_year = st.selectbox(
            "Año:",
            options=sorted(available_periods['years'], reverse=True),
            index=0,
            key="report_year"
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🔍 Generar Reporte", type="primary", use_container_width=True)

    # Generar reporte
    if generate_button or 'current_report_data' in st.session_state:
        if generate_button:
            with st.spinner("Generando reporte..."):
                report_data = generate_monthly_report(processor, selected_year, selected_month)

                if report_data:
                    st.session_state.current_report_data = report_data
                    st.session_state.report_config = {
                        'year': selected_year,
                        'month': selected_month,
                        'month_name': calendar.month_name[selected_month]
                    }
                else:
                    st.error(f"No se encontraron datos para {calendar.month_name[selected_month]} {selected_year}")
                    return

        # Mostrar reporte si existe en session_state
        if 'current_report_data' in st.session_state:
            display_monthly_report(
                st.session_state.current_report_data,
                st.session_state.report_config,
                processor
            )

def initialize_processor():
    """Inicializa el procesador de datos"""
    try:
        processor = EnhancedDataProcessor()
        if processor.initialize_from_database():
            if processor.df is not None and not processor.df.empty:
                processor.df['fecha_emision'] = pd.to_datetime(processor.df['fecha_emision'])
                return processor
        return None
    except Exception as e:
        st.error(f"Error inicializando procesador: {str(e)}")
        return None

def get_available_periods(processor):
    """Obtiene los períodos (años y meses) disponibles en la base de datos"""
    try:
        if processor.df is None or processor.df.empty:
            return None

        df = processor.df.copy()
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])

        years = sorted(df['fecha_emision'].dt.year.unique().tolist())
        months_by_year = {}

        for year in years:
            year_data = df[df['fecha_emision'].dt.year == year]
            months = sorted(year_data['fecha_emision'].dt.month.unique().tolist())
            months_by_year[year] = months

        return {
            'years': years,
            'months_by_year': months_by_year,
            'min_date': df['fecha_emision'].min(),
            'max_date': df['fecha_emision'].max()
        }
    except Exception as e:
        st.error(f"Error obteniendo períodos: {str(e)}")
        return None

def generate_monthly_report(processor, year, month):
    """Genera los datos del reporte mensual con comparativas"""
    try:
        if processor.df is None or processor.df.empty:
            return None

        df = processor.df.copy()
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])

        # Datos del mes actual
        current_month_data = df[
            (df['fecha_emision'].dt.year == year) &
            (df['fecha_emision'].dt.month == month)
        ]

        if current_month_data.empty:
            return None

        # Calcular mes anterior
        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year

        prev_month_data = df[
            (df['fecha_emision'].dt.year == prev_year) &
            (df['fecha_emision'].dt.month == prev_month)
        ]

        # Calcular mismo mes año anterior
        same_month_prev_year_data = df[
            (df['fecha_emision'].dt.year == year - 1) &
            (df['fecha_emision'].dt.month == month)
        ]

        # Agrupar por servicio
        current_summary = current_month_data.groupby('servicio').agg({
            'num_tramites': 'sum',
            'ingresos_totales': 'sum'
        }).reset_index()

        # Aplicar nombres cortos
        current_summary['servicio_corto'] = current_summary['servicio'].apply(get_short_service_name)

        prev_month_summary = prev_month_data.groupby('servicio').agg({
            'num_tramites': 'sum',
            'ingresos_totales': 'sum'
        }).reset_index() if not prev_month_data.empty else pd.DataFrame()

        if not prev_month_summary.empty:
            prev_month_summary['servicio_corto'] = prev_month_summary['servicio'].apply(get_short_service_name)

        prev_year_summary = same_month_prev_year_data.groupby('servicio').agg({
            'num_tramites': 'sum',
            'ingresos_totales': 'sum'
        }).reset_index() if not same_month_prev_year_data.empty else pd.DataFrame()

        if not prev_year_summary.empty:
            prev_year_summary['servicio_corto'] = prev_year_summary['servicio'].apply(get_short_service_name)

        return {
            'current_month': current_summary,
            'prev_month': prev_month_summary,
            'prev_year': prev_year_summary,
            'current_data_raw': current_month_data,
            'prev_month_data_raw': prev_month_data,
            'prev_year_data_raw': same_month_prev_year_data
        }

    except Exception as e:
        st.error(f"Error generando reporte: {str(e)}")
        return None

def display_monthly_report(report_data, config, processor):
    """Muestra el reporte mensual completo"""

    month_name = config['month_name']
    year = config['year']
    month = config['month']

    st.markdown("---")
    st.markdown(f"<h2 style='text-align: center;'>Reporte: {month_name} {year}</h2>", unsafe_allow_html=True)

    # KPIs Generales
    show_monthly_kpis(report_data, config)

    st.markdown("---")

    # Tabla principal de servicios
    st.markdown("<h3 style='text-align: center;'>📋 Servicios Expedidos en el Mes</h3>", unsafe_allow_html=True)
    show_services_table(report_data['current_month'])

    st.markdown("---")

    # Tabla de comparación de recaudación total
    st.markdown("<h3 style='text-align: center;'>💰 Comparativa de Recaudación Total</h3>", unsafe_allow_html=True)
    show_revenue_comparative_table(report_data, config)

    st.markdown("---")

    # Tabla comparativa de trámites por servicio
    st.markdown("<h3 style='text-align: center;'>📊 Comparativa de Trámites por Servicio</h3>", unsafe_allow_html=True)
    show_comparative_table(report_data, config)

    st.markdown("---")

    # Botón de exportación
    show_pdf_export_section(report_data, config)

def show_monthly_kpis(report_data, config):
    """Muestra KPIs generales del mes"""
    current = report_data['current_month']

    total_tramites = current['num_tramites'].sum()
    total_ingresos = current['ingresos_totales'].sum()
    num_servicios = len(current)
    promedio_ingreso = total_ingresos / max(total_tramites, 1)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Ingresos Totales",
            value=f"${total_ingresos:,.2f}"
        )

    with col2:
        st.metric(
            label="📝 Trámites Realizados",
            value=f"{total_tramites:,}"
        )

    with col3:
        st.metric(
            label="🏷️ Servicios Activos",
            value=f"{num_servicios}"
        )

    with col4:
        st.metric(
            label="💵 Ingreso Promedio/Trámite",
            value=f"${promedio_ingreso:,.2f}"
        )

def show_services_table(current_data):
    """Muestra tabla de servicios del mes actual"""
    if current_data.empty:
        st.warning("No hay datos para mostrar")
        return

    # Ordenar por ingresos
    display_data = current_data.copy()
    display_data = display_data.sort_values('ingresos_totales', ascending=False)

    # Formatear para display usando nombres cortos
    display_data['Servicio'] = display_data['servicio_corto']
    display_data['Cantidad'] = display_data['num_tramites'].apply(lambda x: f"{int(x):,}")
    display_data['Ingresos Totales'] = display_data['ingresos_totales'].apply(lambda x: f"${x:,.2f}")
    display_data['Ingreso Promedio'] = (display_data['ingresos_totales'] / display_data['num_tramites']).apply(lambda x: f"${x:,.2f}")

    # Mostrar solo columnas relevantes
    st.dataframe(
        display_data[['Servicio', 'Cantidad', 'Ingresos Totales', 'Ingreso Promedio']],
        use_container_width=True,
        hide_index=True
    )

def show_revenue_comparative_table(report_data, config):
    """Muestra tabla comparativa de RECAUDACIÓN TOTAL con mes anterior y año anterior"""
    current = report_data['current_month']
    prev_month = report_data['prev_month']
    prev_year = report_data['prev_year']

    if current.empty:
        st.warning("No hay datos del mes actual")
        return

    # Calcular totales
    ingresos_actual = current['ingresos_totales'].sum()
    ingresos_mes_ant = prev_month['ingresos_totales'].sum() if not prev_month.empty else 0
    ingresos_año_ant = prev_year['ingresos_totales'].sum() if not prev_year.empty else 0

    # Calcular cambios porcentuales
    cambio_mes = calculate_percentage_change(ingresos_actual, ingresos_mes_ant)
    cambio_año = calculate_percentage_change(ingresos_actual, ingresos_año_ant)

    # Calcular nombres de períodos
    if config['month'] == 1:
        prev_month_name = f"Diciembre {config['year'] - 1}"
    else:
        prev_month_name = f"{calendar.month_name[config['month'] - 1]} {config['year']}"

    prev_year_name = f"{config['month_name']} {config['year'] - 1}"

    # Crear tabla HTML con colores
    table_html = f"""
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead style="background-color: #2E86C1; color: white;">
            <tr>
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Período</th>
                <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Recaudación Total</th>
                <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">% Cambio</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">{config['month_name']} {config['year']}</td>
                <td style="padding: 12px; text-align: right; border: 1px solid #ddd; font-weight: bold;">${ingresos_actual:,.2f}</td>
                <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">-</td>
            </tr>
            <tr style="background-color: white;">
                <td style="padding: 12px; border: 1px solid #ddd;">{prev_month_name}</td>
                <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">${ingresos_mes_ant:,.2f}</td>
                <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{format_percentage_with_arrow_colored(cambio_mes)}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #ddd;">{prev_year_name}</td>
                <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">${ingresos_año_ant:,.2f}</td>
                <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{format_percentage_with_arrow_colored(cambio_año)}</td>
            </tr>
        </tbody>
    </table>
    """

    st.markdown(table_html, unsafe_allow_html=True)

def show_comparative_table(report_data, config):
    """Muestra tabla comparativa de NÚMERO DE TRÁMITES con mes anterior y año anterior"""
    current = report_data['current_month']
    prev_month = report_data['prev_month']
    prev_year = report_data['prev_year']

    if current.empty:
        st.warning("No hay datos del mes actual")
        return

    # Crear tabla comparativa basada en TRÁMITES
    comparison = current.copy()
    comparison = comparison.rename(columns={
        'num_tramites': 'tramites_actual',
        'ingresos_totales': 'ingresos_actual'
    })

    # Merge con mes anterior
    if not prev_month.empty:
        prev_month_data = prev_month[['servicio', 'num_tramites']].copy()
        prev_month_data = prev_month_data.rename(columns={
            'num_tramites': 'tramites_mes_ant'
        })
        comparison = comparison.merge(prev_month_data, on='servicio', how='left')
    else:
        comparison['tramites_mes_ant'] = 0

    # Merge con año anterior
    if not prev_year.empty:
        prev_year_data = prev_year[['servicio', 'num_tramites']].copy()
        prev_year_data = prev_year_data.rename(columns={
            'num_tramites': 'tramites_año_ant'
        })
        comparison = comparison.merge(prev_year_data, on='servicio', how='left')
    else:
        comparison['tramites_año_ant'] = 0

    # Llenar NaN con 0
    comparison['tramites_mes_ant'] = comparison['tramites_mes_ant'].fillna(0)
    comparison['tramites_año_ant'] = comparison['tramites_año_ant'].fillna(0)

    # Calcular cambios porcentuales basados en TRÁMITES
    comparison['cambio_mes_ant'] = comparison.apply(
        lambda row: calculate_percentage_change(row['tramites_actual'], row['tramites_mes_ant']),
        axis=1
    )

    comparison['cambio_año_ant'] = comparison.apply(
        lambda row: calculate_percentage_change(row['tramites_actual'], row['tramites_año_ant']),
        axis=1
    )

    # Ordenar por número de trámites actuales
    comparison = comparison.sort_values('tramites_actual', ascending=False)

    # Formatear para display con NOMBRES CORTOS y COLORES
    display_df = pd.DataFrame({
        'Servicio': comparison['servicio_corto'],
        'Trámites Actual': comparison['tramites_actual'].apply(lambda x: f"{int(x):,}"),
        'Mes Anterior': comparison['tramites_mes_ant'].apply(lambda x: f"{int(x):,}"),
        '% Cambio Mes': comparison['cambio_mes_ant'].apply(format_percentage_with_arrow_colored),
        f'{config["month_name"]} {config["year"]-1}': comparison['tramites_año_ant'].apply(lambda x: f"{int(x):,}"),
        '% Cambio Año': comparison['cambio_año_ant'].apply(format_percentage_with_arrow_colored)
    })

    # Mostrar con HTML habilitado para colores
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Guardar datos para PDF
    if 'comparison_data' not in st.session_state:
        st.session_state.comparison_data = {}
    st.session_state.comparison_data = comparison

def calculate_percentage_change(current, previous):
    """Calcula el cambio porcentual entre dos valores"""
    if pd.isna(previous) or previous == 0:
        return np.nan if pd.isna(current) or current == 0 else 100.0
    return ((current - previous) / previous) * 100

def format_percentage_with_arrow_colored(value):
    """Formatea el porcentaje con flecha indicadora y colores HTML"""
    if pd.isna(value):
        return '<span style="color: gray;">N/A</span>'

    if value > 0:
        color = "green"
        arrow = "↑"
    elif value < 0:
        color = "red"
        arrow = "↓"
    else:
        color = "gray"
        arrow = "→"

    return f'<span style="color: {color}; font-weight: bold;">{value:+.1f}% {arrow}</span>'

def show_pdf_export_section(report_data, config):
    """Muestra sección de exportación a PDF"""
    st.markdown("<h3 style='text-align: center;'>📄 Exportar Reporte</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("📥 Generar y Descargar PDF", type="primary", use_container_width=True):
            with st.spinner("Generando PDF..."):
                try:
                    pdf_buffer = create_monthly_pdf_report(report_data, config)

                    if pdf_buffer:
                        filename = f"reporte_mensual_{config['month']:02d}_{config['year']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

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
                    st.error(f"Error generando PDF: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

def create_monthly_pdf_report(report_data, config):
    """Crea el reporte PDF completo"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E86C1'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        # Contenido
        story = []

        # Título
        story.append(Paragraph(f"Reporte Mensual de Expedición de Documentos", title_style))
        story.append(Paragraph(f"{config['month_name']} {config['year']}", title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))

        # KPIs
        current = report_data['current_month']
        total_tramites = current['num_tramites'].sum()
        total_ingresos = current['ingresos_totales'].sum()

        kpi_data = [
            ['Indicador', 'Valor'],
            ['Ingresos Totales', f"${total_ingresos:,.2f}"],
            ['Trámites Realizados', f"{int(total_tramites):,}"],
            ['Servicios Activos', f"{len(current)}"],
            ['Ingreso Promedio/Trámite', f"${(total_ingresos/max(total_tramites,1)):,.2f}"]
        ]

        kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86C1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        story.append(Paragraph("Resumen Ejecutivo", heading_style))
        story.append(kpi_table)
        story.append(Spacer(1, 20))

        # Tabla de servicios
        story.append(Paragraph("Servicios Expedidos", heading_style))

        services_data = [['Servicio', 'Cantidad', 'Ingresos Totales']]
        for _, row in current.nlargest(15, 'ingresos_totales').iterrows():
            services_data.append([
                Paragraph(row['servicio_corto'][:40], styles['Normal']),
                f"{int(row['num_tramites']):,}",
                f"${row['ingresos_totales']:,.2f}"
            ])

        services_table = Table(services_data, colWidths=[3.5*inch, 1*inch, 1.5*inch])
        services_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#85C1E9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))

        story.append(services_table)
        story.append(PageBreak())

        # Tabla comparativa de TRÁMITES
        if 'comparison_data' in st.session_state:
            story.append(Paragraph("Análisis Comparativo de Trámites", heading_style))

            comparison = st.session_state.comparison_data
            comp_data = [['Servicio', 'Mes Actual', 'Mes Ant.', '% Cambio', 'Año Ant.', '% Cambio']]

            for _, row in comparison.nlargest(10, 'tramites_actual').iterrows():
                cambio_mes = row['cambio_mes_ant']
                cambio_año = row['cambio_año_ant']

                comp_data.append([
                    Paragraph(row['servicio_corto'][:30], styles['Normal']),
                    f"{int(row['tramites_actual']):,}",
                    f"{int(row['tramites_mes_ant']):,}",
                    f"{cambio_mes:+.1f}%" if not pd.isna(cambio_mes) else "N/A",
                    f"{int(row['tramites_año_ant']):,}",
                    f"{cambio_año:+.1f}%" if not pd.isna(cambio_año) else "N/A"
                ])

            comp_table = Table(comp_data, colWidths=[2.2*inch, 1*inch, 0.9*inch, 0.8*inch, 0.9*inch, 0.8*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
            ]))

            story.append(comp_table)
            story.append(Spacer(1, 20))

        # Construir PDF
        doc.build(story)

        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        st.error(f"Error creando PDF: {str(e)}")
        return None
