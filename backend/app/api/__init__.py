from fastapi import APIRouter
from backend.app.api.eligibility import router as eligibility_router
from backend.app.api.schemes import router as schemes_router
from backend.app.api.assistant import router as assistant_router
from backend.app.api.languages import router as languages_router
from backend.app.api.sources import router as sources_router
from backend.app.api.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(eligibility_router)
api_router.include_router(schemes_router)
api_router.include_router(assistant_router)
api_router.include_router(languages_router)
api_router.include_router(sources_router)
api_router.include_router(admin_router)
