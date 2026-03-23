import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from pathlib import Path
import time
from file_manager import FileManager

def show_file_upload_page():
    """Página principal para gestión de archivos"""
    st.markdown("<h1 style='text-align: center;'>Gestión de Archivos Consulares</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    file_manager = FileManager()
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["Buscar Archivos", "Explorar Sistema", "Estado BD", "Administración"])
    
    with tab1:
        show_file_search_tab(file_manager)
    
    with tab2:
        show_file_explorer_tab(file_manager)
    
    with tab3:
        show_database_status_tab(file_manager)
    
    with tab4:
        show_admin_tab(file_manager)

def show_file_search_tab(file_manager):
    """Tab para buscar y seleccionar archivos"""
    st.markdown("<h2 style='text-align: center;'>Buscar Archivos Disponibles</h2>", unsafe_allow_html=True)
    
    # Configuración de búsqueda
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_directory = st.text_input(
            "Directorio de búsqueda", 
            value=".", 
            help="Ruta del directorio donde buscar archivos"
        )
    
    with col2:
        if st.button("Actualizar Búsqueda"):
            st.session_state.search_results = None  # Limpiar resultados anteriores
    
    # Buscar archivos
    if st.button("Buscar Archivos", type="primary") or 'search_results' not in st.session_state:
        with st.spinner("Buscando archivos..."):
            files = file_manager.get_available_files(search_directory)
            st.session_state.search_results = files
    
    if 'search_results' in st.session_state and st.session_state.search_results:
        files = st.session_state.search_results
        
        st.success(f"Encontrados {len(files)} archivos")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            extensions = list(set([f['extension'] for f in files]))
            selected_extensions = st.multiselect(
                "Filtrar por extensión", 
                extensions, 
                default=extensions
            )
        
        with col2:
            show_loaded = st.checkbox("Mostrar archivos ya cargados", value=True)
            show_not_loaded = st.checkbox("Mostrar archivos no cargados", value=True)
        
        with col3:
            min_size = st.number_input("Tamaño mínimo (bytes)", min_value=0, value=0)
        
        # Aplicar filtros
        filtered_files = []
        for f in files:
            if f['extension'] not in selected_extensions:
                continue
            if not show_loaded and f['ya_cargado']:
                continue
            if not show_not_loaded and not f['ya_cargado']:
                continue
            if f['tamaño'] < min_size:
                continue
            filtered_files.append(f)
        
        if filtered_files:
            # Mostrar archivos en tabla
            st.markdown(f"<h3 style='text-align: center;'>Archivos Encontrados ({len(filtered_files)})</h3>", unsafe_allow_html=True)
            
            # Convertir a DataFrame para mejor visualización
            df_files = pd.DataFrame(filtered_files)
            df_files['tamaño_mb'] = (df_files['tamaño'] / (1024*1024)).round(2)
            df_files['estado'] = df_files['ya_cargado'].map({True: 'Cargado', False: 'Pendiente'})
            
            # Selección de archivos
            selected_files = []
            
            for idx, file_info in enumerate(filtered_files):
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                
                # Calcular tamaño en MB
                tamaño_mb = file_info['tamaño'] / (1024 * 1024)
                
                with col1:
                    selected = st.checkbox("Seleccionar", key=f"file_{idx}", label_visibility="collapsed")
                    if selected:
                        selected_files.append(file_info)
                
                with col2:
                    status_text = "[CARGADO]" if file_info['ya_cargado'] else "[PENDIENTE]"
                    st.write(f"{status_text} **{file_info['nombre']}**")
                    st.caption(file_info['ruta_relativa'])
                
                with col3:
                    st.write(f"{tamaño_mb:.2f} MB")
                
                with col4:
                    st.write(file_info['fecha_modificacion'].strftime("%Y-%m-%d"))
                
                with col5:
                    if st.button("Previsualizar", key=f"preview_{idx}"):
                        show_file_preview(file_manager, file_info['ruta_completa'])
            
            # Acciones en lote
            if selected_files:
                st.markdown("---")
                st.markdown("<h3 style='text-align: center;'>Acciones para Archivos Seleccionados</h3>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    overwrite = st.checkbox("Sobrescribir duplicados existentes")
                
                with col2:
                    if st.button("Cargar Seleccionados", type="primary"):
                        load_selected_files(file_manager, selected_files, overwrite)
                
                with col3:
                    if st.button("Validar Seleccionados"):
                        validate_selected_files(file_manager, selected_files)
        
        else:
            st.info("No se encontraron archivos que coincidan con los filtros")
    
    elif 'search_results' in st.session_state:
        st.info("No se encontraron archivos en el directorio especificado")

def show_file_upload_tab(file_manager):
    """Tab para subir archivos directamente"""
    st.markdown("<h2 style='text-align: center;'>Cargar Archivo Directamente</h2>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Seleccionar archivo consular",
        type=['xls', 'xlsx', 'html', 'htm'],
        help="Seleccione un archivo con datos consulares (.xls, .xlsx, .html)"
    )
    
    if uploaded_file is not None:
        # Guardar archivo temporalmente
        temp_path = f"temp_{uploaded_file.name}"
        
        try:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"Archivo '{uploaded_file.name}' cargado temporalmente")
            
            # Validar estructura
            with st.spinner("Validando estructura del archivo..."):
                validation = file_manager.validate_file_structure(temp_path)
            
            if validation['is_valid']:
                st.success("Archivo válido")
                
                # Mostrar información del archivo
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Registros encontrados", validation['rows_count'])
                with col2:
                    st.metric("Columnas encontradas", len(validation['columns_found']))
                
                # Mostrar advertencias
                if validation['warnings']:
                    st.warning("Advertencias:")
                    for warning in validation['warnings']:
                        st.write(f"- {warning}")
                
                # Preview de datos
                if validation['preview_data'] is not None:
                    st.markdown("<h3 style='text-align: center;'>Previsualización de Datos</h3>", unsafe_allow_html=True)
                    st.dataframe(validation['preview_data'])
                
                # Opciones de carga
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    overwrite_duplicates = st.checkbox("Sobrescribir registros duplicados")
                
                with col2:
                    if st.button("💾 Cargar a Base de Datos", type="primary"):
                        with st.spinner("Cargando datos a la base de datos..."):
                            result = file_manager.load_file_to_database(temp_path, overwrite_duplicates)
                        
                        if result['success']:
                            st.success(result['message'])
                            st.balloons()
                        else:
                            st.error(result['message'])
            
            else:
                st.error(f"Archivo no válido: {validation['error_message']}")
                
        except Exception as e:
            st.error(f"Error procesando archivo: {str(e)}")
        
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)

def show_database_status_tab(file_manager):
    """Tab para mostrar estado de la base de datos"""
    st.markdown("<h2 style='text-align: center;'>Estado de la Base de Datos</h2>", unsafe_allow_html=True)
    
    # Obtener información de la BD
    db_summary = file_manager.get_database_summary()
    
    # KPIs principales
    stats = db_summary['stats']
    st.markdown("<h3 style='text-align: center;'>Métricas Principales</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Registros", f"{stats['total_registros']:,}")
    
    with col2:
        st.metric("Ingresos Totales", f"${stats['ingresos_totales']:,.2f}")
    
    with col3:
        st.metric("Trámites Totales", f"{stats['tramites_totales']:,}")
    
    with col4:
        st.metric("Cancelaciones", f"{stats['canceladas_totales']:,}")
    
    # Rango de fechas
    date_range = db_summary['date_range']
    if date_range['total_registros'] > 0:
        st.markdown("<h3 style='text-align: center;'>Rango de Fechas</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Fecha Más Antigua:** {date_range['fecha_min']}")
        with col2:
            st.info(f"**Fecha Más Reciente:** {date_range['fecha_max']}")
    
    # Historial de archivos cargados
    files_history = db_summary['files_history']
    if not files_history.empty:
        st.markdown("<h3 style='text-align: center;'>Historial de Archivos Cargados</h3>", unsafe_allow_html=True)
        
        # Agregar acciones
        for idx, row in files_history.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.write(f"📄 **{row['nombre_archivo']}**")
            
            with col2:
                st.caption(f"Cargado: {row['fecha_carga']}")
            
            with col3:
                st.write(f"✅ {row['registros_insertados']}")
            
            with col4:
                st.write(f"⚠️ {row['registros_duplicados']}")
            
            with col5:
                if st.button("🗑️", key=f"delete_{idx}", help="Eliminar datos de este archivo"):
                    if st.session_state.get(f"confirm_delete_{idx}", False):
                        result = file_manager.delete_file_data(row['nombre_archivo'])
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                    else:
                        st.session_state[f"confirm_delete_{idx}"] = True
                        st.warning("¿Confirma eliminar? Haga clic nuevamente.")
    
    else:
        st.info("No hay archivos cargados en la base de datos")

def show_admin_tab(file_manager):
    """Tab de administración avanzada"""
    st.markdown("<h2 style='text-align: center;'>Administración Avanzada</h2>", unsafe_allow_html=True)
    
    # Backup de base de datos
    st.markdown("<h3 style='text-align: center;'>Backup de Base de Datos</h3>", unsafe_allow_html=True)
    if st.button("Crear Backup"):
        try:
            backup_path = file_manager.db_manager.backup_database()
            st.success(f"Backup creado: {backup_path}")
        except Exception as e:
            st.error(f"Error creando backup: {str(e)}")
    
    # Exportar datos
    st.markdown("<h3 style='text-align: center;'>Exportar Datos</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        export_start_date = st.date_input("Fecha inicio", value=None)
    
    with col2:
        export_end_date = st.date_input("Fecha fin", value=None)
    
    export_filename = st.text_input("Nombre archivo export", value=f"export_consular_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    if st.button("📥 Exportar a Excel"):
        try:
            start_str = export_start_date.strftime('%Y-%m-%d') if export_start_date else None
            end_str = export_end_date.strftime('%Y-%m-%d') if export_end_date else None
            
            result = file_manager.export_data_to_excel(export_filename, start_str, end_str)
            
            if result['success']:
                st.success(result['message'])
                
                # Ofrecer descarga
                if os.path.exists(export_filename):
                    with open(export_filename, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Archivo",
                            data=file.read(),
                            file_name=export_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.error(result['message'])
        except Exception as e:
            st.error(f"Error exportando: {str(e)}")
    
    # Información del sistema
    st.markdown("<h3 style='text-align: center;'>Información del Sistema</h3>", unsafe_allow_html=True)
    st.info(f"Base de datos: {file_manager.db_manager.db_path}")
    st.info(f"Directorio actual: {os.getcwd()}")

def show_file_preview(file_manager, file_path):
    """Muestra preview de un archivo"""
    try:
        validation = file_manager.validate_file_structure(file_path)
        
        if validation['is_valid']:
            st.success("✅ Archivo válido")
            
            # Información del archivo
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Registros", validation['rows_count'])
            with col2:
                st.metric("Columnas", len(validation['columns_found']))
            
            # Preview de datos
            if validation['preview_data'] is not None:
                st.dataframe(validation['preview_data'])
        
        else:
            st.error(f"❌ Archivo no válido: {validation['error_message']}")
    
    except Exception as e:
        st.error(f"Error previsualizando archivo: {str(e)}")

def load_selected_files(file_manager, selected_files, overwrite):
    """Carga archivos seleccionados"""
    file_paths = [f['ruta_completa'] for f in selected_files]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Cargando archivos seleccionados..."):
        result = file_manager.batch_load_files(file_paths, overwrite)
    
    progress_bar.progress(1.0)
    status_text.text("¡Carga completada!")
    
    st.success(result['summary_message'])
    
    # Mostrar detalles
    if result['successful_files']:
        st.subheader("✅ Archivos Cargados Exitosamente")
        for file_result in result['successful_files']:
            st.write(f"- {file_result['filename']}: {file_result['stats']['inserted']} registros insertados")
    
    if result['failed_files']:
        st.subheader("❌ Archivos con Errores")
        for file_result in result['failed_files']:
            st.error(f"- {file_result['filename']}: {file_result['error']}")

def validate_selected_files(file_manager, selected_files):
    """Valida archivos seleccionados"""
    st.subheader("🔍 Validación de Archivos")
    
    for file_info in selected_files:
        with st.expander(f"📄 {file_info['nombre']}"):
            show_file_preview(file_manager, file_info['ruta_completa'])

def show_file_explorer_tab(file_manager):
    """Tab para explorar archivos usando el explorador del sistema"""
    st.markdown("<h2 style='text-align: center;'>Explorador de Sistema</h2>", unsafe_allow_html=True)
    st.markdown("Utiliza el explorador de archivos del sistema para cargar archivos individuales.")
    
    # Selector de archivos nativo de Streamlit
    uploaded_files = st.file_uploader(
        "🗂️ Seleccionar Archivos Consulares",
        type=['xls', 'xlsx', 'html', 'htm'],
        accept_multiple_files=True,
        help="Seleccione uno o más archivos con datos consulares (.xls, .xlsx, .html)"
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} archivo(s) seleccionado(s)")
        
        # Mostrar información de archivos seleccionados
        st.subheader("📋 Archivos Seleccionados")
        
        files_data = []
        valid_files = []
        
        for idx, uploaded_file in enumerate(uploaded_files):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"📄 **{uploaded_file.name}**")
                st.caption(f"Tipo: {uploaded_file.type}, Tamaño: {uploaded_file.size / 1024:.1f} KB")
            
            with col2:
                if st.button("👁️ Previsualizar", key=f"preview_explorer_{idx}"):
                    show_file_preview_from_upload(file_manager, uploaded_file)
            
            with col3:
                validate_btn = st.button("✅ Validar", key=f"validate_explorer_{idx}")
                if validate_btn:
                    validation_result = validate_uploaded_file(file_manager, uploaded_file)
                    if validation_result['is_valid']:
                        st.success("Válido ✅")
                        valid_files.append((uploaded_file, validation_result))
                    else:
                        st.error(f"❌ {validation_result['error_message']}")
            
            with col4:
                files_data.append({
                    'file': uploaded_file,
                    'name': uploaded_file.name,
                    'size_kb': uploaded_file.size / 1024
                })
        
        # Sección de carga en lote
        if uploaded_files:
            st.markdown("---")
            st.subheader("⚡ Carga en Lote")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                validate_all = st.button("🔍 Validar Todos", type="secondary")
                if validate_all:
                    validate_all_uploaded_files(file_manager, uploaded_files)
            
            with col2:
                overwrite_batch = st.checkbox("Sobrescribir duplicados", key="batch_overwrite")
            
            with col3:
                load_all = st.button("📤 Cargar Todos", type="primary")
                if load_all:
                    load_all_uploaded_files(file_manager, uploaded_files, overwrite_batch)
        
        # Información adicional
        st.markdown("---")
        st.info("""
        **💡 Consejos para el Explorador:**
        - Puedes seleccionar múltiples archivos a la vez
        - Los archivos .xls pueden ser HTML disfrazados (compatible)
        - Se valida automáticamente la estructura antes de cargar
        - Los duplicados se detectan por servicio + fecha + categoría
        """)

def show_file_preview_from_upload(file_manager, uploaded_file):
    """Muestra preview de un archivo subido"""
    temp_path = f"temp_preview_{uploaded_file.name}"
    
    try:
        # Guardar temporalmente
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Mostrar preview
        show_file_preview(file_manager, temp_path)
        
    except Exception as e:
        st.error(f"Error previsualizando archivo: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)

def validate_uploaded_file(file_manager, uploaded_file):
    """Valida un archivo subido"""
    temp_path = f"temp_validate_{uploaded_file.name}"
    
    try:
        # Guardar temporalmente
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Validar
        return file_manager.validate_file_structure(temp_path)
        
    except Exception as e:
        return {
            'is_valid': False,
            'error_message': f"Error validando archivo: {str(e)}",
            'warnings': [],
            'preview_data': None
        }
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)

def validate_all_uploaded_files(file_manager, uploaded_files):
    """Valida todos los archivos subidos"""
    st.subheader("🔍 Validación en Lote")
    
    valid_count = 0
    invalid_count = 0
    
    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name}"):
            validation = validate_uploaded_file(file_manager, uploaded_file)
            
            if validation['is_valid']:
                st.success("Archivo válido")
                valid_count += 1
                
                # Mostrar información
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Registros", validation.get('rows_count', 0))
                with col2:
                    st.metric("Columnas", len(validation.get('columns_found', [])))
                
                # Mostrar advertencias
                if validation.get('warnings'):
                    st.warning("Advertencias:")
                    for warning in validation['warnings']:
                        st.write(f"- {warning}")
            else:
                st.error(f"❌ {validation['error_message']}")
                invalid_count += 1
    
    # Resumen
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Archivos Válidos", valid_count)
    with col2:
        st.metric("❌ Archivos Inválidos", invalid_count)

def load_all_uploaded_files(file_manager, uploaded_files, overwrite_duplicates):
    """Carga todos los archivos subidos"""
    st.subheader("📤 Carga en Lote")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    successful_files = []
    failed_files = []
    total_stats = {'inserted': 0, 'duplicates': 0, 'errors': 0, 'total_processed': 0}
    
    for idx, uploaded_file in enumerate(uploaded_files):
        # Actualizar progreso
        progress = (idx + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Procesando: {uploaded_file.name}")
        
        temp_path = f"temp_load_{uploaded_file.name}"
        
        try:
            # Guardar temporalmente
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Cargar archivo
            result = file_manager.load_file_to_database(temp_path, overwrite_duplicates)
            
            if result['success']:
                successful_files.append({
                    'filename': uploaded_file.name,
                    'stats': result['stats']
                })
                
                # Acumular estadísticas
                for key in total_stats:
                    total_stats[key] += result['stats'].get(key, 0)
            else:
                failed_files.append({
                    'filename': uploaded_file.name,
                    'error': result['message']
                })
        
        except Exception as e:
            failed_files.append({
                'filename': uploaded_file.name,
                'error': f"Error procesando archivo: {str(e)}"
            })
        
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # Completar progreso
    progress_bar.progress(1.0)
    status_text.text("¡Carga completada!")
    
    # Mostrar resultados
    if successful_files or failed_files:
        st.success(f"""✅ Carga en lote completada:
        - {len(successful_files)} archivos cargados exitosamente
        - {len(failed_files)} archivos fallaron
        - {total_stats['inserted']:,} registros insertados
        - {total_stats['duplicates']:,} duplicados omitidos
        """)
        
        if successful_files:
            st.subheader("✅ Archivos Cargados Exitosamente")
            for file_result in successful_files:
                st.write(f"- **{file_result['filename']}**: {file_result['stats']['inserted']:,} registros insertados")
        
        if failed_files:
            st.subheader("❌ Archivos con Errores")
            for file_result in failed_files:
                st.error(f"- **{file_result['filename']}**: {file_result['error']}")
        
        st.balloons()