"""
Embedding Service — IBM watsonx.ai (primary) with Bob/OpenAI fallback.

Priority:
  1. IBM watsonx.ai  ibm/slate-125m-english-rtrvr  (USE_IBM_EMBEDDINGS=true + creds set)
  2. Bob/Cline API   text-embedding-3-small          (fallback via OpenAI-compat layer)
"""

from typing import List, Optional
from openai import AsyncOpenAI

from app.config import settings


class EmbeddingService:
    """Generates vector embeddings for RAG."""

    def __init__(self):
        self._watsonx_client = None
        self._bob_client: Optional[AsyncOpenAI] = None
        self._use_ibm = settings.USE_IBM_EMBEDDINGS and settings.watsonx_available

        if self._use_ibm:
            self._init_watsonx()
        else:
            self._init_bob()

    # ── Initializers ────────────────────────────────────────────────────────

    def _init_watsonx(self):
        """Set up ibm-watsonx-ai client for embeddings."""
        try:
            from ibm_watsonx_ai import APIClient, Credentials
            creds = Credentials(
                url=settings.WATSONX_URL,
                api_key=settings.IBM_CLOUD_API_KEY or settings.OPENAI_API_KEY,
            )
            self._watsonx_client = APIClient(creds)
            print("[EmbeddingService] Using IBM watsonx.ai for embeddings")
        except Exception as e:
            print(f"[EmbeddingService] watsonx init failed ({e}), falling back to Bob")
            self._use_ibm = False
            self._init_bob()

    def _init_bob(self):
        """Set up Bob/Cline OpenAI-compatible client for embeddings."""
        kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.effective_api_base:
            kwargs["base_url"] = settings.effective_api_base
        self._bob_client = AsyncOpenAI(**kwargs)
        print("[EmbeddingService] Using Bob/Cline for embeddings")

    # ── Public API ──────────────────────────────────────────────────────────

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a single embedding vector."""
        if self._use_ibm:
            return await self._embed_watsonx([text[:8000]])[0]
        return await self._embed_bob(text[:8191])

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of texts."""
        if self._use_ibm:
            return await self._embed_watsonx_batch(texts)
        return await self._embed_bob_batch(texts)

    # ── IBM watsonx.ai ───────────────────────────────────────────────────────

    async def _embed_watsonx(self, texts: List[str]) -> List[List[float]]:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._embed_watsonx_sync, texts)

    def _embed_watsonx_sync(self, texts: List[str]) -> List[List[float]]:
        from ibm_watsonx_ai.foundation_models import Embeddings
        from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams

        embed_params = {EmbedParams.TRUNCATE_INPUT_TOKENS: 512}
        embedder = Embeddings(
            model_id="ibm/slate-125m-english-rtrvr",
            params=embed_params,
            credentials={
                "url": settings.WATSONX_URL,
                "apikey": settings.IBM_CLOUD_API_KEY or settings.OPENAI_API_KEY,
            },
            project_id=settings.WATSONX_PROJECT_ID,
        )
        response = embedder.embed_documents(texts=texts)
        return [item["embedding"] for item in response]

    async def _embed_watsonx_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embed, chunking into groups of 25 (API limit)."""
        results: List[List[float]] = []
        batch_size = 25
        for i in range(0, len(texts), batch_size):
            batch = [t[:8000] for t in texts[i: i + batch_size]]
            results.extend(await self._embed_watsonx(batch))
        return results

    # ── Bob / Cline fallback ─────────────────────────────────────────────────

    async def _embed_bob(self, text: str) -> List[float]:
        response = await self._bob_client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    async def _embed_bob_batch(self, texts: List[str]) -> List[List[float]]:
        trimmed = [t[:8191] for t in texts]
        response = await self._bob_client.embeddings.create(
            model="text-embedding-3-small",
            input=trimmed,
        )
        return [item.embedding for item in response.data]


# Global singleton
embedding_service = EmbeddingService()
