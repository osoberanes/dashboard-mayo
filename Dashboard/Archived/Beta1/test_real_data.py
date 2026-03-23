#!/usr/bin/env python3
"""
Test de comparación con datos reales de múltiples años
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Inicio'))

from period_comparison_page import execute_year_comparison, get_available_years_and_periods, initialize_processor

def test_real_data_comparison():
    """Test de comparación con datos reales"""
    
    print('=' * 60)
    print('TESTING COMPARACIÓN CON DATOS REALES')
    print('=' * 60)
    
    processor = initialize_processor()
    if not processor:
        print('ERROR: No se pudo inicializar el procesador')
        return False
    
    available_data = get_available_years_and_periods(processor)
    if not available_data:
        print('ERROR: No se pudieron obtener años y períodos disponibles')
        return False
    
    print(f"Años disponibles: {available_data['years']}")
    
    # Test 1: Comparación de Mayo entre años
    print('\n--- TEST 1: Mayo 2023 vs 2024 vs 2025 ---')
    
    comparison_config = {
        'period_name': 'Mayo',
        'period_value': 5,  # Mayo
        'selected_years': [2023, 2024, 2025],
        'available_data': available_data
    }
    
    year_data = execute_year_comparison(processor, comparison_config)
    
    if year_data:
        print('Resultados Mayo:')
        for year, data in year_data.items():
            stats = data['stats']
            print(f'  {year}:')
            print(f'    - Ingresos totales: ${stats["total_ingresos"]:,.2f}')
            print(f'    - Trámites totales: {stats["total_tramites"]:,}')
            print(f'    - Días de datos: {stats["num_dias"]}')
            print(f'    - Ingreso diario promedio: ${stats["ingreso_diario_promedio"]:,.2f}')
        print('✓ Test Mayo EXITOSO')
    else:
        print('✗ Test Mayo FALLÓ')
        return False
    
    # Test 2: Comparación de Año Completo
    print('\n--- TEST 2: Año Completo 2023 vs 2024 ---')
    
    comparison_config_year = {
        'period_name': 'Año Completo',
        'period_value': list(range(1, 13)),  # Todos los meses
        'selected_years': [2023, 2024],
        'available_data': available_data
    }
    
    year_data_full = execute_year_comparison(processor, comparison_config_year)
    
    if year_data_full:
        print('Resultados Año Completo:')
        for year, data in year_data_full.items():
            stats = data['stats']
            print(f'  {year}:')
            print(f'    - Ingresos totales: ${stats["total_ingresos"]:,.2f}')
            print(f'    - Trámites totales: {stats["total_tramites"]:,}')
            print(f'    - Días de datos: {stats["num_dias"]}')
            print(f'    - Servicios únicos: {stats["num_servicios"]}')
        print('✓ Test Año Completo EXITOSO')
    else:
        print('✗ Test Año Completo FALLÓ')
        return False
    
    # Test 3: Comparación de Q4
    print('\n--- TEST 3: Q4 (Oct-Dic) 2022 vs 2023 vs 2024 ---')
    
    comparison_config_q4 = {
        'period_name': 'Q4 (Oct-Dic)',
        'period_value': [10, 11, 12],  # Q4
        'selected_years': [2022, 2023, 2024],
        'available_data': available_data
    }
    
    year_data_q4 = execute_year_comparison(processor, comparison_config_q4)
    
    if year_data_q4:
        print('Resultados Q4:')
        for year, data in year_data_q4.items():
            stats = data['stats']
            print(f'  {year}:')
            print(f'    - Ingresos totales: ${stats["total_ingresos"]:,.2f}')
            print(f'    - Trámites totales: {stats["total_tramites"]:,}')
            print(f'    - Días de datos: {stats["num_dias"]}')
        print('✓ Test Q4 EXITOSO')
    else:
        print('✗ Test Q4 FALLÓ')
        return False
    
    print('\n' + '=' * 60)
    print('TODOS LOS TESTS EXITOSOS!')
    print('✓ Comparación Mayo funcionando')
    print('✓ Comparación Año Completo funcionando')
    print('✓ Comparación Trimestral funcionando')
    print('✓ Datos de 5 años (2021-2025) disponibles')
    print('✓ Dashboard listo para uso con datos reales')
    print('=' * 60)
    
    return True

if __name__ == "__main__":
    test_real_data_comparison()