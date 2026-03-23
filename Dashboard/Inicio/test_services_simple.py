# -*- coding: utf-8 -*-
"""
Script simple para probar servicios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor
from service_name_mappings import service_mapper, get_short_service_name

def main():
    print("=== PRUEBA DE SERVICIOS PARA PDF ===")
    
    # Inicializar procesador
    processor = EnhancedDataProcessor()
    if not processor.initialize_from_database():
        print("ERROR: No se pudieron cargar los datos")
        return False
    
    print(f"Datos cargados: {len(processor.df)} registros")
    
    # Top 10 servicios por frecuencia
    service_counts = processor.df['servicio'].value_counts().head(10)
    print("\nTOP 10 SERVICIOS MAS FRECUENTES:")
    print("-" * 60)
    
    for i, (service, count) in enumerate(service_counts.items(), 1):
        short_name = get_short_service_name(service)
        service_data = processor.df[processor.df['servicio'] == service]
        total_ingresos = service_data['ingresos_totales'].sum()
        total_tramites = service_data['num_tramites'].sum()
        
        print(f"{i:2d}. {service[:50]}...")
        print(f"    Frecuencia: {count} registros")
        print(f"    Nombre corto: {short_name}")
        print(f"    Ingresos: ${total_ingresos:,.2f}")
        print(f"    Tramites: {total_tramites:,}")
        print()
    
    # Buscar servicios de nacimientos
    birth_keywords = ['nacimiento', 'birth', 'acta de nacimiento', 'certificado de nacimiento']
    birth_services = []
    
    for service in processor.df['servicio'].unique():
        if any(keyword.lower() in service.lower() for keyword in birth_keywords):
            birth_services.append(service)
    
    print(f"\nSERVICIOS DE NACIMIENTOS ENCONTRADOS: {len(birth_services)}")
    print("-" * 60)
    
    if birth_services:
        for service in birth_services:
            short_name = get_short_service_name(service)
            service_data = processor.df[processor.df['servicio'] == service]
            count = len(service_data)
            
            print(f"Servicio: {service}")
            print(f"Nombre corto: {short_name}")
            print(f"Registros: {count}")
            
            if count > 0:
                total_ingresos = service_data['ingresos_totales'].sum()
                total_tramites = service_data['num_tramites'].sum()
                print(f"Ingresos: ${total_ingresos:,.2f}")
                print(f"Tramites: {total_tramites:,}")
            print()
    else:
        print("No se encontraron servicios relacionados con nacimientos")
    
    # Verificar mapeos
    mappings = service_mapper.get_all_mappings()
    print(f"\nMAPEOS CONFIGURADOS: {len(mappings)}")
    print("-" * 60)
    
    if mappings:
        for i, (original, short) in enumerate(list(mappings.items())[:5], 1):
            print(f"{i}. {original[:40]}... -> {short}")
    
    return True

if __name__ == "__main__":
    import pandas as pd
    main()