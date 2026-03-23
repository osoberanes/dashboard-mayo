"""
Test básico de funcionalidad sin usar la aplicación completa
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core import DatabaseManager, AnalyticsEngine, ChartFactory
from config import settings
import pandas as pd

def test_basic_functionality():
    """Test funcionalidad básica"""
    print("=" * 60)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Test 1: Configuración
        print(f"✓ Settings loaded: {settings.app.title}")
        
        # Test 2: Base de datos
        print("Testing Database...")
        db = DatabaseManager()
        stats = db.get_summary_stats()
        print(f"✓ Database connected: {stats.get('total_registros', 0)} records")
        
        # Test 3: Analytics
        print("Testing Analytics...")
        analytics = AnalyticsEngine(db)
        kpis = analytics.get_kpis()
        print(f"✓ Analytics working: ${kpis['total_ingresos']:,.2f} total income")
        
        # Test 4: Charts
        print("Testing Charts...")
        charts = ChartFactory()
        # Crear datos de prueba simples
        test_data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [10, 20, 15, 25, 30]
        })
        fig = charts.create_line_chart(test_data, 'x', 'y', 'Test Chart')
        print(f"✓ Charts working: {len(fig.data)} traces created")
        
        # Test 5: Load test data si existe
        if os.path.exists('data/test_data.xlsx'):
            print("Testing data loading...")
            test_df = pd.read_excel('data/test_data.xlsx')
            # Mapear columnas
            column_mapping = {
                'Servicio': 'servicio',
                'Articulo': 'categoria',
                'Derechos': 'costo_unitario',
                'No. de trámites': 'num_tramites',
                'Importe USD': 'ingresos_totales',
                'Fecha recaudación': 'fecha_emision',
                'No. cancelados': 'formas_canceladas'
            }
            test_df = test_df.rename(columns=column_mapping)
            test_df = test_df.fillna(0)
            test_df['fecha_emision'] = pd.to_datetime(test_df['fecha_emision'])
            
            result = db.insert_data(test_df, 'test_functionality.xlsx')
            print(f"✓ Data loaded: {result['insertados']} records inserted, {result['duplicados']} duplicates")
            
            # Test analytics con datos reales
            new_kpis = analytics.get_kpis()
            print(f"✓ Analytics with data: ${new_kpis['total_ingresos']:,.2f} total, {new_kpis['total_tramites']} trámites")
        
        print("\n" + "=" * 60)
        print("✅ ALL BASIC TESTS PASSED!")
        print("🚀 System is ready for deployment")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_functionality()
    if success:
        print("\n🎉 You can now start the full application!")
        print("Run: python run_app.py")
    else:
        print("\n💡 Please fix the errors before proceeding.")
    exit(0 if success else 1)