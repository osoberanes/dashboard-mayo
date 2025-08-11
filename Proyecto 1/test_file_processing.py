import sys
import os
sys.path.append('backend')

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.product import Product, Category
from app.models.production import ProductionRecord, ImportBatch
from app.services.file_processor import FileProcessor

def test_file_processing():
    print("=== INICIANDO PRUEBA DE PROCESAMIENTO ===")
    
    # Crear base de datos temporal
    engine = create_engine("sqlite:///test_mayo.db", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Crear usuario de prueba
        user = User(
            username="test_user",
            email="test@test.com",
            full_name="Usuario de Prueba",
            hashed_password="test_hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Usuario creado: {user.username} (ID: {user.id})")
        
        # Procesar archivo
        processor = FileProcessor(db)
        print("\nIniciando procesamiento del archivo mayo.xls...")
        
        result = processor.process_excel_file("mayo.xls", user.id)
        
        print(f"\nResultado del procesamiento:")
        print(f"Éxito: {result['success']}")
        print(f"Mensaje: {result['message']}")
        
        if result['success']:
            print(f"Registros importados: {result['records_imported']}")
            print(f"Batch ID: {result['batch_id']}")
            
            # Verificar datos
            print("\n=== VERIFICACIÓN DE DATOS ===")
            
            # Contar registros
            total_records = db.query(ProductionRecord).count()
            total_products = db.query(Product).count()
            total_categories = db.query(Category).count()
            
            print(f"Total registros de producción: {total_records}")
            print(f"Total productos: {total_products}")
            print(f"Total categorías: {total_categories}")
            
            # Mostrar algunas categorías
            print("\nCategorías encontradas:")
            categories = db.query(Category).all()
            for cat in categories[:10]:  # Primeras 10
                print(f"- {cat.name}")
            
            # Mostrar algunos productos
            print("\nPrimeros productos:")
            products = db.query(Product).limit(5).all()
            for prod in products:
                print(f"- {prod.name} (Categoría: {prod.category.name if prod.category else 'N/A'})")
            
            # Mostrar estadísticas de ingresos
            print("\nEstadísticas de ingresos:")
            from sqlalchemy import func
            total_revenue = db.query(func.sum(ProductionRecord.revenue)).scalar()
            print(f"Ingresos totales: ${total_revenue:,.2f}" if total_revenue else "Ingresos totales: $0.00")
            
        else:
            print(f"Error: {result.get('error', 'Error desconocido')}")
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print("\n=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    test_file_processing()