"""
Human-in-the-Loop Session Manager
Manages review sessions for bias detection with user approval workflow
"""

import uuid
from datetime import datetime
from typing import Dict, Optional
from api.schemas import BiasReviewSession, BiasReviewItem

class HITLSessionManager:
    """
    Manages in-memory sessions for human-in-the-loop bias detection workflow.
    Stores session state between PDF upload, review, and final PDF generation.
    """

    def __init__(self):
        """Initialize session manager with empty sessions dictionary."""
        self._sessions: Dict[str, BiasReviewSession] = {}

    def create_session(
        self,
        filename: str,
        sentences: list,
        raw_text: str,
        pdf_bytes: bytes
    ) -> BiasReviewSession:
        """
        Create a new review session.

        Args:
            filename: Original PDF filename
            sentences: List of BiasReviewItem objects
            raw_text: Raw extracted text from PDF
            pdf_bytes: Original PDF content as bytes

        Returns:
            BiasReviewSession object with generated session_id
        """
        session_id = str(uuid.uuid4())

        session = BiasReviewSession(
            session_id=session_id,
            original_filename=filename,
            sentences=sentences,
            raw_text=raw_text,
            pdf_bytes=pdf_bytes,
            created_at=datetime.utcnow().isoformat(),
            status="pending_review"
        )

        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[BiasReviewSession]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            BiasReviewSession if found, None otherwise
        """
        return self._sessions.get(session_id)

    def update_sentence_status(
        self,
        session_id: str,
        sentence_id: str,
        status: str,
        approved_suggestion: Optional[str] = None
    ) -> bool:
        """
        Update the status of a specific sentence in a session.

        Args:
            session_id: Session identifier
            sentence_id: Sentence identifier
            status: New status ("pending", "approved", "needs_regeneration")
            approved_suggestion: Approved suggestion text (if status is "approved")

        Returns:
            True if update successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        for sentence in session.sentences:
            if sentence.sentence_id == sentence_id:
                sentence.status = status
                if approved_suggestion:
                    sentence.approved_suggestion = approved_suggestion

                # Update session status to in_progress once first action taken
                if session.status == "pending_review":
                    session.status = "in_progress"

                return True

        return False

    def update_sentence_suggestion(
        self,
        session_id: str,
        sentence_id: str,
        new_suggestion: str
    ) -> bool:
        """
        Update the suggestion for a specific sentence.

        Args:
            session_id: Session identifier
            sentence_id: Sentence identifier
            new_suggestion: New suggestion text from LLM

        Returns:
            True if update successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        for sentence in session.sentences:
            if sentence.sentence_id == sentence_id:
                sentence.suggestion = new_suggestion
                sentence.status = "pending"  # Reset to pending after regeneration
                return True

        return False

    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """
        Get statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with counts or None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        total = len(session.sentences)
        pending = sum(1 for s in session.sentences if s.status == "pending")
        approved = sum(1 for s in session.sentences if s.status == "approved")
        needs_regen = sum(1 for s in session.sentences if s.status == "needs_regeneration")

        return {
            "total_sentences": total,
            "pending_count": pending,
            "approved_count": approved,
            "needs_regeneration_count": needs_regen
        }

    def is_session_ready_for_pdf(self, session_id: str) -> bool:
        """
        Check if all sentences in a session have been reviewed.

        Args:
            session_id: Session identifier

        Returns:
            True if all sentences are approved, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Check if all sentences are either approved or were neutral
        for sentence in session.sentences:
            if sentence.is_biased and sentence.status != "approved":
                return False

        return True

    def mark_session_completed(self, session_id: str) -> bool:
        """
        Mark a session as completed.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = "completed"
        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from memory.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_all_sessions(self) -> Dict[str, BiasReviewSession]:
        """
        Get all active sessions (for debugging/monitoring).

        Returns:
            Dictionary of all sessions
        """
        return self._sessions
