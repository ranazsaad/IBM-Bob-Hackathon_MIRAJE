"""
IBM Watson Speech-to-Text Service

Handles audio transcription using IBM Watson STT API.
Falls back to returning raw text if credentials are not set.

Supported audio formats: wav, mp3, webm, ogg, flac, mp4
"""

import asyncio
import io
from typing import Optional

from app.config import settings


class WatsonSTTService:
    """Transcribes audio using IBM Watson Speech to Text."""

    def __init__(self):
        self._client = None
        self._available = settings.watson_stt_available
        if self._available:
            self._init_client()

    def _init_client(self):
        """Initialize IBM Watson STT client."""
        try:
            from ibm_watson import SpeechToTextV1
            from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

            authenticator = IAMAuthenticator(settings.WATSON_STT_API_KEY)
            stt = SpeechToTextV1(authenticator=authenticator)
            stt.set_service_url(settings.WATSON_STT_URL)
            stt.set_default_headers({"x-watson-learning-opt-out": "true"})
            self._client = stt
            print("[WatsonSTT] IBM Watson Speech-to-Text initialized [OK]")
        except Exception as e:
            print(f"[WatsonSTT] Init failed: {e} — STT will be unavailable")
            self._available = False

    # ── Public API ───────────────────────────────────────────────────────────

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        content_type: str = "audio/webm",
        language_code: str = "en-US",
    ) -> dict:
        """
        Transcribe audio bytes to text using Watson STT.

        Args:
            audio_bytes:   Raw audio content (webm/wav/mp3/ogg/flac)
            content_type:  MIME type of the audio
            language_code: BCP-47 language code

        Returns:
            {"transcript": str, "confidence": float, "words": list, "provider": str}
        """
        if not self._available or not self._client:
            return {
                "transcript": "",
                "confidence": 0.0,
                "words": [],
                "provider": "unavailable",
                "error": "Watson STT credentials not configured. Set WATSON_STT_API_KEY in .env",
            }

        # Map content_type to Watson model
        model = self._get_model(language_code, content_type)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._transcribe_sync,
            audio_bytes,
            content_type,
            model,
        )
        return result

    # ── Internal ────────────────────────────────────────────────────────────

    def _transcribe_sync(
        self,
        audio_bytes: bytes,
        content_type: str,
        model: str,
    ) -> dict:
        """Blocking Watson STT call (run in executor)."""
        try:
            audio_file = io.BytesIO(audio_bytes)
            response = self._client.recognize(
                audio=audio_file,
                content_type=content_type,
                model=model,
                word_confidence=True,
                timestamps=True,
                smart_formatting=True,       # Formats numbers, dates, etc.
                profanity_filter=False,
                speaker_labels=True,          # Who said what (multi-speaker)
            ).get_result()

            results = response.get("results", [])
            if not results:
                return {"transcript": "", "confidence": 0.0, "words": [], "provider": "watson"}

            # Combine all alternatives
            full_transcript = ""
            total_confidence = 0.0
            word_list = []
            count = 0

            for r in results:
                alternatives = r.get("alternatives", [])
                if alternatives:
                    best = alternatives[0]
                    full_transcript += best.get("transcript", "") + " "
                    total_confidence += best.get("confidence", 0.0)
                    count += 1
                    word_list.extend(best.get("word_confidence", []))

            avg_confidence = total_confidence / count if count > 0 else 0.0

            return {
                "transcript": full_transcript.strip(),
                "confidence": round(avg_confidence, 3),
                "words": word_list[:50],   # Limit for response size
                "provider": "watson_stt",
                "model": model,
            }

        except Exception as e:
            print(f"[WatsonSTT] Transcription error: {e}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "words": [],
                "provider": "watson_stt",
                "error": str(e),
            }

    def _get_model(self, language_code: str, content_type: str) -> str:
        """Select best Watson STT model for the given language + content type."""
        lang_prefix = language_code.replace("-", "_").lower()

        model_map = {
            "en_us": "en-US_BroadbandModel",
            "en_gb": "en-GB_BroadbandModel",
            "ar_ms": "ar-MS_BroadbandModel",
            "fr_fr": "fr-FR_BroadbandModel",
            "de_de": "de-DE_BroadbandModel",
            "es_es": "es-ES_BroadbandModel",
            "ja_jp": "ja-JP_BroadbandModel",
            "zh_cn": "zh-CN_BroadbandModel",
        }
        return model_map.get(lang_prefix, "en-US_BroadbandModel")

    @property
    def is_available(self) -> bool:
        return self._available


# Global singleton
watson_stt_service = WatsonSTTService()
