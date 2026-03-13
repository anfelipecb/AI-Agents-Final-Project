"""EmbeddingLoader: sentence-transformers, get_embeddings, cosine_sim."""
import numpy as np

from ..config import EMBEDDING_MODEL


class EmbeddingLoader:
    """Loads sentence-transformers model; provides get_embeddings, cosine_sim."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def get_embeddings(self, texts: list[str], show_progress_bar: bool = False) -> np.ndarray:
        """Get embeddings for a list of texts."""
        return self.model.encode(texts, show_progress_bar=show_progress_bar, convert_to_numpy=True)

    @staticmethod
    def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))
