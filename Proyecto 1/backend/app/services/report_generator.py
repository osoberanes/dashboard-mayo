import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, Optional
import io
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product, Category
from app.models.production import ProductionRecord

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_performance_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        format: str = "excel"
    ) -> bytes:
        
        query = self.db.query(
            Product.name.label('Producto'),
            Category.name.label('Categoría'),
            func.sum(ProductionRecord.quantity_produced).label('Total_Producido'),
            func.sum(ProductionRecord.quantity_sold).label('Total_Vendido'),
            func.sum(ProductionRecord.revenue).label('Ingresos_Totales'),
            func.avg(ProductionRecord.quantity_produced).label('Producción_Promedio_Diaria'),
            func.avg(ProductionRecord.unit_cost).label('Costo_Promedio')
        ).join(Product).join(Category)
        
        if start_date:
            query = query.filter(ProductionRecord.production_date >= start_date)
        if end_date:
            query = query.filter(ProductionRecord.production_date <= end_date)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        results = query.group_by(Product.name, Category.name).all()
        
        df = pd.DataFrame([
            {
                'Producto': r.Producto,
                'Categoría': r.Categoría,
                'Total Producido': r.Total_Producido or 0,
                'Total Vendido': r.Total_Vendido or 0,
                'Ingresos Totales': round(r.Ingresos_Totales or 0, 2),
                'Producción Promedio Diaria': round(r.Producción_Promedio_Diaria or 0, 2),
                'Costo Promedio': round(r.Costo_Promedio or 0, 2),
                'Tasa de Conversión (%)': round(
                    (r.Total_Vendido / r.Total_Producido * 100) if r.Total_Producido else 0, 2
                ),
                'Ganancia por Unidad': round(
                    (r.Ingresos_Totales / r.Total_Vendido) - (r.Costo_Promedio or 0)
                    if r.Total_Vendido else 0, 2
                )
            }
            for r in results
        ])
        
        if format.lower() == "excel":
            return self._dataframe_to_excel(df, "Reporte de Performance")
        else:
            return self._dataframe_to_csv(df)
    
    def generate_trends_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        product_id: Optional[int] = None,
        period: str = "daily",
        format: str = "excel"
    ) -> bytes:
        
        if period == "weekly":
            date_trunc = func.date_trunc('week', ProductionRecord.production_date)
        elif period == "monthly":
            date_trunc = func.date_trunc('month', ProductionRecord.production_date)
        else:
            date_trunc = ProductionRecord.production_date
        
        query = self.db.query(
            date_trunc.label('Período'),
            func.sum(ProductionRecord.quantity_produced).label('Total_Producido'),
            func.sum(ProductionRecord.quantity_sold).label('Total_Vendido'),
            func.sum(ProductionRecord.revenue).label('Ingresos'),
            func.count(func.distinct(ProductionRecord.product_id)).label('Productos_Activos')
        ).join(Product)
        
        if start_date:
            query = query.filter(ProductionRecord.production_date >= start_date)
        if end_date:
            query = query.filter(ProductionRecord.production_date <= end_date)
        if product_id:
            query = query.filter(ProductionRecord.product_id == product_id)
        
        results = query.group_by(date_trunc).order_by(date_trunc).all()
        
        df = pd.DataFrame([
            {
                'Período': r.Período.strftime('%Y-%m-%d'),
                'Total Producido': r.Total_Producido or 0,
                'Total Vendido': r.Total_Vendido or 0,
                'Ingresos': round(r.Ingresos or 0, 2),
                'Productos Activos': r.Productos_Activos or 0,
                'Tasa de Conversión (%)': round(
                    (r.Total_Vendido / r.Total_Producido * 100) if r.Total_Producido else 0, 2
                )
            }
            for r in results
        ])
        
        if format.lower() == "excel":
            return self._dataframe_to_excel(df, f"Tendencias {period.title()}")
        else:
            return self._dataframe_to_csv(df)
    
    def generate_category_summary_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        format: str = "excel"
    ) -> bytes:
        
        query = self.db.query(
            Category.name.label('Categoría'),
            func.count(func.distinct(Product.id)).label('Número_Productos'),
            func.sum(ProductionRecord.quantity_produced).label('Total_Producido'),
            func.sum(ProductionRecord.quantity_sold).label('Total_Vendido'),
            func.sum(ProductionRecord.revenue).label('Ingresos_Totales'),
            func.avg(ProductionRecord.revenue / ProductionRecord.quantity_sold).label('Precio_Promedio')
        ).join(Product).join(ProductionRecord)
        
        if start_date:
            query = query.filter(ProductionRecord.production_date >= start_date)
        if end_date:
            query = query.filter(ProductionRecord.production_date <= end_date)
        
        results = query.group_by(Category.name).all()
        
        df = pd.DataFrame([
            {
                'Categoría': r.Categoría,
                'Número de Productos': r.Número_Productos or 0,
                'Total Producido': r.Total_Producido or 0,
                'Total Vendido': r.Total_Vendido or 0,
                'Ingresos Totales': round(r.Ingresos_Totales or 0, 2),
                'Precio Promedio': round(r.Precio_Promedio or 0, 2),
                'Participación en Ventas (%)': 0  # Se calculará después
            }
            for r in results
        ])
        
        # Calcular participación en ventas
        total_revenue = df['Ingresos Totales'].sum()
        if total_revenue > 0:
            df['Participación en Ventas (%)'] = (df['Ingresos Totales'] / total_revenue * 100).round(2)
        
        if format.lower() == "excel":
            return self._dataframe_to_excel(df, "Resumen por Categorías")
        else:
            return self._dataframe_to_csv(df)
    
    def generate_complete_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> bytes:
        
        # Performance report
        performance_df = self._get_performance_dataframe(start_date, end_date)
        
        # Trends report
        trends_df = self._get_trends_dataframe(start_date, end_date)
        
        # Category summary
        category_df = self._get_category_summary_dataframe(start_date, end_date)
        
        # Create Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            performance_df.to_excel(writer, sheet_name='Performance por Producto', index=False)
            trends_df.to_excel(writer, sheet_name='Tendencias Diarias', index=False)
            category_df.to_excel(writer, sheet_name='Resumen por Categorías', index=False)
            
            # Add summary sheet
            summary_data = self._get_summary_data(start_date, end_date)
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name='Resumen General', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def _dataframe_to_excel(self, df: pd.DataFrame, sheet_name: str) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output.getvalue()
    
    def _dataframe_to_csv(self, df: pd.DataFrame) -> bytes:
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        return output.getvalue().encode('utf-8')
    
    def _get_performance_dataframe(self, start_date: Optional[date], end_date: Optional[date]):
        # Similar logic to generate_performance_report but returns DataFrame
        pass
    
    def _get_trends_dataframe(self, start_date: Optional[date], end_date: Optional[date]):
        # Similar logic to generate_trends_report but returns DataFrame
        pass
    
    def _get_category_summary_dataframe(self, start_date: Optional[date], end_date: Optional[date]):
        # Similar logic to generate_category_summary_report but returns DataFrame
        pass
    
    def _get_summary_data(self, start_date: Optional[date], end_date: Optional[date]) -> Dict[str, Any]:
        total_metrics = self.db.query(
            func.sum(ProductionRecord.quantity_produced).label('total_produced'),
            func.sum(ProductionRecord.quantity_sold).label('total_sold'),
            func.sum(ProductionRecord.revenue).label('total_revenue'),
            func.count(func.distinct(ProductionRecord.product_id)).label('active_products')
        )
        
        if start_date:
            total_metrics = total_metrics.filter(ProductionRecord.production_date >= start_date)
        if end_date:
            total_metrics = total_metrics.filter(ProductionRecord.production_date <= end_date)
        
        result = total_metrics.first()
        
        return {
            'Período Inicio': start_date.isoformat() if start_date else 'N/A',
            'Período Fin': end_date.isoformat() if end_date else 'N/A',
            'Total Producido': result.total_produced or 0,
            'Total Vendido': result.total_sold or 0,
            'Ingresos Totales': round(result.total_revenue or 0, 2),
            'Productos Activos': result.active_products or 0,
            'Tasa de Conversión Global (%)': round(
                (result.total_sold / result.total_produced * 100) if result.total_produced else 0, 2
            ),
            'Fecha de Generación': datetime.now().isoformat()
        }