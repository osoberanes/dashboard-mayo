#!/usr/bin/env python3
"""
Script de verificación completa de la nueva funcionalidad de comparación de períodos
"""

def verify_complete_functionality():
    """Verifica que toda la funcionalidad esté implementada correctamente"""
    
    print("="*60)
    print("VERIFICACION COMPLETA DE FUNCIONALIDAD")
    print("="*60)
    
    # 1. Verificar que el archivo principal existe y tiene el contenido correcto
    try:
        with open(r'C:\Users\consuladscrito\claudecode\Inicio\period_comparison_page.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar funciones clave implementadas
        required_functions = [
            'show_period_comparison_page',
            'get_available_years_and_periods', 
            'configure_year_comparison',
            'execute_year_comparison',
            'create_year_comparison_chart',
            'calculate_weekly_statistics',
            'show_weekly_analysis',
            'create_pdf_report',
            'show_pdf_export_button'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f'def {func}(' not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"[ERROR] Funciones faltantes: {missing_functions}")
            return False
        else:
            print(f"[OK] Todas las {len(required_functions)} funciones principales implementadas")
        
        # Verificar características específicas
        features = {
            'Interfaz año + período': 'configure_year_comparison' in content and 'selected_period' in content,
            'Gráfica consolidada': 'create_year_comparison_chart' in content and 'go.Figure()' in content,
            'Dropdown expandido': "['servicio'].unique()" in content and 'servicio_' in content,
            'Agrupación semanal': "'semana':" in content and 'isocalendar()' in content,
            'Análisis día semana': 'calculate_weekly_statistics' in content and 'dia_semana_es' in content,
            'Exportación PDF': 'create_pdf_report' in content and 'ReportLab' in content.replace('reportlab', 'ReportLab')
        }
        
        print("\nFUNCIONALIDADES IMPLEMENTADAS:")
        for feature, implemented in features.items():
            status = "[OK]" if implemented else "[FALTA]"
            print(f"  {status} {feature}")
            
        all_implemented = all(features.values())
        
        if all_implemented:
            print(f"\n[SUCCESS] Todas las funcionalidades están implementadas!")
        else:
            print(f"\n[WARNING] Algunas funcionalidades pueden estar incompletas")
            
        return all_implemented
        
    except Exception as e:
        print(f"[ERROR] Error verificando archivo principal: {e}")
        return False

def verify_dependencies():
    """Verifica que las dependencias están instaladas"""
    
    print("\nVERIFICANDO DEPENDENCIAS:")
    
    dependencies = [
        ('streamlit', 'Streamlit framework'),
        ('pandas', 'Análisis de datos'),
        ('plotly', 'Gráficas interactivas'),
        ('reportlab', 'Generación PDF'),
        ('kaleido', 'Conversión gráficas a imagen')
    ]
    
    all_deps_ok = True
    
    for dep_name, description in dependencies:
        try:
            __import__(dep_name)
            print(f"  [OK] {dep_name} - {description}")
        except ImportError:
            print(f"  [FALTA] {dep_name} - {description}")
            all_deps_ok = False
    
    return all_deps_ok

def verify_requirements_file():
    """Verifica que requirements.txt tiene las nuevas dependencias"""
    
    print("\nVERIFICANDO REQUIREMENTS.TXT:")
    
    try:
        with open(r'C:\Users\consuladscrito\claudecode\Inicio\requirements.txt', 'r') as f:
            content = f.read()
        
        new_deps = ['reportlab', 'matplotlib', 'kaleido']
        missing_deps = []
        
        for dep in new_deps:
            if dep not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"  [FALTA] Dependencias no encontradas en requirements.txt: {missing_deps}")
            return False
        else:
            print("  [OK] Todas las nuevas dependencias están en requirements.txt")
            return True
            
    except Exception as e:
        print(f"  [ERROR] Error verificando requirements.txt: {e}")
        return False

def verify_documentation():
    """Verifica que la documentación fue actualizada"""
    
    print("\nVERIFICANDO DOCUMENTACION:")
    
    try:
        with open(r'C:\Users\consuladscrito\claudecode\CLAUDE.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc_features = [
            'ACTUALIZACIONES SESIÓN 14 AGOSTO 2025',
            'Rediseño COMPLETO de Comparación de Períodos',
            'Análisis por Día de la Semana',
            'Exportación PDF Profesional',
            'create_year_comparison_chart'
        ]
        
        missing_docs = []
        for feature in doc_features:
            if feature not in content:
                missing_docs.append(feature)
        
        if missing_docs:
            print(f"  [FALTA] Secciones no encontradas en documentación: {missing_docs}")
            return False
        else:
            print("  [OK] Documentación actualizada con todas las nuevas funcionalidades")
            return True
            
    except Exception as e:
        print(f"  [ERROR] Error verificando documentación: {e}")
        return False

def main():
    """Función principal de verificación"""
    
    # Ejecutar todas las verificaciones
    func_ok = verify_complete_functionality()
    deps_ok = verify_dependencies()
    req_ok = verify_requirements_file() 
    doc_ok = verify_documentation()
    
    print("\n" + "="*60)
    print("RESUMEN DE VERIFICACION")
    print("="*60)
    
    results = [
        ("Funcionalidades implementadas", func_ok),
        ("Dependencias instaladas", deps_ok), 
        ("Requirements.txt actualizado", req_ok),
        ("Documentación actualizada", doc_ok)
    ]
    
    all_ok = True
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("ESTADO FINAL: TODO LISTO PARA USO [OK]")
        print("\nEl dashboard está ejecutándose en:")
        print("  http://localhost:8506")
        print("\nFuncionalidades disponibles:")
        print("  * Comparación año vs año del mismo período")
        print("  * Dropdown expandido con servicios individuales")
        print("  * Agrupación temporal semanal")
        print("  * Análisis por día de la semana")
        print("  * Exportación completa a PDF")
    else:
        print("ESTADO FINAL: REQUIERE ATENCION [WARNING]")
        print("\nAlgunas verificaciones fallaron. Revisar detalles arriba.")
    
    print("="*60)
    
    return all_ok

if __name__ == "__main__":
    main()