"""
Script de ejecución principal del Visor de Servicios Consulares
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar y ejecutar la aplicación
from app import main

if __name__ == '__main__':
    main()