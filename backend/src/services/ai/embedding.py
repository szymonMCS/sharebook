import logging
from typing import List
from openai import AsyncOpenAI
from src.config import settings
from src.services.ai.interfaces import IEmbeddingService

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(IEmbeddingService):
    def __init__(self, client: AsyncOpenAI = None, model: str = None):
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model or settings.OPENAI_EMBEDDING_MODEL

    def get_dimension(self) -> int:
        return 1536

    def _truncate(self, text: str, max_length: int = 8000) -> str:
        if len(text) <= max_length:
            return text
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        return truncated[:last_space] if last_space > 0 else truncated

    async def generate_embedding(self, text: str) -> List[float]:
        try:
            truncated = self._truncate(text)
            response = await self._client.embeddings.create(model=self._model, input=truncated)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        truncated = [self._truncate(t) for t in texts]
        response = await self._client.embeddings.create(model=self._model, input=truncated)
        return [item.embedding for item in response.data]
