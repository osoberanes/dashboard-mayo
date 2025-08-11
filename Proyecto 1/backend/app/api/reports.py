from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import io

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.report_generator import ReportGenerator

router = APIRouter()

@router.get("/performance")
async def download_performance_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    format: str = Query("excel", regex="^(excel|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generator = ReportGenerator(db)
    
    try:
        report_data = generator.generate_performance_report(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            format=format
        )
        
        if format.lower() == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"performance_report_{date.today().isoformat()}.xlsx"
        else:
            media_type = "text/csv"
            filename = f"performance_report_{date.today().isoformat()}.csv"
        
        return StreamingResponse(
            io.BytesIO(report_data),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/trends")
async def download_trends_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    product_id: Optional[int] = Query(None),
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    format: str = Query("excel", regex="^(excel|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generator = ReportGenerator(db)
    
    try:
        report_data = generator.generate_trends_report(
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            period=period,
            format=format
        )
        
        if format.lower() == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"trends_report_{period}_{date.today().isoformat()}.xlsx"
        else:
            media_type = "text/csv"
            filename = f"trends_report_{period}_{date.today().isoformat()}.csv"
        
        return StreamingResponse(
            io.BytesIO(report_data),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/categories")
async def download_category_summary_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("excel", regex="^(excel|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generator = ReportGenerator(db)
    
    try:
        report_data = generator.generate_category_summary_report(
            start_date=start_date,
            end_date=end_date,
            format=format
        )
        
        if format.lower() == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"category_summary_{date.today().isoformat()}.xlsx"
        else:
            media_type = "text/csv"
            filename = f"category_summary_{date.today().isoformat()}.csv"
        
        return StreamingResponse(
            io.BytesIO(report_data),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/complete")
async def download_complete_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generator = ReportGenerator(db)
    
    try:
        report_data = generator.generate_complete_report(
            start_date=start_date,
            end_date=end_date
        )
        
        filename = f"complete_report_{date.today().isoformat()}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(report_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")