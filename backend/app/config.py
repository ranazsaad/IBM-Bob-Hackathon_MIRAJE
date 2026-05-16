"""Application configuration — Bob/Cline + IBM watsonx integration"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Union


class Settings(BaseSettings):
    """Application settings"""

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

    # ── Bob / Cline API (OpenAI-compatible, primary LLM) ────────────────────
    # Endpoint: https://api.cline.bot/v1
    # Key format: bob_prod_bob-user_...
    OPENAI_API_KEY: str = ""       # Bob/Cline API key
    OPENAI_API_BASE: str = "https://api.cline.bot/v1"
    OPENAI_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_EMBEDDING_MODEL: str = "ibm/slate-125m-english-rtrvr"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    @property
    def effective_api_base(self) -> Optional[str]:
        """Return the Bob API base URL (None only when left completely blank)."""
        v = self.OPENAI_API_BASE.strip()
        return v if v else None

    # ── IBM Cloud (Watson STT + watsonx.ai embeddings) ───────────────────────
    IBM_CLOUD_API_KEY: str = ""
    IBM_CLOUD_REGION: str = "us-south"

    # Watson Speech-to-Text
    WATSON_STT_API_KEY: str = ""
    WATSON_STT_URL: str = "https://api.us-south.speech-to-text.watson.cloud.ibm.com"

    # watsonx.ai (foundation models / embeddings)
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"

    # Feature flag: use IBM watsonx for embeddings (requires IBM keys)
    USE_IBM_EMBEDDINGS: bool = True

    @property
    def watson_stt_available(self) -> bool:
        """True when Watson STT credentials are configured."""
        return bool(self.WATSON_STT_API_KEY and self.WATSON_STT_API_KEY != "YOUR_WATSON_STT_API_KEY_HERE")

    @property
    def watsonx_available(self) -> bool:
        """True when watsonx.ai credentials are configured."""
        return bool(
            self.WATSONX_PROJECT_ID
            and self.WATSONX_PROJECT_ID != "YOUR_WATSONX_PROJECT_ID_HERE"
            and (self.IBM_CLOUD_API_KEY or self.OPENAI_API_KEY)
        )

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
