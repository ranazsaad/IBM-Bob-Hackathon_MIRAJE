"""
Live Meeting endpoints
  POST /api/live-meeting/process        — full analysis of text notes
  POST /api/live-meeting/quick-insights — lightweight mid-meeting feedback
  POST /api/live-meeting/transcribe     — audio → text via IBM Watson STT
  GET  /api/live-meeting/stt-status     — check if Watson STT is configured
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.services.live_meeting_service import LiveMeetingService
from app.services.watson_stt_service import watson_stt_service

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
#  Schemas
# ──────────────────────────────────────────────────────────────────────────────

class LiveMeetingProcessRequest(BaseModel):
    raw_notes: str = Field(..., description="Transcript text (typed or from STT)")
    meeting_title: str = Field("Meeting", description="Meeting name")
    context: Optional[str] = Field("", description="Project or sprint context")

    model_config = {
        "json_schema_extra": {
            "example": {
                "raw_notes": "We need a login page, also password reset, maybe oauth with google...",
                "meeting_title": "Sprint Planning Q2",
                "context": "E-commerce platform redesign",
            }
        }
    }


class QuickInsightsRequest(BaseModel):
    partial_notes: str = Field(..., description="Partial meeting transcript so far")


# ──────────────────────────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/process")
async def process_live_meeting(
    request: LiveMeetingProcessRequest,
    db: Session = Depends(get_db),
):
    """
    Full analysis of meeting notes (text).

    Uses Bob (Claude 3.5 Sonnet via api.cline.bot) to:
    - Clean and structure the raw transcript
    - Extract requirements
    - Generate user stories
    - Create engineering tickets with priorities
    - Build an implementation plan
    - Write an executive summary
    """
    try:
        service = LiveMeetingService(db)
        result = await service.process_live_notes(
            raw_notes=request.raw_notes,
            meeting_title=request.meeting_title,
            context=request.context or "",
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-insights")
async def get_quick_insights(
    request: QuickInsightsRequest,
    db: Session = Depends(get_db),
):
    """
    Lightweight real-time analysis (call every 30-60 s while meeting runs).
    Returns key topics, action items, and AI observations without full processing.
    Powered by Bob (Claude 3.5 Sonnet).
    """
    try:
        service = LiveMeetingService(db)
        result = await service.get_quick_insights(request.partial_notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (webm, wav, mp3, ogg, flac)"),
    language: str = Form("en-US", description="BCP-47 language code, e.g. en-US, ar-MS"),
):
    """
    Convert an uploaded audio recording to text using IBM Watson Speech-to-Text.

    Supported formats: audio/webm, audio/wav, audio/mp3, audio/ogg, audio/flac

    The frontend records in webm format using MediaRecorder and POSTs the blob here.
    Watson STT returns:
    - transcript: cleaned, smart-formatted text
    - confidence: overall confidence score
    - words: word-level confidence (for highlighting low-confidence words)
    - provider: 'watson_stt' | 'unavailable'
    """
    if not watson_stt_service.is_available:
        raise HTTPException(
            status_code=503,
            detail=(
                "IBM Watson STT is not configured. "
                "Add WATSON_STT_API_KEY and WATSON_STT_URL to backend/.env. "
                "Get credentials from IBM Cloud → Resource List → Watson Speech to Text."
            ),
        )

    # Validate file type
    content_type = audio.content_type or "audio/webm"
    allowed_types = {
        "audio/webm", "audio/wav", "audio/mpeg", "audio/mp3",
        "audio/ogg", "audio/flac", "audio/mp4", "video/webm",
    }
    if content_type not in allowed_types:
        content_type = "audio/webm"  # default for browser recordings

    audio_bytes = await audio.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file is too short or empty.")

    result = await watson_stt_service.transcribe_audio(
        audio_bytes=audio_bytes,
        content_type=content_type,
        language_code=language,
    )

    if result.get("error") and not result.get("transcript"):
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/stt-status")
async def get_stt_status():
    """
    Check whether IBM Watson STT is available.
    The frontend uses this to show/hide the 'Upload Audio' option.
    """
    from app.config import settings
    return {
        "watson_stt_available": watson_stt_service.is_available,
        "watsonx_embeddings_available": settings.watsonx_available,
        "bob_api_configured": bool(settings.OPENAI_API_KEY),
        "bob_endpoint": settings.OPENAI_API_BASE,
        "active_llm_model": settings.OPENAI_MODEL,
        "active_embedding_model": settings.OPENAI_EMBEDDING_MODEL,
    }
