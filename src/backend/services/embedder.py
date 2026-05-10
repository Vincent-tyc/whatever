import hashlib
import os
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from src.backend.config import EMBEDDING_MODEL

_model = None
_fallback_reason = None
FALLBACK_DIM = 384


def get_model():
    global _model, _fallback_reason
    if _fallback_reason:
        return None

    use_sentence_transformer = os.getenv("USE_SENTENCE_TRANSFORMER", "").lower() in {"1", "true", "yes"}
    is_local_model = Path(EMBEDDING_MODEL).exists()
    if not use_sentence_transformer and not is_local_model:
        _fallback_reason = "using local hash embedding; set USE_SENTENCE_TRANSFORMER=1 or EMBEDDING_MODEL to a local path to use SentenceTransformer"
        return None

    if _model is None:
        try:
            _model = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as e:
            _fallback_reason = str(e)
            return None
    return _model


def _hash_encode(texts: list[str]) -> np.ndarray:
    vectors = np.zeros((len(texts), FALLBACK_DIM), dtype=np.float32)
    token_pattern = re.compile(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+")

    for row, text in enumerate(texts):
        tokens = token_pattern.findall(text.lower())
        if not tokens:
            tokens = [text[:128]]

        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % FALLBACK_DIM
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vectors[row, idx] += sign

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return vectors / norms


def encode_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    if model is None:
        return _hash_encode(texts)
    return model.encode(texts, normalize_embeddings=True)


def embedding_backend() -> dict[str, str | bool | None]:
    return {
        "model": EMBEDDING_MODEL,
        "using_fallback": _fallback_reason is not None,
        "fallback_reason": _fallback_reason,
    }


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
