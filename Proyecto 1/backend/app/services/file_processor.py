import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import os
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from app.models.production import ProductionRecord, ImportBatch
from app.models.product import Product, Category

class FileProcessor:
    def __init__(self, db: Session):
        self.db = db
    
    def process_excel_file(self, file_path: str, user_id: int) -> Dict[str, Any]:
        try:
            # Detectar tipo de archivo
            df = self._read_file_data(file_path)
            
            batch = ImportBatch(
                filename=os.path.basename(file_path),
                file_path=file_path,
                imported_by=user_id,
                status="processing"
            )
            self.db.add(batch)
            self.db.commit()
            self.db.refresh(batch)
            
            processed_data = self._normalize_dataframe(df)
            records_imported = self._import_production_records(processed_data, batch.id)
            
            batch.records_imported = records_imported
            batch.status = "completed"
            self.db.commit()
            
            return {
                "success": True,
                "batch_id": batch.id,
                "records_imported": records_imported,
                "message": f"Successfully imported {records_imported} records"
            }
            
        except Exception as e:
            if 'batch' in locals():
                batch.status = "error"
                batch.error_message = str(e)
                self.db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Error processing file: {str(e)}"
            }
    
    def _read_file_data(self, file_path: str) -> pd.DataFrame:
        """Lee datos desde archivos Excel o HTML"""
        try:
            # Primero intentar como Excel
            return pd.read_excel(file_path, engine='openpyxl')
        except:
            try:
                # Si falla, intentar como Excel antiguo
                return pd.read_excel(file_path, engine='xlrd')
            except:
                try:
                    # Si falla, intentar como HTML con tablas
                    tables = pd.read_html(file_path, encoding='utf-8')
                    if tables:
                        # Retornar la tabla más grande (probablemente la principal)
                        return max(tables, key=lambda x: x.shape[0])
                    else:
                        raise ValueError("No se encontraron tablas en el archivo HTML")
                except:
                    raise ValueError(f"No se pudo leer el archivo {file_path}. Formato no soportado.")
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.lower().str.strip()
        
        # Mapeo de columnas general y específico para archivo gubernamental
        column_mapping = {
            # Mapeo general
            'fecha': 'production_date',
            'date': 'production_date',
            'producto': 'product_name',
            'product': 'product_name',
            'codigo': 'product_code',
            'code': 'product_code',
            'cantidad': 'quantity_produced',
            'quantity': 'quantity_produced',
            'vendido': 'quantity_sold',
            'sold': 'quantity_sold',
            'ingresos': 'revenue',
            'revenue': 'revenue',
            'costo': 'unit_cost',
            'cost': 'unit_cost',
            
            # Mapeo específico para archivo gubernamental
            'servicio': 'product_name',
            'concepto': 'product_category',
            'articulo': 'product_description',
            'no. de trámites': 'quantity_produced',
            'no. de tr�mites': 'quantity_produced',  # Con encoding issue
            'importe recaudación': 'revenue',
            'importe recaudaci�n': 'revenue',  # Con encoding issue
            'fecha recaudación': 'production_date',
            'fecha recaudaci�n': 'production_date',  # Con encoding issue
            'derechos': 'unit_cost',
            'moneda': 'currency'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Procesar fecha de producción
        if 'production_date' in df.columns:
            df['production_date'] = pd.to_datetime(df['production_date'], 
                                                   format='%d/%m/%Y', 
                                                   errors='coerce')
        
        # Si no hay cantidad vendida, asumir que lo producido es lo vendido
        if 'quantity_produced' in df.columns and 'quantity_sold' not in df.columns:
            df['quantity_sold'] = df['quantity_produced']
        
        # Limpiar valores numéricos
        numeric_columns = ['quantity_produced', 'quantity_sold', 'revenue', 'unit_cost']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Filtrar registros válidos
        valid_mask = True
        if 'production_date' in df.columns:
            valid_mask = valid_mask & df['production_date'].notna()
        if 'product_name' in df.columns:
            valid_mask = valid_mask & df['product_name'].notna()
        
        df = df[valid_mask]
        
        # Si tenemos descripción del producto pero no nombre, usar descripción como nombre
        if 'product_description' in df.columns and 'product_name' in df.columns:
            mask_no_name = df['product_name'].isna() | (df['product_name'] == '')
            df.loc[mask_no_name, 'product_name'] = df.loc[mask_no_name, 'product_description']
        
        return df
    
    def _import_production_records(self, df: pd.DataFrame, batch_id: int) -> int:
        records_imported = 0
        
        for _, row in df.iterrows():
            try:
                # Obtener o crear categoría si existe
                category = None
                if 'product_category' in row and pd.notna(row.get('product_category')):
                    category = self._get_or_create_category(row['product_category'])
                
                # Obtener o crear producto
                product = self._get_or_create_product(
                    name=row.get('product_name', ''),
                    code=row.get('product_code', ''),
                    description=row.get('product_description', ''),
                    category=category
                )
                
                # Crear registro de producción
                production_date = row.get('production_date')
                if pd.isna(production_date):
                    continue  # Skip records without date
                
                production_record = ProductionRecord(
                    product_id=product.id,
                    production_date=production_date.date() if hasattr(production_date, 'date') else production_date,
                    quantity_produced=int(row.get('quantity_produced', 0)),
                    quantity_sold=int(row.get('quantity_sold', 0)),
                    revenue=float(row.get('revenue', 0)),
                    unit_cost=float(row.get('unit_cost', 0))
                )
                
                self.db.add(production_record)
                records_imported += 1
                
                # Commit cada 50 registros para evitar problemas de memoria
                if records_imported % 50 == 0:
                    self.db.commit()
                
            except Exception as e:
                self.db.rollback()  # Rollback on error
                print(f"Error processing row {records_imported + 1}: {e}")
                continue
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error final commit: {e}")
        
        return records_imported
    
    def _get_or_create_product(self, name: str, code: str = '', description: str = '', category: Category = None) -> Product:
        # Buscar por código primero
        if code:
            product = self.db.query(Product).filter(Product.code == code).first()
            if product:
                return product
        
        # Buscar por nombre
        if name:
            product = self.db.query(Product).filter(Product.name == name).first()
            if product:
                return product
        
        # Crear nuevo producto
        if not category:
            category = self._get_or_create_default_category()
        
        # Generar código único si no se proporciona
        if not code:
            import hashlib
            # Crear código basado en el nombre para evitar duplicados
            code = f"PROD_{hashlib.md5(name.encode()).hexdigest()[:8].upper()}"
        
        product = Product(
            name=name or f"Producto {code}",
            code=code,
            description=description,
            category_id=category.id
        )
        
        self.db.add(product)
        try:
            self.db.commit()
            self.db.refresh(product)
        except Exception as e:
            self.db.rollback()
            # Si hay conflicto, buscar el producto existente
            product = self.db.query(Product).filter(
                (Product.code == code) | (Product.name == name)
            ).first()
            if not product:
                raise e
        
        return product
    
    def _get_or_create_category(self, name: str) -> Category:
        """Obtiene o crea una categoría"""
        category = self.db.query(Category).filter(Category.name == name).first()
        if not category:
            category = Category(
                name=name,
                description=f"Categoría creada automáticamente: {name}"
            )
            self.db.add(category)
            try:
                self.db.commit()
                self.db.refresh(category)
            except Exception as e:
                self.db.rollback()
                # Si hay conflicto, buscar la categoría existente
                category = self.db.query(Category).filter(Category.name == name).first()
                if not category:
                    raise e
        
        return category
    
    def _get_or_create_default_category(self) -> Category:
        category = self.db.query(Category).filter(Category.name == "Sin Categoría").first()
        if not category:
            category = Category(
                name="Sin Categoría",
                description="Categoría por defecto para productos importados"
            )
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
        
        return category