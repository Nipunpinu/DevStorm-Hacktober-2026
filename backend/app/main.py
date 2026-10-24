import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="YojanaSetu National Civic Welfare & Eligibility Discovery Engine",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"], # Allow configured origins + wildcard for local static file loading
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health & Privacy Notice Endpoint
@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected",
        "ai_configured": bool(settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your_openai")),
        "privacy": "DPDP compliant. No Aadhaar or biometric data is collected or retained."
    }

# Check if frontend directory exists or serve project/ai_studio_code.html
project_html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../project/ai_studio_code.html"))
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

if os.path.exists(project_html_path):
    @app.get("/")
    def serve_frontend_root():
        return FileResponse(project_html_path)

if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")
