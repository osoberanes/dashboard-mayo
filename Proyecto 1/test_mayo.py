import pandas as pd
import sys
import os

def analyze_mayo_file():
    try:
        # Intentar leer el archivo Excel
        print("Intentando leer mayo.xls...")
        df = pd.read_excel('mayo.xls', engine='xlrd')
        
        print('=== ESTRUCTURA DEL ARCHIVO MAYO.XLS ===')
        print(f'Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas')
        print(f'Columnas: {list(df.columns)}')
        print()
        
        print('=== PRIMERAS 5 FILAS ===')
        print(df.head())
        print()
        
        print('=== TIPOS DE DATOS ===')
        print(df.dtypes)
        print()
        
        print('=== VALORES NULOS ===')
        print(df.isnull().sum())
        print()
        
        print('=== ESTADÍSTICAS BÁSICAS ===')
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(df[numeric_cols].describe())
        
        return True
        
    except Exception as e:
        print(f'Error al leer el archivo: {e}')
        print(f'Tipo de error: {type(e).__name__}')
        return False

if __name__ == "__main__":
    analyze_mayo_file()