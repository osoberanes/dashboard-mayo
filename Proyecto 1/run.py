#!/usr/bin/env python3
import uvicorn
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import engine, Base
from app.models import user, product, production

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir="backend"
    )