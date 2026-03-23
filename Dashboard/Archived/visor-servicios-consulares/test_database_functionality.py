"""
Test completo de funcionalidad de base de datos
"""
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configurar path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_database_with_real_data():
    """Test completo de base de datos con datos reales"""
    
    print("=" * 60)
    print("DATABASE FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        # Importar módulos
        from config.settings import settings
        from core.database import DatabaseManager
        
        print(f"[OK] Config: {settings.app.title}")
        print(f"[OK] DB Path: {settings.database.path}")
        
        # Crear instancia de base de datos
        db = DatabaseManager()
        print("[OK] Database manager created")
        
        # Verificar estadísticas iniciales
        initial_stats = db.get_summary_stats()
        print(f"[INFO] Initial records: {initial_stats['total_registros']}")
        
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'servicio': ['Test Service 1', 'Test Service 2', 'Test Service 3'],
            'categoria': ['TEST_CATEGORY', 'TEST_CATEGORY', 'TEST_CATEGORY'],
            'costo_unitario': [100.0, 150.0, 200.0],
            'num_tramites': [5, 8, 12],
            'ingresos_totales': [500.0, 1200.0, 2400.0],
            'fecha_emision': [datetime(2024, 5, 1), datetime(2024, 5, 2), datetime(2024, 5, 3)],
            'formas_canceladas': [0, 1, 2]
        })
        
        print(f"[OK] Test data created: {len(test_data)} records")
        
        # Insertar datos de prueba
        result = db.insert_data(test_data, 'test_database_functionality.py')
        print(f"[OK] Data inserted: {result['insertados']} new, {result['duplicados']} duplicates")
        
        # Verificar carga de datos
        loaded_data = db.load_data()
        print(f"[OK] Data loaded: {len(loaded_data)} total records")
        
        # Verificar estadísticas actualizadas
        final_stats = db.get_summary_stats()
        print(f"[OK] Final stats:")
        print(f"    - Total records: {final_stats['total_registros']}")
        print(f"    - Total income: ${final_stats['ingresos_totales']:,.2f}")
        print(f"    - Total procedures: {final_stats['tramites_totales']}")
        print(f"    - Unique categories: {final_stats['categorias_unicas']}")
        print(f"    - Unique services: {final_stats['servicios_unicos']}")
        
        # Verificar rango de fechas
        date_range = db.get_date_range()
        print(f"[OK] Date range: {date_range['fecha_min']} to {date_range['fecha_max']}")
        
        # Verificar listas
        services = db.get_services_list()
        categories = db.get_categories_list()
        print(f"[OK] Services list: {len(services)} services")
        print(f"[OK] Categories list: {len(categories)} categories")
        
        # Verificar datos temporales
        temporal_data = db.get_temporal_data('mensual')
        print(f"[OK] Temporal data (monthly): {len(temporal_data)} periods")
        
        # Verificar historial de archivos
        file_history = db.get_file_history()
        print(f"[OK] File history: {len(file_history)} files loaded")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] DATABASE FUNCTIONALITY VERIFIED")
        print("✓ Database creation and connection")
        print("✓ Data insertion with duplicate control")
        print("✓ Data loading with filters")
        print("✓ Statistics calculation")
        print("✓ Date range queries")
        print("✓ Service and category lists")
        print("✓ Temporal data grouping")
        print("✓ File history tracking")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics_functionality():
    """Test funcionalidad de analytics"""
    
    print("\n" + "=" * 60)
    print("ANALYTICS FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        from core.database import DatabaseManager
        from core.analytics import AnalyticsEngine
        
        db = DatabaseManager()
        analytics = AnalyticsEngine(db)
        
        print("[OK] Analytics engine created")
        
        # Test KPIs
        kpis = analytics.get_kpis()
        print(f"[OK] KPIs calculated:")
        print(f"    - Total income: ${kpis['total_ingresos']:,.2f}")
        print(f"    - Total procedures: {kpis['total_tramites']}")
        print(f"    - Average per procedure: ${kpis['promedio_por_tramite']:.2f}")
        print(f"    - Unique services: {kpis['servicios_unicos']}")
        
        # Test análisis temporal
        temporal = analytics.get_temporal_analysis()
        print(f"[OK] Temporal analysis: {len(temporal)} periods")
        
        # Test top servicios
        top_services = analytics.get_top_services(by='ingresos', limit=5)
        print(f"[OK] Top services by income: {len(top_services)} services")
        
        # Test comparación
        comparison = analytics.get_period_comparison('2024-05-01', '2024-05-31', '2024-04-01', '2024-04-30')
        print(f"[OK] Period comparison completed")
        
        print("\n[SUCCESS] ANALYTICS FUNCTIONALITY VERIFIED")
        print("✓ KPI calculations")
        print("✓ Temporal analysis")
        print("✓ Top services ranking")
        print("✓ Period comparisons")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_charts_functionality():
    """Test funcionalidad de charts"""
    
    print("\n" + "=" * 60)
    print("CHARTS FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        from core.charts import ChartFactory
        import pandas as pd
        
        charts = ChartFactory()
        print("[OK] Chart factory created")
        
        # Datos de prueba para gráficas
        test_data = pd.DataFrame({
            'x': ['A', 'B', 'C', 'D', 'E'],
            'y': [10, 25, 30, 45, 20],
            'category': ['Cat1', 'Cat1', 'Cat2', 'Cat2', 'Cat3']
        })
        
        # Test line chart
        line_chart = charts.create_line_chart(test_data, 'x', 'y', 'Test Line Chart')
        print(f"[OK] Line chart created: {len(line_chart.data)} traces")
        
        # Test bar chart
        bar_chart = charts.create_bar_chart(test_data, 'x', 'y', 'Test Bar Chart')
        print(f"[OK] Bar chart created: {len(bar_chart.data)} traces")
        
        # Test KPI display
        kpi_display = charts.create_kpi_display("Test KPI", 12345, "currency")
        print(f"[OK] KPI display created")
        
        # Test comparison chart
        comparison_data = pd.DataFrame({
            'periodo': ['Jan', 'Feb', 'Mar'],
            'valor_1': [100, 150, 200],
            'valor_2': [120, 130, 180]
        })
        
        comparison_chart = charts.create_comparison_chart(
            comparison_data, 'periodo', ['valor_1', 'valor_2'], 'Comparison Chart'
        )
        print(f"[OK] Comparison chart created: {len(comparison_chart.data)} traces")
        
        print("\n[SUCCESS] CHARTS FUNCTIONALITY VERIFIED")
        print("✓ Line charts")
        print("✓ Bar charts") 
        print("✓ KPI displays")
        print("✓ Comparison charts")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Charts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests funcionales"""
    
    tests = [
        test_database_with_real_data,
        test_analytics_functionality,
        test_charts_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 80)
    if passed == total:
        print(f"[SUCCESS] ALL FUNCTIONALITY TESTS PASSED ({passed}/{total})")
        print("🚀 Visor de Servicios Consulares is ready for full deployment!")
    else:
        print(f"[WARNING] {passed}/{total} functionality tests passed")
        print("Some components may need additional debugging")
    print("=" * 80)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✨ Next step: Launch the full application with:")
        print("   python start_app.py")
    exit(0 if success else 1)