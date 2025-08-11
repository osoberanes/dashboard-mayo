import pandas as pd
from bs4 import BeautifulSoup
import sys

def analyze_html_file():
    try:
        print("Analizando archivo HTML mayo.xls...")
        
        # Leer el archivo HTML
        with open('mayo.xls', 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        print("Contenido HTML leído correctamente")
        print(f"Longitud del contenido: {len(html_content)} caracteres")
        
        # Intentar extraer tablas con pandas
        try:
            tables = pd.read_html('mayo.xls')
            print(f"Encontradas {len(tables)} tablas")
            
            for i, table in enumerate(tables):
                print(f"\n=== TABLA {i+1} ===")
                print(f"Dimensiones: {table.shape}")
                print("Primeras columnas:", list(table.columns)[:5])
                print("Primeras 3 filas:")
                print(table.head(3))
                
                if table.shape[0] > 10:  # Si tiene muchas filas, es probablemente la tabla principal
                    print(f"\nEsta parece ser la tabla principal con {table.shape[0]} registros")
                    return table
                    
        except Exception as e:
            print(f"Error usando pandas.read_html: {e}")
            
            # Método alternativo con BeautifulSoup
            print("Intentando método alternativo con BeautifulSoup...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            tables = soup.find_all('table')
            print(f"Encontradas {len(tables)} tablas HTML")
            
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"Tabla {i+1}: {len(rows)} filas")
                
                if len(rows) > 5:  # Tabla con contenido significativo
                    print(f"Analizando tabla {i+1}...")
                    
                    # Extraer headers
                    headers = []
                    first_row = rows[0]
                    headers = [th.get_text().strip() for th in first_row.find_all(['th', 'td'])]
                    print("Headers encontrados:", headers)
                    
                    # Extraer algunas filas de datos
                    data_rows = []
                    for row in rows[1:4]:  # Primeras 3 filas de datos
                        cells = [td.get_text().strip() for td in row.find_all('td')]
                        if cells:
                            data_rows.append(cells)
                    
                    print("Primeras filas de datos:")
                    for j, row in enumerate(data_rows):
                        print(f"Fila {j+1}: {row[:5]}...")  # Primeras 5 columnas
                    
                    return None
        
    except Exception as e:
        print(f'Error general: {e}')
        print(f'Tipo de error: {type(e).__name__}')
        return None

if __name__ == "__main__":
    analyze_html_file()