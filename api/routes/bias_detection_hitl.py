"""
Human-in-the-Loop Bias Detection API
Handles the interactive workflow for bias detection with human approval
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import Response
from api.core.deps import get_current_user
from api.schemas import (
    StartReviewResponse,
    ApprovalRequest,
    ApprovalResponse,
    RegenerateSuggestionRequest,
    RegenerateSuggestionResponse,
    GeneratePDFRequest,
    GeneratePDFResponse,
    SessionStatusResponse,
    BiasReviewItem,
    DebiasSentenceRequest,
)
from api.routes.bias_detection import run_bias_detection, generate_debiased_sentence
from utility.pdf_processor import PDFProcessor
from utility.hitl_session_manager import HITLSessionManager
from utility.pdf_regenerator import PDFRegenerator
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize global session manager
session_manager = HITLSessionManager()

# Initialize PDF processor and regenerator
pdf_processor = PDFProcessor()
pdf_regenerator = PDFRegenerator()


@router.post("/start-review", response_model=StartReviewResponse)
async def start_bias_review(
    file: UploadFile = File(...),
    refine_with_llm: bool = Form(True),
    confidence_threshold: float = Form(0.7),
    user: dict = Depends(get_current_user)
):
    """
    Start a human-in-the-loop bias detection review session.

    Workflow:
    1. Upload PDF
    2. Extract and segment sentences
    3. Run bias detection
    4. Generate suggestions for biased sentences
    5. Return session ID with all results for review
    """
    try:
        logger.info(f"Starting HITL review for file: {file.filename}")

        # Read PDF bytes
        pdf_content = await file.read()

        # Process PDF to extract sentences
        result = pdf_processor.process_pdf_from_bytes(
            pdf_bytes=pdf_content,
            refine_with_llm=refine_with_llm
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"PDF processing failed: {result.get('error', 'Unknown error')}"
            )

        sentences = result["sentences"]
        raw_text = result["raw_text"]

        if not sentences:
            raise HTTPException(
                status_code=400,
                detail="No sentences could be extracted from the PDF"
            )

        # Run bias detection on each sentence individually
        logger.info(f"Running bias detection on {len(sentences)} sentences")
        all_bias_results = []

        for sentence in sentences:
            bias_detection_result = run_bias_detection(sentence, confidence_threshold)
            if bias_detection_result.success and bias_detection_result.results:
                # Each sentence gets analyzed separately
                all_bias_results.extend(bias_detection_result.results)
            else:
                logger.warning(f"Bias detection failed for sentence: {sentence[:50]}...")

        if not all_bias_results:
            raise HTTPException(
                status_code=500,
                detail="Bias detection failed for all sentences"
            )

        logger.info(f"Bias detection completed. Found {len(all_bias_results)} results")

        # Create review items with suggestions for biased sentences
        review_items = []
        biased_count = 0
        neutral_count = 0

        for bias_result in all_bias_results:
            sentence_id = str(uuid.uuid4())

            # Generate suggestion for biased sentences
            suggestion = None
            if bias_result.is_biased:
                biased_count += 1
                # Generate debiased suggestion
                debias_request = DebiasSentenceRequest(
                    sentence=bias_result.sentence,
                    category=bias_result.category,
                    context=None
                )
                debias_response = generate_debiased_sentence(debias_request)
                if debias_response.success:
                    suggestion = debias_response.suggestion
            else:
                neutral_count += 1

            review_item = BiasReviewItem(
                sentence_id=sentence_id,
                original_sentence=bias_result.sentence,
                is_biased=bias_result.is_biased,
                category=bias_result.category,
                confidence=bias_result.confidence,
                suggestion=suggestion,
                approved_suggestion=None,
                status="pending" if bias_result.is_biased else "approved"  # Auto-approve neutral
            )

            review_items.append(review_item)

        # Create session
        session = session_manager.create_session(
            filename=file.filename,
            sentences=review_items,
            raw_text=raw_text,
            pdf_bytes=pdf_content
        )

        logger.info(f"Created HITL session {session.session_id} with {len(review_items)} sentences")

        return StartReviewResponse(
            success=True,
            session_id=session.session_id,
            total_sentences=len(review_items),
            biased_count=biased_count,
            neutral_count=neutral_count,
            sentences=review_items,
            filename=file.filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting HITL review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve-suggestion", response_model=ApprovalResponse)
async def approve_suggestion(
    request: ApprovalRequest,
    user: dict = Depends(get_current_user)
):
    """
    Approve or reject a suggestion for a biased sentence.

    Actions:
    - "approve": Accept the suggested sentence
    - "reject": Mark for regeneration
    """
    try:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if request.action == "approve":
            # Approve the suggestion
            success = session_manager.update_sentence_status(
                session_id=request.session_id,
                sentence_id=request.sentence_id,
                status="approved",
                approved_suggestion=request.approved_suggestion
            )

            if not success:
                raise HTTPException(status_code=404, detail="Sentence not found in session")

            return ApprovalResponse(
                success=True,
                sentence_id=request.sentence_id,
                message="Suggestion approved successfully"
            )

        elif request.action == "reject":
            # Mark for regeneration
            success = session_manager.update_sentence_status(
                session_id=request.session_id,
                sentence_id=request.sentence_id,
                status="needs_regeneration",
                approved_suggestion=None
            )

            if not success:
                raise HTTPException(status_code=404, detail="Sentence not found in session")

            return ApprovalResponse(
                success=True,
                sentence_id=request.sentence_id,
                message="Suggestion rejected. Please regenerate a new suggestion."
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate-suggestion", response_model=RegenerateSuggestionResponse)
async def regenerate_suggestion(
    request: RegenerateSuggestionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Regenerate a new suggestion for a rejected sentence using LLM.
    """
    try:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Find the sentence
        target_sentence = None
        for sentence in session.sentences:
            if sentence.sentence_id == request.sentence_id:
                target_sentence = sentence
                break

        if not target_sentence:
            raise HTTPException(status_code=404, detail="Sentence not found in session")

        # Generate new suggestion using LLM
        debias_request = DebiasSentenceRequest(
            sentence=target_sentence.original_sentence,
            category=target_sentence.category,
            context=None
        )

        debias_response = generate_debiased_sentence(debias_request)

        if not debias_response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate new suggestion: {debias_response.error}"
            )

        # Update the session with new suggestion
        success = session_manager.update_sentence_suggestion(
            session_id=request.session_id,
            sentence_id=request.sentence_id,
            new_suggestion=debias_response.suggestion
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update session")

        logger.info(f"Regenerated suggestion for sentence {request.sentence_id}")

        return RegenerateSuggestionResponse(
            success=True,
            sentence_id=request.sentence_id,
            new_suggestion=debias_response.suggestion
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pdf")
async def generate_debiased_pdf(
    request: GeneratePDFRequest,
    user: dict = Depends(get_current_user)
):
    """
    Generate final PDF with all approved suggestions applied.

    Requirements:
    - All biased sentences must be approved
    - Returns the modified PDF as downloadable file
    """
    try:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if session is ready for PDF generation
        if not session_manager.is_session_ready_for_pdf(request.session_id):
            stats = session_manager.get_session_stats(request.session_id)
            raise HTTPException(
                status_code=400,
                detail=f"Not all sentences have been reviewed. Pending: {stats['pending_count']}, "
                       f"Needs regeneration: {stats['needs_regeneration_count']}"
            )

        # Count changes to be applied
        changes_count = sum(
            1 for s in session.sentences
            if s.is_biased and s.approved_suggestion and s.status == "approved"
        )

        # Regenerate PDF with approved changes
        success, pdf_bytes, error = pdf_regenerator.regenerate_pdf(
            original_pdf_bytes=session.pdf_bytes,
            sentences=session.sentences,
            output_filename=f"debiased_{session.original_filename}"
        )

        if not success:
            # Fallback: create simple PDF
            logger.warning(f"PDF regeneration failed, trying fallback method: {error}")
            success, pdf_bytes, error = pdf_regenerator.create_simple_pdf_from_sentences(
                sentences=session.sentences,
                filename=f"debiased_{session.original_filename}"
            )

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PDF: {error}"
            )

        # Mark session as completed
        session_manager.mark_session_completed(request.session_id)

        logger.info(f"Generated debiased PDF for session {request.session_id} with {changes_count} changes")

        # Return PDF as downloadable response
        filename = f"debiased_{session.original_filename}"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Changes-Applied": str(changes_count)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get the current status of a review session.

    Returns:
    - Session details
    - Review progress statistics
    - All sentences with their current status
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        stats = session_manager.get_session_stats(session_id)

        return SessionStatusResponse(
            success=True,
            session_id=session.session_id,
            status=session.status,
            total_sentences=stats["total_sentences"],
            pending_count=stats["pending_count"],
            approved_count=stats["approved_count"],
            needs_regeneration_count=stats["needs_regeneration_count"],
            sentences=session.sentences
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def hitl_health_check():
    """
    Check if the HITL service is running properly.
    """
    active_sessions = len(session_manager.get_all_sessions())

    return {
        "status": "healthy",
        "service": "bias-detection-hitl",
        "active_sessions": active_sessions,
        "features": {
            "session_management": True,
            "pdf_regeneration": True,
            "llm_suggestions": True
        }
    }
