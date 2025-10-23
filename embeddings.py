from __future__ import annotations
import os
from typing import List

class Embedder:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class SBertEmbedder(Embedder):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        print(f"🔄 Loading embedding model: {model_name}")
        print(f"   (First time: ~1.3GB download, cached for future runs)")
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
        print(f"✅ Embedding model loaded successfully!")
    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()
