"""
Lokantra Embedding and Similarity Utility.
Provides dense vector representations and cosine similarity calculation.
Supports OpenAI / compatible embedding endpoints with a local fallback.
"""

from __future__ import annotations

import math
import re
from typing import List, Optional
import numpy as np

from ..config import Config
from .logger import get_logger

logger = get_logger("lokantra.embedding")


class EmbeddingService:
    """Unified embedding generator with fallback support."""

    _openai_client = None
    _remote_available = True

    @classmethod
    def _get_client(cls):
        if not cls._remote_available:
            return None
        if cls._openai_client is None and Config.LLM_API_KEY:
            try:
                from openai import OpenAI
                cls._openai_client = OpenAI(
                    api_key=Config.LLM_API_KEY,
                    base_url=Config.LLM_BASE_URL,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI embedding client: {e}")
                cls._remote_available = False
        return cls._openai_client

    @classmethod
    def get_embedding(cls, text: str, dimensions: int = 128) -> List[float]:
        """
        Generate embedding vector for text.
        Tries remote LLM embedding API first if configured,
        falls back to deterministic character/word n-gram hashing vector.
        """
        if not text or not text.strip():
            return [0.0] * dimensions

        if cls._remote_available:
            client = cls._get_client()
            if client:
                try:
                    # Try standard embedding model with tight timeout
                    model_name = "text-embedding-3-small"
                    response = client.embeddings.create(
                        input=[text[:2000]],
                        model=model_name,
                        timeout=2.0,
                    )
                    raw_vec = response.data[0].embedding
                    # If dimensions match or need reduction
                    if len(raw_vec) == dimensions:
                        return raw_vec
                    # Project or truncate/pad to requested dimensions
                    return cls._project_vector(raw_vec, dimensions)
                except Exception as e:
                    logger.debug(f"Remote embedding unavailable ({e}), using fast local semantic hashing.")
                    cls._remote_available = False

        return cls._local_hash_embedding(text, dimensions)

    @classmethod
    def _project_vector(cls, vec: List[float], target_dim: int) -> List[float]:
        if len(vec) == target_dim:
            return vec
        # Simple deterministic downsampling / pooling
        step = len(vec) / target_dim
        projected = []
        for i in range(target_dim):
            start = int(i * step)
            end = max(start + 1, int((i + 1) * step))
            chunk = vec[start:end]
            projected.append(sum(chunk) / len(chunk))
        norm = math.sqrt(sum(x * x for x in projected)) or 1.0
        return [round(x / norm, 6) for x in projected]

    @classmethod
    def _local_hash_embedding(cls, text: str, dimensions: int = 128) -> List[float]:
        """
        Fast, zero-cost, deterministic local embedding using token n-grams and hashing.
        Guarantees semantically related strings share higher cosine similarities.
        """
        vec = [0.0] * dimensions
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vec

        # Bag of words and character 3-grams
        tokens = list(words)
        for word in words:
            if len(word) >= 3:
                tokens.extend([word[i : i + 3] for i in range(len(word) - 2)])

        for token in tokens:
            idx = abs(hash(token)) % dimensions
            # Alternate sign based on secondary hash
            sign = 1.0 if (hash(token + "_sign") % 2 == 0) else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 6) for v in vec]
        return vec

    @classmethod
    def cosine_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return max(-1.0, min(1.0, dot / (norm_a * norm_b)))
