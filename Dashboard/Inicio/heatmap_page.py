import calendar
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from enhanced_data_processor import EnhancedDataProcessor

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


def _initialize_processor():
    """Inicializa y retorna el procesador con datos cargados, o None si falla."""
    try:
        processor = EnhancedDataProcessor()
        if not processor.initialize_from_database():
            st.error("No se pudo conectar a la base de datos.")
            return None
        if processor.df is None or processor.df.empty:
            st.warning("No hay datos disponibles en la base de datos.")
            return None
        processor.df["fecha_emision"] = pd.to_datetime(processor.df["fecha_emision"])
        return processor
    except Exception as e:
        st.error(f"Error al inicializar el procesador: {e}")
        return None


def _get_available_periods(df: pd.DataFrame) -> list[dict]:
    """Retorna lista de periodos disponibles ordenados desc: [{label, year, month}]."""
    periods = (
        df[["fecha_emision"]]
        .assign(year=df["fecha_emision"].dt.year, month=df["fecha_emision"].dt.month)
        .drop_duplicates(subset=["year", "month"])
        .sort_values(["year", "month"], ascending=False)
    )
    result = []
    for _, row in periods.iterrows():
        label = f"{MESES_ES[int(row['month'])]} {int(row['year'])}"
        result.append({"label": label, "year": int(row["year"]), "month": int(row["month"])})
    return result


def _build_calendar_matrix(year: int, month: int, daily_values: dict) -> tuple:
    """
    Construye la matriz de valores para el heatmap estilo calendario.

    Orientación:
        Eje X (columnas) = días de la semana: Lun, Mar, Mié, Jue, Vie, Sáb, Dom
        Eje Y (filas)    = semanas: Sem 1 (arriba) → última semana (abajo)

    Returns:
        z_matrix: lista de n_weeks listas de 7 elementos (valor o None)
        annotations: lista de dicts con info de cada celda válida
        n_weeks: número de semanas (filas)
    """
    weeks = calendar.monthcalendar(year, month)  # lista de semanas; 0 = día fuera del mes
    n_weeks = len(weeks)

    # z_matrix[w_idx][d_idx] = valor o None
    z_matrix = [[None] * 7 for _ in range(n_weeks)]
    annotations = []

    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            if day == 0:
                continue  # día fuera del mes
            fecha = pd.Timestamp(year=year, month=month, day=day)
            valor = daily_values.get(fecha, 0)
            z_matrix[w_idx][d_idx] = valor

            annotations.append({
                "w_idx": w_idx,
                "d_idx": d_idx,
                "day": day,
                "value": valor,
                "fecha": fecha,
            })

    return z_matrix, annotations, n_weeks


def _build_heatmap_figure(
    z_matrix: list,
    annotations: list,
    n_weeks: int,
    year: int,
    month: int,
    metrica_label: str,
    colorscale: str,
    format_value,
) -> go.Figure:
    """
    Construye la figura Plotly del heatmap calendario.

    Eje X = días de la semana (Lun → Dom)
    Eje Y = semanas (Sem 1 arriba → última semana abajo)
    Celdas cuadradas mediante scaleanchor.
    """
    y_labels = [f"Sem {i + 1}" for i in range(n_weeks)]

    # Rango de color (ignorar None)
    valores = [v for row in z_matrix for v in row if v is not None]
    zmin = 0
    zmax = max(valores) if valores else 1

    # Grilla de customdata[w_idx][d_idx] para hover
    custom_grid = [["" for _ in range(7)] for _ in range(n_weeks)]
    for ann in annotations:
        fecha_str = ann["fecha"].strftime("%A %d/%m/%Y").capitalize()
        val_str = format_value(ann["value"])
        custom_grid[ann["w_idx"]][ann["d_idx"]] = (
            f"<b>{fecha_str}</b><br>{metrica_label}: {val_str}"
        )

    fig = go.Figure(
        go.Heatmap(
            z=z_matrix,
            x=DIAS_SEMANA,
            y=y_labels,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            showscale=True,
            colorbar=dict(
                title=dict(text=metrica_label, font=dict(color="#4A5568", size=11, family="'DM Sans',sans-serif")),
                tickfont=dict(color="#8A9099", size=10),
                thickness=12,
                len=0.75,
                bgcolor="rgba(247,245,240,0)",
                outlinecolor="#E0DDD7",
            ),
            hoverongaps=False,
            customdata=custom_grid,
            hovertemplate="%{customdata}<extra></extra>",
        )
    )

    # Anotaciones de texto: número de día (grande) + valor (pequeño)
    plot_annotations = []
    for ann in annotations:
        val_text = format_value(ann["value"]) if ann["value"] else "—"
        # Color del texto: blanco en celdas oscuras, gris oscuro en celdas claras
        text_color = "#FFFFFF" if ann["value"] and ann["value"] > zmax * 0.55 else "#1E2B3C"
        plot_annotations.append(
            dict(
                x=DIAS_SEMANA[ann["d_idx"]],
                y=y_labels[ann["w_idx"]],
                text=f"<b>{ann['day']}</b><br><span style='font-size:10px'>{val_text}</span>",
                showarrow=False,
                font=dict(size=12, color=text_color),
                xref="x",
                yref="y",
            )
        )

    mes_nombre = MESES_ES[month]

    # Alto fijo por fila para lograr celdas cuadradas:
    # 7 columnas en ancho → cada celda ~100px; n_weeks filas
    cell_px = 100
    chart_height = n_weeks * cell_px + 120  # margen para título y ejes

    fig.update_layout(
        title=dict(
            text=f"<b>{metrica_label} por día — {mes_nombre} {year}</b>",
            font=dict(
                size=16,
                family="'DM Serif Display', Georgia, serif",
                color="#1E2B3C",
            ),
        ),
        xaxis=dict(
            side="top",
            tickfont=dict(size=13, color="#4A5568", family="'DM Sans', sans-serif"),
            fixedrange=True,
            linecolor="#E0DDD7",
            showgrid=False,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color="#8A9099", family="'DM Sans', sans-serif"),
            autorange="reversed",
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1,
            linecolor="#E0DDD7",
            showgrid=False,
        ),
        height=chart_height,
        margin=dict(t=90, b=10, l=70, r=20),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#F7F5F0",
        annotations=plot_annotations,
    )

    return fig


def _show_kpis(daily_values: dict, metrica_label: str, format_value, year: int, month: int):
    """Muestra KPIs resumen debajo del heatmap."""
    if not daily_values:
        st.info("Sin datos para el período seleccionado.")
        return

    total = sum(daily_values.values())
    dias_con_datos = len([v for v in daily_values.values() if v > 0])
    dias_en_mes = calendar.monthrange(year, month)[1]
    dias_sin_op = dias_en_mes - dias_con_datos
    promedio = total / dias_con_datos if dias_con_datos else 0
    dia_max = max(daily_values, key=daily_values.get)
    valor_max = daily_values[dia_max]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total del mes", format_value(total))
    with col2:
        st.metric("Día más activo", f"{dia_max.strftime('%d/%m')} ({format_value(valor_max)})")
    with col3:
        st.metric("Promedio diario", format_value(promedio))
    with col4:
        st.metric("Días sin operación", str(dias_sin_op))


def show_heatmap_page():
    """Página principal: Heatmap Calendario de operación consular."""
    st.markdown("""
    <div style="margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #E0DDD7;">
        <p style="font-family:'DM Sans',sans-serif; font-size:0.72rem; color:#2C4A6E; text-transform:uppercase; letter-spacing:0.15em; margin:0 0 0.3rem;">
            Análisis de operación
        </p>
        <h1 style="font-family:'DM Serif Display',Georgia,serif; color:#1E2B3C; margin:0 0 0.3rem; font-size:2rem; font-weight:400; line-height:1.1;">
            Heatmap Calendario
        </h1>
        <p style="font-family:'DM Sans',sans-serif; color:#8A9099; margin:0; font-size:0.85rem;">
            Distribución diaria de actividad consular por semana del mes
        </p>
    </div>
    """, unsafe_allow_html=True)

    processor = _initialize_processor()
    if processor is None:
        return

    df = processor.df

    # ── Controles ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        categorias = ["Todas"] + sorted(df["categoria"].dropna().unique().tolist())
        categoria = st.selectbox("Categoría de acto", options=categorias, key="hm_categoria")

    with col2:
        periods = _get_available_periods(df)
        if not periods:
            st.warning("No hay períodos disponibles.")
            return
        period_labels = [p["label"] for p in periods]
        selected_label = st.selectbox("Mes", options=period_labels, key="hm_mes")
        selected_period = next(p for p in periods if p["label"] == selected_label)
        year = selected_period["year"]
        month = selected_period["month"]

    with col3:
        metrica = st.radio("Métrica", options=["Trámites", "Ingresos"], key="hm_metrica")

    # ── Filtrado de datos ───────────────────────────────────────────────────────
    df_filtered = df[
        (df["fecha_emision"].dt.year == year) &
        (df["fecha_emision"].dt.month == month)
    ].copy()

    if categoria != "Todas":
        df_filtered = df_filtered[df_filtered["categoria"] == categoria]

    if df_filtered.empty:
        st.warning(f"No hay datos para {selected_label}" + (f" — {categoria}" if categoria != "Todas" else "") + ".")
        return

    # ── Agrupación diaria ───────────────────────────────────────────────────────
    if metrica == "Trámites":
        metric_col = "num_tramites"
        metrica_label = "Trámites"
        colorscale = [[0, "#EEF4FA"], [0.4, "#3A7CA5"], [1, "#2C4A6E"]]
        format_value = lambda v: f"{int(v):,}"
    else:
        metric_col = "ingresos_totales"
        metrica_label = "Ingresos (USD)"
        colorscale = [[0, "#EEF4EE"], [0.4, "#4A9E6A"], [1, "#2A7A4B"]]
        format_value = lambda v: f"${v:,.2f}"

    daily_series = (
        df_filtered.groupby("fecha_emision")[metric_col]
        .sum()
        .reset_index()
    )
    daily_values = {
        row["fecha_emision"]: row[metric_col]
        for _, row in daily_series.iterrows()
    }

    # Subtitle con filtro activo
    cat_text = f" &nbsp;·&nbsp; {categoria}" if categoria != "Todas" else ""
    st.markdown(
        f'<p style="font-family:\'DM Sans\',sans-serif; font-size:0.8rem; color:#8A9099; '
        f'text-transform:uppercase; letter-spacing:0.1em; margin:0.5rem 0 0.2rem;">'
        f'{metrica_label}{cat_text}</p>',
        unsafe_allow_html=True,
    )

    # ── Heatmap ─────────────────────────────────────────────────────────────────
    z_matrix, annotations, n_weeks = _build_calendar_matrix(year, month, daily_values)

    fig = _build_heatmap_figure(
        z_matrix=z_matrix,
        annotations=annotations,
        n_weeks=n_weeks,
        year=year,
        month=month,
        metrica_label=metrica_label,
        colorscale=colorscale,
        format_value=format_value,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── KPIs ────────────────────────────────────────────────────────────────────
    st.markdown("---")
    _show_kpis(daily_values, metrica_label, format_value, year, month)
