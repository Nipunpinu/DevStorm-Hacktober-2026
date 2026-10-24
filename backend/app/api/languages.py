from fastapi import APIRouter
from backend.app.services.translation_service import SUPPORTED_LANGUAGES, get_ui_translations

router = APIRouter(prefix="/languages", tags=["Languages"])

@router.get("")
def list_languages():
    """Returns list of supported 14 Indian languages with native scripts and RTL markers."""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "total": len(SUPPORTED_LANGUAGES)
    }

@router.get("/{code}/translations")
def get_translations_for_language(code: str):
    """Returns the translation dictionary and directionality metadata for the requested language."""
    return get_ui_translations(code)
