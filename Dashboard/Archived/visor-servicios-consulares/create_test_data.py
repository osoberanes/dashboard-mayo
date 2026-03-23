"""
Script para crear datos de prueba si no hay archivo original
"""
import pandas as pd
import os
from datetime import datetime, timedelta
import random

def create_test_data():
    """Crea datos de prueba para testing"""
    
    # Servicios de ejemplo
    services = [
        'Pasaporte Ordinario', 'Pasaporte Urgente', 
        'RCM Expedición', 'RCM Renovación',
        'Apostilla Documento', 'Legalización',
        'Constancia Consular', 'Carta Poder'
    ]
    
    categories = [
        'PASAPORTES', 'PASAPORTES',
        'RCM', 'RCM',
        'NOTARIALES', 'NOTARIALES',
        'SERVICIOS CONSULARES', 'SERVICIOS CONSULARES'
    ]
    
    costs = [165, 200, 30, 30, 50, 40, 25, 35]
    
    # Generar datos para los últimos 6 meses
    start_date = datetime.now() - timedelta(days=180)
    data = []
    
    for i in range(300):  # 300 registros de prueba
        date = start_date + timedelta(days=random.randint(0, 180))
        service_idx = random.randint(0, len(services) - 1)
        
        tramites = random.randint(1, 25)
        costo = costs[service_idx]
        ingresos = tramites * costo
        cancelados = random.randint(0, max(1, tramites // 5))
        
        data.append({
            'Servicio': services[service_idx],
            'Articulo': categories[service_idx],
            'Derechos': costo,
            'No. de trámites': tramites,
            'Importe USD': ingresos,
            'Fecha recaudación': date.strftime('%Y-%m-%d'),
            'No. cancelados': cancelados
        })
    
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    print("Creando datos de prueba...")
    
    # Verificar si existe archivo original
    original_file = 'data/mayo_test.xls'
    if os.path.exists(original_file):
        print(f"Archivo original encontrado: {original_file}")
    else:
        print("Creando archivo de datos de prueba...")
        
        # Crear directorio si no existe
        os.makedirs('data', exist_ok=True)
        
        # Generar y guardar datos
        test_data = create_test_data()
        test_data.to_excel('data/test_data.xlsx', index=False)
        
        print(f"Archivo de prueba creado: data/test_data.xlsx")
        print(f"Registros generados: {len(test_data)}")
    
    print("Datos listos para testing")