# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el funcionamiento del PDF con servicios específicos
"""

import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor
from service_name_mappings import service_mapper, get_short_service_name

def test_service_pdf_generation():
    """Prueba la generación de PDF con servicios específicos"""
    
    print("Iniciando prueba de servicios para PDF...")
    
    # Inicializar procesador
    processor = EnhancedDataProcessor()
    if not processor.initialize_from_database():
        print("Error: No se pudieron cargar los datos de la base de datos")
        return False
    
    print(f"Datos cargados: {len(processor.df)} registros")
    
    # Obtener servicios únicos
    services_list = sorted(processor.df['servicio'].unique().tolist())
    print(f"📋 Total de servicios únicos: {len(services_list)}")
    
    # Obtener top 10 servicios por frecuencia
    service_counts = processor.df['servicio'].value_counts().head(10)
    top_services = service_counts.index.tolist()
    
    print("\n🏆 Top 10 servicios más frecuentes:")
    for i, service in enumerate(top_services, 1):
        short_name = get_short_service_name(service)
        count = service_counts[service]
        print(f"{i:2d}. {service[:60]}{'...' if len(service) > 60 else ''}")
        print(f"    📊 Frecuencia: {count} registros")
        print(f"    🔗 Nombre corto: {short_name}")
        
        # Verificar si hay datos para este servicio
        service_data = processor.df[processor.df['servicio'] == service]
        total_ingresos = service_data['ingresos_totales'].sum()
        total_tramites = service_data['num_tramites'].sum()
        
        print(f"    💰 Ingresos totales: ${total_ingresos:,.2f}")
        print(f"    📝 Trámites totales: {total_tramites:,}")
        print()
    
    # Buscar específicamente "nacimientos" o servicios relacionados
    birth_services = []
    for service in services_list:
        if any(keyword in service.lower() for keyword in ['nacimiento', 'birth', 'acta de nacimiento', 'certificado de nacimiento']):
            birth_services.append(service)
    
    if birth_services:
        print("👶 Servicios relacionados con nacimientos encontrados:")
        for service in birth_services:
            short_name = get_short_service_name(service)
            service_data = processor.df[processor.df['servicio'] == service]
            count = len(service_data)
            print(f"  • {service}")
            print(f"    🔗 Nombre corto: {short_name}")
            print(f"    📊 Registros: {count}")
            
            if count > 0:
                total_ingresos = service_data['ingresos_totales'].sum()
                total_tramites = service_data['num_tramites'].sum()
                print(f"    💰 Ingresos: ${total_ingresos:,.2f}")
                print(f"    📝 Trámites: {total_tramites:,}")
            print()
    else:
        print("👶 No se encontraron servicios relacionados con nacimientos")
        
        # Buscar servicios que podrían estar mapeados incorrectamente
        print("\n🔍 Buscando servicios que contengan palabras clave...")
        keywords = ['registro', 'civil', 'documento', 'certificado', 'constancia']
        
        for keyword in keywords:
            matching_services = [s for s in services_list if keyword.lower() in s.lower()]
            if matching_services:
                print(f"\n🔑 Servicios que contienen '{keyword}':")
                for service in matching_services[:5]:  # Solo mostrar los primeros 5
                    short_name = get_short_service_name(service)
                    count = len(processor.df[processor.df['servicio'] == service])
                    print(f"  • {service[:50]}{'...' if len(service) > 50 else ''}")
                    print(f"    🔗 Nombre corto: {short_name}")
                    print(f"    📊 Registros: {count}")
    
    # Verificar mapeos existentes
    mappings = service_mapper.get_all_mappings()
    print(f"\n🗺️ Mapeos de nombres configurados: {len(mappings)}")
    
    if mappings:
        print("📝 Mapeos existentes:")
        for original, short in list(mappings.items())[:10]:  # Mostrar solo los primeros 10
            print(f"  • {original[:40]}{'...' if len(original) > 40 else ''} → {short}")
    
    return True

def test_specific_service_data(service_name):
    """Prueba datos de un servicio específico"""
    print(f"\n🔬 Analizando servicio específico: {service_name}")
    
    processor = EnhancedDataProcessor()
    if not processor.initialize_from_database():
        print("❌ Error cargando datos")
        return False
    
    # Buscar el servicio exacto o similar
    exact_match = processor.df[processor.df['servicio'] == service_name]
    
    if not exact_match.empty:
        print(f"✅ Encontrado servicio exacto: {len(exact_match)} registros")
        
        total_ingresos = exact_match['ingresos_totales'].sum()
        total_tramites = exact_match['num_tramites'].sum()
        
        print(f"💰 Ingresos totales: ${total_ingresos:,.2f}")
        print(f"📝 Trámites totales: {total_tramites:,}")
        
        # Verificar fechas
        exact_match_copy = exact_match.copy()
        exact_match_copy['fecha_emision'] = pd.to_datetime(exact_match_copy['fecha_emision'])
        fecha_min = exact_match_copy['fecha_emision'].min()
        fecha_max = exact_match_copy['fecha_emision'].max()
        
        print(f"📅 Rango de fechas: {fecha_min.strftime('%Y-%m-%d')} a {fecha_max.strftime('%Y-%m-%d')}")
        
        return True
    else:
        # Buscar servicios similares
        similar_services = []
        search_terms = service_name.lower().split()
        
        for service in processor.df['servicio'].unique():
            service_lower = service.lower()
            if any(term in service_lower for term in search_terms):
                similar_services.append(service)
        
        if similar_services:
            print(f"🔍 No se encontró exacto, pero hay servicios similares:")
            for similar in similar_services[:5]:
                count = len(processor.df[processor.df['servicio'] == similar])
                print(f"  • {similar} ({count} registros)")
        else:
            print("❌ No se encontraron servicios similares")
            
        return False

if __name__ == "__main__":
    import pandas as pd
    
    print("PRUEBA DE SERVICIOS PARA PDF")
    print("="*50)
    
    success = test_service_pdf_generation()
    
    print("\n" + "="*50)
    
    if success:
        print("✅ Prueba completada exitosamente")
        
        # Probar servicios específicos comunes
        test_services = [
            "EXPEDICION DE PASAPORTE ORDINARIO",
            "RENOVACION DE MATRICULA CONSULAR", 
            "LEGALIZACION DE DOCUMENTOS",
            "ACTA DE NACIMIENTO",
            "CERTIFICADO DE NACIMIENTO"
        ]
        
        for service in test_services:
            test_specific_service_data(service)
            
    else:
        print("❌ Prueba fallida")