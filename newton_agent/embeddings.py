#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON EMBEDDINGS ENGINE
Local semantic search using Ollama embeddings
═══════════════════════════════════════════════════════════════════════════════

Newton Philosophy:
- Local first (Ollama, no cloud)
- Deterministic (same text → same vector)
- Verifiable (show similarity scores)
- Bounded execution (timeout, dimension limits)
"""
import math
import hashlib
import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class EmbeddingConfig:
    """Configuration for embedding engine."""
    ollama_url: str = "http://localhost:11434"
    model: str = "nomic-embed-text"
    similarity_threshold: float = 0.60  # Minimum to consider a match (0.6 is reasonable)
    timeout_seconds: float = 5.0
    cache_embeddings: bool = True
    cache_dir: str = ".newton_cache"


@dataclass 
class SemanticMatch:
    """A semantic search result."""
    text: str
    similarity: float
    key: str  # Original key/identifier


class EmbeddingEngine:
    """
    Local embedding engine using Ollama.
    Provides semantic search with verification scores.
    """
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self._embedding_cache: Dict[str, List[float]] = {}
        self._fact_embeddings: Dict[str, Tuple[str, List[float]]] = {}
        self._available: Optional[bool] = None
        self._dimensions: Optional[int] = None
        
        # Load cache from disk if enabled
        if self.config.cache_embeddings:
            self._load_cache()
    
    def is_available(self) -> bool:
        """Check if Ollama embedding model is available."""
        if self._available is not None:
            return self._available
        
        if not HAS_REQUESTS:
            self._available = False
            return False
        
        try:
            response = requests.get(
                f"{self.config.ollama_url}/api/tags",
                timeout=2.0
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                self._available = any(self.config.model in name for name in model_names)
            else:
                self._available = False
        except Exception:
            self._available = False
        
        return self._available
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for text."""
        if not self.is_available():
            return None
        
        # Check cache first
        cache_key = self._cache_key(text)
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        try:
            response = requests.post(
                f"{self.config.ollama_url}/api/embeddings",
                json={"model": self.config.model, "prompt": text},
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code == 200:
                embedding = response.json().get("embedding")
                if embedding:
                    self._embedding_cache[cache_key] = embedding
                    if self._dimensions is None:
                        self._dimensions = len(embedding)
                    return embedding
        except Exception:
            pass
        
        return None
    
    def index_facts(self, facts: Dict[str, str]) -> int:
        """
        Pre-embed a dictionary of facts for semantic search.
        Args:
            facts: Dict mapping key -> fact text
        Returns:
            Number of facts indexed
        """
        if not self.is_available():
            return 0
        
        indexed = 0
        for key, text in facts.items():
            embedding = self.get_embedding(text)
            if embedding:
                self._fact_embeddings[key] = (text, embedding)
                indexed += 1
        
        # Save cache after indexing
        if self.config.cache_embeddings and indexed > 0:
            self._save_cache()
        
        return indexed
    
    def search(self, query: str, top_k: int = 3) -> List[SemanticMatch]:
        """
        Semantic search across indexed facts.
        Returns matches above similarity threshold.
        """
        if not self.is_available() or not self._fact_embeddings:
            return []
        
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []
        
        results = []
        for key, (text, fact_embedding) in self._fact_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, fact_embedding)
            if similarity >= self.config.similarity_threshold:
                results.append(SemanticMatch(
                    text=text,
                    similarity=similarity,
                    key=key
                ))
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:top_k]
    
    def find_best_match(self, query: str) -> Optional[SemanticMatch]:
        """Find the single best semantic match."""
        matches = self.search(query, top_k=1)
        return matches[0] if matches else None
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
    
    @staticmethod
    def _cache_key(text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    def _get_cache_path(self) -> Path:
        """Get path to cache file."""
        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / "embeddings_cache.json"
    
    def _save_cache(self):
        """Save embedding cache to disk."""
        try:
            cache_path = self._get_cache_path()
            cache_data = {
                "model": self.config.model,
                "embeddings": self._embedding_cache,
                "facts": {k: v[0] for k, v in self._fact_embeddings.items()},
                "fact_keys": list(self._fact_embeddings.keys()),
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except Exception:
            pass
    
    def _load_cache(self):
        """Load embedding cache from disk."""
        try:
            cache_path = self._get_cache_path()
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                
                # Only use cache if same model
                if cache_data.get("model") == self.config.model:
                    self._embedding_cache = cache_data.get("embeddings", {})
                    
                    # Rebuild fact_embeddings from cached facts and embeddings
                    cached_facts = cache_data.get("facts", {})
                    for key, text in cached_facts.items():
                        cache_key = self._cache_key(text)
                        if cache_key in self._embedding_cache:
                            self._fact_embeddings[key] = (text, self._embedding_cache[cache_key])
        except Exception:
            pass
    
    def get_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            "available": self.is_available(),
            "model": self.config.model,
            "dimensions": self._dimensions,
            "cached_embeddings": len(self._embedding_cache),
            "indexed_facts": len(self._fact_embeddings),
            "similarity_threshold": self.config.similarity_threshold,
        }


# Global instance (lazy loaded)
_embedding_engine: Optional[EmbeddingEngine] = None


def get_embedding_engine() -> EmbeddingEngine:
    """Get or create the global embedding engine."""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = EmbeddingEngine()
    return _embedding_engine


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("EMBEDDING ENGINE TEST")
    print("=" * 60)
    
    engine = EmbeddingEngine()
    print(f"\n📊 Status: {engine.get_stats()}")
    
    if not engine.is_available():
        print("\n❌ Ollama embedding model not available")
        print("   Run: ollama pull nomic-embed-text")
        exit(1)
    
    # Test facts
    test_facts = {
        "france_capital": "The capital of France is Paris.",
        "mitochondria": "The mitochondria is the powerhouse of the cell.",
        "water": "Water has the chemical formula H2O.",
        "newton_first": "Newton's first law states objects at rest stay at rest.",
        "dna": "DNA stands for Deoxyribonucleic Acid.",
    }
    
    print(f"\n📚 Indexing {len(test_facts)} facts...")
    indexed = engine.index_facts(test_facts)
    print(f"   Indexed: {indexed}")
    
    # Test queries
    test_queries = [
        "What is the capital of France?",
        "What city does France's government meet in?",  # Semantic match
        "Tell me about the cell's energy factory",  # Semantic match
        "What does DNA stand for?",
    ]
    
    print("\n" + "=" * 60)
    print("SEMANTIC SEARCH TEST")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n❓ {query}")
        match = engine.find_best_match(query)
        if match:
            print(f"   ✓ [{match.similarity:.3f}] {match.text}")
        else:
            print(f"   ✗ No match above threshold")
    
    print(f"\n📊 Final stats: {engine.get_stats()}")
