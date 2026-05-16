"""Application configuration — IBM watsonx.ai + Granite models ONLY"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Union


class Settings(BaseSettings):
    """Application settings for IBM Bob Hackathon"""

    # ── Application ─────────────────────────────────────────────────────────
    APP_NAME: str = "DevPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Server ──────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # ── CORS ────────────────────────────────────────────────────────────────
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [o.strip() for o in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./devpilot.db"

    # ── IBM Cloud Credentials ────────────────────────────────────────────────
    IBM_CLOUD_API_KEY: str = ""
    IBM_CLOUD_REGION: str = "us-south"

    # ── IBM watsonx.ai (Primary AI Service) ──────────────────────────────────
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    
    # Granite Model Configuration
    WATSONX_MODEL_ID: str = "ibm/granite-3-8b-instruct"
    WATSONX_EMBEDDING_MODEL: str = "ibm/slate-125m-english-rtrvr"
    
    # Model Parameters
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    TOP_P: float = 1.0
    TOP_K: int = 50
    REPETITION_PENALTY: float = 1.0

    @property
    def watsonx_available(self) -> bool:
        """True when watsonx.ai credentials are configured."""
        return bool(
            self.IBM_CLOUD_API_KEY
            and self.IBM_CLOUD_API_KEY != "YOUR_IBM_CLOUD_API_KEY_HERE"
            and self.WATSONX_PROJECT_ID
            and self.WATSONX_PROJECT_ID != "YOUR_WATSONX_PROJECT_ID_HERE"
        )

    # ── IBM Watson Speech-to-Text (Optional) ─────────────────────────────────
    WATSON_STT_API_KEY: str = ""
    WATSON_STT_URL: str = "https://api.us-south.speech-to-text.watson.cloud.ibm.com"

    @property
    def watson_stt_available(self) -> bool:
        """True when Watson STT credentials are configured."""
        return bool(
            self.WATSON_STT_API_KEY
            and self.WATSON_STT_API_KEY != "YOUR_WATSON_STT_API_KEY_HERE"
        )

    # ── Embedding Strategy ────────────────────────────────────────────────────
    # Set to true to use IBM watsonx.ai embeddings; false = Bob/OpenAI fallback
    USE_IBM_EMBEDDINGS: bool = True

    # ── Bob / OpenAI-compatible fallback ─────────────────────────────────────
    # Used only when USE_IBM_EMBEDDINGS=false or watsonx is unavailable
    OPENAI_API_KEY: str = ""
    BOB_API_BASE: str = ""  # e.g. https://api.bob.com/v1

    @property
    def effective_api_base(self) -> Optional[str]:
        """Return the base URL for the Bob/OpenAI-compat client, or None."""
        return self.BOB_API_BASE.strip() or None

    # ── Vector Store ─────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"

    # ── RAG ──────────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # ── Cache ─────────────────────────────────────────────────────────────────
    CACHE_TTL: int = 3600

    # ── GitHub (optional) ─────────────────────────────────────────────────────
    GITHUB_TOKEN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global singleton
settings = Settings()
