"""
Test simple sin dependencias relativas complejas
"""
import sys
import os
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_database_creation():
    """Test básico de creación de base de datos"""
    print("Testing database creation...")
    
    import sqlite3
    from config.settings import settings
    
    # Verificar que la configuración se carga
    print(f"[OK] Config loaded: {settings.app.title}")
    
    # Crear BD de prueba
    test_db = "test_database.db"
    conn = sqlite3.connect(test_db)
    
    # Crear tabla simple
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL
        )
    """)
    
    # Insertar dato de prueba
    conn.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 123.45))
    conn.commit()
    
    # Verificar dato
    cursor = conn.execute("SELECT COUNT(*) FROM test_table")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    # Limpiar
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print(f"[OK] Database test passed: {count} record")
    return count > 0

def test_pandas_operations():
    """Test básico de pandas"""
    print("Testing pandas operations...")
    
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Crear DataFrame de prueba
    data = {
        'servicio': ['Test 1', 'Test 2', 'Test 3'],
        'ingresos': [100.0, 200.0, 150.0],
        'tramites': [5, 10, 7],
        'fecha': [datetime.now() - timedelta(days=i) for i in range(3)]
    }
    
    df = pd.DataFrame(data)
    
    # Operaciones básicas
    total_ingresos = df['ingresos'].sum()
    total_tramites = df['tramites'].sum()
    
    print(f"[OK] Pandas test passed: ${total_ingresos} total, {total_tramites} tramites")
    return True

def test_plotly_basic():
    """Test básico de Plotly"""
    print("Testing plotly basic...")
    
    import plotly.graph_objects as go
    
    # Crear gráfica simple
    fig = go.Figure(data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
    fig.update_layout(title='Test Chart')
    
    # Verificar que la gráfica tiene datos
    has_data = len(fig.data) > 0
    
    print(f"[OK] Plotly test passed: {len(fig.data)} traces")
    return has_data

def main():
    """Ejecutar todos los tests simples"""
    print("=" * 60)
    print("SIMPLE FUNCTIONALITY TESTS")
    print("=" * 60)
    
    tests = [
        test_database_creation,
        test_pandas_operations,
        test_plotly_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    if passed == total:
        print(f"[SUCCESS] ALL TESTS PASSED ({passed}/{total})")
        print("Core functionality is working")
    else:
        print(f"[WARNING] {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)