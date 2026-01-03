from fastapi import APIRouter, HTTPException
from api.schemas import (
    LetterGenerationRequest, LetterGenerationResponse,
    TemplateSearchRequest, TemplateSearchResponse,
    TemplateDetailsRequest, TemplateDetailsResponse,
    TemplateFillRequest, TemplateFillResponse
)
from module_c.interface import LetterGenerationAPI

router = APIRouter()
letter_api = LetterGenerationAPI()

# ... existing endpoints ...

@router.post("/search-template", response_model=TemplateSearchResponse)
async def search_template(request: TemplateSearchRequest):
    try:
        result = letter_api.search_template(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-template-details", response_model=TemplateDetailsResponse)
async def get_template_details(request: TemplateDetailsRequest):
    try:
        result = letter_api.get_template_details(request.template_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fill-template", response_model=TemplateFillResponse)
async def fill_template(request: TemplateFillRequest):
    try:
        result = letter_api.fill_template(request.template_name, request.placeholders)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-letter", response_model=LetterGenerationResponse)
async def generate_letter(request: LetterGenerationRequest):
    try:
        # Check if we need to analyze or generate
        # For simplicity, we assume the user might want to generate directly
        # If additional_data is provided, we use it.
        
        result = letter_api.generate_smart_letter(
            description=request.description,
            template_name=request.template_name,
            additional_data=request.additional_data
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-requirements", response_model=LetterGenerationResponse)
async def analyze_requirements(request: LetterGenerationRequest):
    try:
        result = letter_api.analyze_requirements(request.description)
        # Map result to response schema
        return {
            "success": result.get("success", False),
            "template_used": result.get("template_name"),
            "detected_placeholders": result.get("detected_placeholders"),
            "missing_fields": result.get("missing_fields"),
            "error": result.get("error")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
