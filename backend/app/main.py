import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .config import get_settings
from .models import PromptRequest, PromptResponse, SpeechRequest
from .openai_service import PromptGenerator
from .speech_service import SpeechService

settings = get_settings()
prompt_generator = PromptGenerator(settings)
speech_service = SpeechService(settings)
logger = logging.getLogger(__name__)

app = FastAPI(title="You Know Game API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "openaiConfigured": prompt_generator.is_configured,
        "speechConfigured": speech_service.is_configured,
        "model": settings.openai_model,
    }


@app.post("/api/prompts", response_model=PromptResponse)
def create_prompt(request: PromptRequest) -> PromptResponse:
    try:
        return prompt_generator.generate_prompt(request.recent_prompts)
    except RuntimeError as exc:
        detail = str(exc)
        status_code = 503 if "not configured" in detail.lower() else 502
        if status_code == 503:
            logger.warning("Prompt generation unavailable: %s", detail)
        else:
            logger.exception("Prompt generation failed")
        raise HTTPException(status_code=status_code, detail=detail) from exc


@app.post("/api/speech")
def create_speech(request: SpeechRequest) -> Response:
    try:
        audio_bytes = speech_service.synthesize_prompt_audio(request.text, request.voice)
    except RuntimeError as exc:
        detail = str(exc)
        status_code = 503 if "configured" in detail or "authentication failed" in detail.lower() else 502
        if status_code == 503:
            logger.warning("Speech synthesis unavailable: %s", detail)
        else:
            logger.exception("Speech synthesis failed")
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Cache-Control": "no-store"},
    )
