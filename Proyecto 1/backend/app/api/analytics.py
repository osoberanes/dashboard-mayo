from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.product import Product, Category
from app.models.production import ProductionRecord

router = APIRouter()

class ProductPerformance(BaseModel):
    product_id: int
    product_name: str
    category_name: str
    total_produced: int
    total_sold: int
    total_revenue: float
    avg_daily_production: float
    sell_through_rate: float

class TrendData(BaseModel):
    date: str
    value: float

class CategorySummary(BaseModel):
    category_name: str
    product_count: int
    total_revenue: float
    total_production: int

@router.get("/performance", response_model=List[ProductPerformance])
async def get_product_performance(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(
        ProductionRecord.product_id,
        Product.name.label('product_name'),
        Category.name.label('category_name'),
        func.sum(ProductionRecord.quantity_produced).label('total_produced'),
        func.sum(ProductionRecord.quantity_sold).label('total_sold'),
        func.sum(ProductionRecord.revenue).label('total_revenue'),
        func.avg(ProductionRecord.quantity_produced).label('avg_daily_production')
    ).join(Product).join(Category)
    
    if start_date:
        query = query.filter(ProductionRecord.production_date >= start_date)
    if end_date:
        query = query.filter(ProductionRecord.production_date <= end_date)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    results = query.group_by(
        ProductionRecord.product_id, 
        Product.name, 
        Category.name
    ).order_by(desc('total_revenue')).limit(limit).all()
    
    performance_data = []
    for result in results:
        sell_through_rate = (result.total_sold / result.total_produced * 100) if result.total_produced > 0 else 0
        
        performance_data.append(ProductPerformance(
            product_id=result.product_id,
            product_name=result.product_name,
            category_name=result.category_name,
            total_produced=result.total_produced or 0,
            total_sold=result.total_sold or 0,
            total_revenue=result.total_revenue or 0,
            avg_daily_production=round(result.avg_daily_production or 0, 2),
            sell_through_rate=round(sell_through_rate, 2)
        ))
    
    return performance_data

@router.get("/trends/revenue")
async def get_revenue_trends(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    period: str = "daily",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    if period == "weekly":
        date_trunc = func.date_trunc('week', ProductionRecord.production_date)
    elif period == "monthly":
        date_trunc = func.date_trunc('month', ProductionRecord.production_date)
    else:
        date_trunc = ProductionRecord.production_date
    
    query = db.query(
        date_trunc.label('period'),
        func.sum(ProductionRecord.revenue).label('total_revenue')
    ).join(Product)
    
    if product_id:
        query = query.filter(ProductionRecord.product_id == product_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    query = query.filter(
        ProductionRecord.production_date >= start_date,
        ProductionRecord.production_date <= end_date
    ).group_by(date_trunc).order_by(date_trunc)
    
    results = query.all()
    
    trends = [
        TrendData(
            date=result.period.isoformat(),
            value=float(result.total_revenue or 0)
        )
        for result in results
    ]
    
    return {"trends": trends, "period": period}

@router.get("/summary")
async def get_dashboard_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Overall metrics
    total_metrics = db.query(
        func.sum(ProductionRecord.quantity_produced).label('total_produced'),
        func.sum(ProductionRecord.quantity_sold).label('total_sold'),
        func.sum(ProductionRecord.revenue).label('total_revenue'),
        func.count(func.distinct(ProductionRecord.product_id)).label('active_products')
    ).filter(
        ProductionRecord.production_date >= start_date,
        ProductionRecord.production_date <= end_date
    ).first()
    
    # Category breakdown
    category_data = db.query(
        Category.name.label('category_name'),
        func.count(func.distinct(Product.id)).label('product_count'),
        func.sum(ProductionRecord.revenue).label('total_revenue'),
        func.sum(ProductionRecord.quantity_produced).label('total_production')
    ).join(Product).join(ProductionRecord).filter(
        ProductionRecord.production_date >= start_date,
        ProductionRecord.production_date <= end_date
    ).group_by(Category.name).all()
    
    categories = [
        CategorySummary(
            category_name=cat.category_name,
            product_count=cat.product_count,
            total_revenue=float(cat.total_revenue or 0),
            total_production=cat.total_production or 0
        )
        for cat in category_data
    ]
    
    # Top performing products
    top_products = db.query(
        Product.name,
        func.sum(ProductionRecord.revenue).label('revenue')
    ).join(ProductionRecord).filter(
        ProductionRecord.production_date >= start_date,
        ProductionRecord.production_date <= end_date
    ).group_by(Product.name).order_by(desc('revenue')).limit(5).all()
    
    return {
        "summary": {
            "total_produced": total_metrics.total_produced or 0,
            "total_sold": total_metrics.total_sold or 0,
            "total_revenue": float(total_metrics.total_revenue or 0),
            "active_products": total_metrics.active_products or 0,
            "sell_through_rate": round(
                (total_metrics.total_sold / total_metrics.total_produced * 100) 
                if total_metrics.total_produced else 0, 2
            )
        },
        "categories": categories,
        "top_products": [
            {"name": prod.name, "revenue": float(prod.revenue)}
            for prod in top_products
        ]
    }