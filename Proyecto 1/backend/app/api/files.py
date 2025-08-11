from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.user import User
from app.models.production import ImportBatch
from app.services.file_processor import FileProcessor

router = APIRouter()

class ImportBatchResponse(BaseModel):
    id: int
    filename: str
    records_imported: int
    import_date: str
    status: str
    error_message: str = None

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    file_path = os.path.join(settings.upload_dir, f"{current_user.id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        processor = FileProcessor(db)
        result = processor.process_excel_file(file_path, current_user.id)
        
        if result["success"]:
            return {
                "message": result["message"],
                "batch_id": result["batch_id"],
                "records_imported": result["records_imported"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/batches", response_model=List[ImportBatchResponse])
async def get_import_batches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    batches = db.query(ImportBatch).filter(
        ImportBatch.imported_by == current_user.id
    ).order_by(ImportBatch.import_date.desc()).all()
    
    return [
        ImportBatchResponse(
            id=batch.id,
            filename=batch.filename,
            records_imported=batch.records_imported,
            import_date=batch.import_date.isoformat(),
            status=batch.status,
            error_message=batch.error_message
        )
        for batch in batches
    ]