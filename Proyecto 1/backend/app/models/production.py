from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    production_date = Column(Date, nullable=False)
    quantity_produced = Column(Integer, default=0)
    quantity_sold = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    unit_cost = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", back_populates="production_records")

class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    records_imported = Column(Integer, default=0)
    import_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")
    error_message = Column(Text)
    imported_by = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User")