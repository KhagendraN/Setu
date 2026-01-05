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


# Debiasing Schemas (LLM-based suggestions)
class DebiasSentenceRequest(BaseModel):
    sentence: str
    category: str
    context: Optional[str] = None  # optional surrounding text for better rewriting


class DebiasSentenceResponse(BaseModel):
    success: bool
    original_sentence: str
    category: str
    suggestion: Optional[str] = None
    rationale: Optional[str] = None
    error: Optional[str] = None


class DebiasBatchItem(BaseModel):
    index: int
    input: DebiasSentenceRequest
    result: DebiasSentenceResponse


class DebiasBatchRequest(BaseModel):
    items: List[DebiasSentenceRequest]


class DebiasBatchResponse(BaseModel):
    success: bool
    items: List[DebiasBatchItem]
    error: Optional[str] = None

# PDF Processing Schemas
class PDFProcessingResponse(BaseModel):
    success: bool
    sentences: List[str]
    total_sentences: int
    raw_text: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None

class PDFToBiasDetectionRequest(BaseModel):
    # This is handled via Form data in the route, but good to have schema if needed for documentation or client generation
    # However, the route uses UploadFile which is not directly compatible with Pydantic models in the same way for the file part.
    # But the response model is needed.
    pass

class PDFToBiasDetectionResponse(BaseModel):
    success: bool
    total_sentences: int
    biased_count: int
    neutral_count: int
    results: List[BiasResult]
    filename: Optional[str] = None
    error: Optional[str] = None

# Human-in-the-Loop (HITL) Schemas
class BiasReviewItem(BaseModel):
    sentence_id: str
    original_sentence: str
    is_biased: bool
    category: str
    confidence: float
    suggestion: Optional[str] = None
    approved_suggestion: Optional[str] = None
    status: str = "pending"  # "pending", "approved", "needs_regeneration"

class BiasReviewSession(BaseModel):
    session_id: str
    original_filename: str
    sentences: List[BiasReviewItem]
    raw_text: str
    pdf_bytes: Optional[bytes] = None
    created_at: str
    status: str = "pending_review"  # "pending_review", "in_progress", "completed"

class StartReviewResponse(BaseModel):
    success: bool
    session_id: str
    total_sentences: int
    biased_count: int
    neutral_count: int
    sentences: List[BiasReviewItem]
    filename: str
    error: Optional[str] = None

class ApprovalRequest(BaseModel):
    session_id: str
    sentence_id: str
    action: str  # "approve", "reject"
    approved_suggestion: Optional[str] = None

class ApprovalResponse(BaseModel):
    success: bool
    sentence_id: str
    message: str
    error: Optional[str] = None

class RegenerateSuggestionRequest(BaseModel):
    session_id: str
    sentence_id: str

class RegenerateSuggestionResponse(BaseModel):
    success: bool
    sentence_id: str
    new_suggestion: Optional[str] = None
    error: Optional[str] = None

class GeneratePDFRequest(BaseModel):
    session_id: str

class GeneratePDFResponse(BaseModel):
    success: bool
    pdf_filename: Optional[str] = None
    pdf_content: Optional[bytes] = None
    changes_applied: int
    error: Optional[str] = None

class SessionStatusResponse(BaseModel):
    success: bool
    session_id: str
    status: str
    total_sentences: int
    pending_count: int
    approved_count: int
    needs_regeneration_count: int
    sentences: List[BiasReviewItem]
    error: Optional[str] = None
