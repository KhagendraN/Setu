from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Module A Schemas
class ExplanationRequest(BaseModel):
    query: str

class ExplanationResponse(BaseModel):
    summary: str
    key_point: str
    explanation: str
    next_steps: str
    sources: List[Dict[str, Any]]
    query: str

# Module C Schemas
class LetterGenerationRequest(BaseModel):
    description: str
    template_name: Optional[str] = None
    additional_data: Optional[Dict[str, str]] = None

class LetterGenerationResponse(BaseModel):
    success: bool
    letter: Optional[str] = None
    template_used: Optional[str] = None
    detected_placeholders: Optional[List[str]] = None
    missing_fields: Optional[List[str]] = None
    error: Optional[str] = None
    method: Optional[str] = None

# Granular API Schemas
class TemplateSearchRequest(BaseModel):
    query: str

class TemplateSearchResponse(BaseModel):
    success: bool
    template_name: Optional[str] = None
    score: Optional[float] = None
    content: Optional[str] = None
    error: Optional[str] = None

class TemplateDetailsRequest(BaseModel):
    template_name: str

class TemplateDetailsResponse(BaseModel):
    success: bool
    template_name: Optional[str] = None
    placeholders: Optional[List[str]] = None
    content: Optional[str] = None
    error: Optional[str] = None

class TemplateFillRequest(BaseModel):
    template_name: str
    placeholders: Dict[str, str]

class TemplateFillResponse(BaseModel):
    success: bool
    letter: Optional[str] = None
    error: Optional[str] = None

# Module B Schemas
class BiasDetectionRequest(BaseModel):
    text: str
    confidence_threshold: Optional[float] = 0.7

class BiasResult(BaseModel):
    sentence: str
    category: str
    confidence: float
    is_biased: bool

class BiasDetectionResponse(BaseModel):
    success: bool
    total_sentences: int
    biased_count: int
    neutral_count: int
    results: List[BiasResult]
    error: Optional[str] = None


# Batch variant for Module B
class BatchBiasDetectionRequest(BaseModel):
    texts: List[str]
    confidence_threshold: Optional[float] = 0.7


class BatchBiasItem(BaseModel):
    index: int
    input_text: str
    result: BiasDetectionResponse


class BatchBiasDetectionResponse(BaseModel):
    success: bool
    items: List[BatchBiasItem]
    error: Optional[str] = None
