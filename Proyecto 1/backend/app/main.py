from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.api import auth, products, analytics, files, reports

app = FastAPI(
    title="Sistema de Análisis de Producción",
    description="Sistema para analizar patrones de producción y recaudación de oficina gubernamental",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Get absolute paths for frontend - adjusted for uvicorn app_dir
# When uvicorn runs with app_dir="backend", the working directory is backend/
# So we need to go up one level to find the frontend directory
if os.path.exists("../frontend"):
    # Running from backend directory (via uvicorn app_dir)
    frontend_static_dir = os.path.abspath("../frontend/static")
    frontend_html_path = os.path.abspath("../frontend/index.html")
else:
    # Running from root directory 
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    frontend_static_dir = os.path.join(current_dir, "frontend", "static")
    frontend_html_path = os.path.join(current_dir, "frontend", "index.html")

# Mount static files only if directory exists
if os.path.exists(frontend_static_dir):
    app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/api")
def read_root():
    return {"message": "Sistema de Análisis de Producción API"}

@app.get("/")
async def serve_frontend():
    if os.path.exists(frontend_html_path):
        return FileResponse(frontend_html_path)
    else:
        return {"message": "Frontend no encontrado. API disponible en /api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)