#!/usr/bin/env python3
"""
Script de diagnostico para verificar la configuracion del sistema
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Probar que todos los imports funcionen"""
    print("[1/4] Probando imports...")
    try:
        from app.core.database import engine, Base
        from app.models import user, product, production
        from app.core.config import settings
        print("OK - Imports exitosos")
        return True
    except ImportError as e:
        print(f"ERROR - Error en imports: {e}")
        return False

def test_database():
    """Probar conexion a base de datos"""
    print("[2/4] Probando base de datos...")
    try:
        from app.core.database import engine, Base
        from sqlalchemy import text
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Probar conexion
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("OK - Base de datos conectada")
            return True
    except Exception as e:
        print(f"ERROR - Error de base de datos: {e}")
        return False

def test_frontend_files():
    """Verificar archivos de frontend"""
    print("[3/4] Verificando frontend...")
    frontend_files = [
        'frontend/index.html',
        'frontend/static/css/styles.css',
        'frontend/static/js/app.js'
    ]
    
    all_exist = True
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"OK - {file_path}")
        else:
            print(f"ERROR - Falta: {file_path}")
            all_exist = False
    
    return all_exist

def test_config():
    """Verificar configuracion"""
    print("[4/4] Verificando configuracion...")
    try:
        from app.core.config import settings
        print(f"OK - DATABASE_URL: {settings.database_url}")
        print(f"OK - UPLOAD_DIR: {settings.upload_dir}")
        key_status = 'Si' if settings.secret_key != 'your-super-secret-key-here' else 'Usando clave por defecto'
        print(f"OK - SECRET_KEY configurado: {key_status}")
        return True
    except Exception as e:
        print(f"ERROR - Error de configuracion: {e}")
        return False

def main():
    print("Sistema de Analisis de Produccion - Diagnostico")
    print("="*50)
    
    tests = [
        ("Imports", test_imports),
        ("Base de datos", test_database),
        ("Archivos frontend", test_frontend_files),
        ("Configuracion", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n[{name}]:")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("EXITO: Todo esta funcionando correctamente!")
        print("Puedes acceder al sistema en: http://localhost:8000")
    else:
        print("ADVERTENCIA: Hay algunos problemas que necesitan resolverse.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)