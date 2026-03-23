# -*- coding: utf-8 -*-
"""
Página de configuración de mapeos de nombres de servicios
"""

import streamlit as st
import pandas as pd
from service_name_mappings import service_mapper
from enhanced_data_processor import EnhancedDataProcessor

def show_service_mapping_config_page():
    """Página para configurar mapeos de nombres de servicios"""
    
    st.markdown("# Configuración de Nombres de Servicios")
    st.markdown("### Gestiona los nombres cortos para mejorar las visualizaciones")
    
    # Obtener servicios únicos de la base de datos
    try:
        processor = EnhancedDataProcessor()
        if processor.initialize_from_database():
            unique_services = sorted(processor.df['servicio'].unique().tolist())
        else:
            unique_services = []
    except:
        unique_services = []
    
    # Pestañas para organizar la funcionalidad
    tab1, tab2, tab3 = st.tabs(["Agregar Mapeos", "Mapeos Existentes", "Vista Previa"])
    
    with tab1:
        show_add_mappings_section(unique_services)
    
    with tab2:
        show_existing_mappings_section()
    
    with tab3:
        show_preview_section(unique_services)

def show_add_mappings_section(unique_services):
    """Sección para agregar nuevos mapeos"""
    
    st.markdown("### Agregar Mapeos de Nombres")
    st.markdown("Selecciona los servicios y define nombres cortos para mejorar la visualización")
    
    if not unique_services:
        st.warning("No hay servicios disponibles. Asegúrate de tener datos cargados en la base de datos.")
        return
    
    # Opción 1: Mapeo individual
    st.markdown("#### Mapeo Individual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_service = st.selectbox(
            "Selecciona el servicio original",
            options=[""] + unique_services,
            key="individual_service"
        )
    
    with col2:
        if selected_service:
            current_short_name = service_mapper.get_short_name(selected_service)
            short_name = st.text_input(
                "Nombre corto",
                value=current_short_name if current_short_name != selected_service else "",
                key="individual_short_name",
                help="Ingresa un nombre más corto y descriptivo"
            )
    
    if selected_service and st.button("Guardar Mapeo Individual"):
        short_name = st.session_state.get("individual_short_name", "").strip()
        if short_name and short_name != selected_service:
            service_mapper.add_mapping(selected_service, short_name)
            st.success(f"✅ Mapeo guardado: '{selected_service}' → '{short_name}'")
            st.rerun()
        else:
            st.error("Por favor ingresa un nombre corto válido")
    
    st.markdown("---")
    
    # Opción 2: Mapeo masivo
    st.markdown("#### Mapeo Masivo")
    st.markdown("Define múltiples mapeos usando el formato: `Nombre Original|Nombre Corto`")
    
    bulk_mappings = st.text_area(
        "Mapeos masivos (uno por línea)",
        height=200,
        help="Formato: Nombre Original|Nombre Corto\nEjemplo:\nEXPEDICION DE PASAPORTE ORDINARIO|Pasaporte Ordinario\nRENOVACION DE MATRICULA CONSULAR|Renovación Matrícula",
        key="bulk_mappings"
    )
    
    if st.button("Procesar Mapeos Masivos"):
        if bulk_mappings.strip():
            process_bulk_mappings(bulk_mappings)
        else:
            st.error("Por favor ingresa al menos un mapeo")

def process_bulk_mappings(bulk_text):
    """Procesa mapeos masivos desde texto"""
    lines = bulk_text.strip().split('\n')
    successful_mappings = []
    errors = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        if '|' not in line:
            errors.append(f"Línea {i}: Formato incorrecto (falta '|')")
            continue
        
        parts = line.split('|', 1)  # Solo dividir en el primer |
        if len(parts) != 2:
            errors.append(f"Línea {i}: Formato incorrecto")
            continue
        
        original_name = parts[0].strip()
        short_name = parts[1].strip()
        
        if not original_name or not short_name:
            errors.append(f"Línea {i}: Nombre original o corto vacío")
            continue
        
        try:
            service_mapper.add_mapping(original_name, short_name)
            successful_mappings.append(f"'{original_name}' → '{short_name}'")
        except Exception as e:
            errors.append(f"Línea {i}: Error guardando mapeo - {str(e)}")
    
    # Mostrar resultados
    if successful_mappings:
        st.success(f"✅ {len(successful_mappings)} mapeos guardados exitosamente:")
        for mapping in successful_mappings:
            st.write(f"• {mapping}")
    
    if errors:
        st.error(f"❌ {len(errors)} errores encontrados:")
        for error in errors:
            st.write(f"• {error}")
    
    if successful_mappings:
        st.rerun()

def show_existing_mappings_section():
    """Sección para ver y editar mapeos existentes"""
    
    st.markdown("### Mapeos Existentes")
    
    mappings = service_mapper.get_all_mappings()
    
    if not mappings:
        st.info("No hay mapeos configurados aún.")
        return
    
    # Crear DataFrame para mostrar los mapeos
    df_mappings = pd.DataFrame([
        {"Nombre Original": original, "Nombre Corto": short}
        for original, short in mappings.items()
    ])
    
    st.markdown(f"**Total de mapeos:** {len(mappings)}")
    
    # Tabla editable
    edited_df = st.data_editor(
        df_mappings,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Nombre Original": st.column_config.TextColumn("Nombre Original", width="large"),
            "Nombre Corto": st.column_config.TextColumn("Nombre Corto", width="medium")
        },
        key="mappings_editor"
    )
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Guardar Cambios"):
            save_edited_mappings(edited_df, mappings)
    
    with col2:
        if st.button("Exportar Mapeos"):
            export_mappings(mappings)
    
    with col3:
        if st.button("Limpiar Todos", type="secondary"):
            if st.session_state.get("confirm_clear", False):
                clear_all_mappings()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Haz clic nuevamente para confirmar")

def save_edited_mappings(edited_df, original_mappings):
    """Guarda los mapeos editados"""
    try:
        # Crear nuevo diccionario de mapeos
        new_mappings = {}
        for _, row in edited_df.iterrows():
            original = str(row["Nombre Original"]).strip()
            short = str(row["Nombre Corto"]).strip()
            if original and short:
                new_mappings[original] = short
        
        # Actualizar mapeos
        service_mapper.mappings = new_mappings
        service_mapper.reverse_mappings = {v: k for k, v in new_mappings.items()}
        service_mapper.save_mappings()
        
        st.success("✅ Mapeos actualizados exitosamente")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error guardando mapeos: {str(e)}")

def export_mappings(mappings):
    """Exporta los mapeos a archivo"""
    try:
        # Crear contenido para exportar
        export_content = ""
        for original, short in mappings.items():
            export_content += f"{original}|{short}\n"
        
        st.download_button(
            label="📁 Descargar Mapeos",
            data=export_content,
            file_name="service_mappings.txt",
            mime="text/plain",
            help="Descarga los mapeos en formato de texto"
        )
        
    except Exception as e:
        st.error(f"Error exportando mapeos: {str(e)}")

def clear_all_mappings():
    """Limpia todos los mapeos"""
    try:
        service_mapper.mappings = {}
        service_mapper.reverse_mappings = {}
        service_mapper.save_mappings()
        
        st.success("✅ Todos los mapeos han sido eliminados")
        st.session_state.confirm_clear = False
        st.rerun()
        
    except Exception as e:
        st.error(f"Error limpiando mapeos: {str(e)}")

def show_preview_section(unique_services):
    """Sección para vista previa de los mapeos"""
    
    st.markdown("### Vista Previa de Mapeos")
    
    if not unique_services:
        st.warning("No hay servicios disponibles para vista previa.")
        return
    
    # Mostrar algunos ejemplos de cómo se verán los nombres
    st.markdown("#### Comparación de Nombres")
    
    preview_data = []
    for service in unique_services[:10]:  # Mostrar solo los primeros 10
        short_name = service_mapper.get_short_name(service)
        preview_data.append({
            "Nombre Original": service,
            "Nombre en Visualizaciones": short_name,
            "Mapeado": "Sí" if short_name != service else "No"
        })
    
    if preview_data:
        df_preview = pd.DataFrame(preview_data)
        st.dataframe(
            df_preview,
            use_container_width=True,
            column_config={
                "Nombre Original": st.column_config.TextColumn("Nombre Original", width="large"),
                "Nombre en Visualizaciones": st.column_config.TextColumn("Nombre en Visualizaciones", width="medium"),
                "Mapeado": st.column_config.TextColumn("Mapeado", width="small")
            }
        )
    
    # Estadísticas
    total_services = len(unique_services)
    mapped_services = sum(1 for service in unique_services if service_mapper.get_short_name(service) != service)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Servicios", total_services)
    with col2:
        st.metric("Servicios Mapeados", mapped_services)
    with col3:
        percentage = (mapped_services / total_services * 100) if total_services > 0 else 0
        st.metric("Porcentaje Mapeado", f"{percentage:.1f}%")