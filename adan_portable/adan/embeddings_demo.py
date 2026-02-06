#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON EMBEDDINGS DEMO
Semantic search using Ollama local embeddings
═══════════════════════════════════════════════════════════════════════════════
"""
import requests
import math
from typing import List, Tuple
import time


OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> List[float]:
    """Get embedding vector from Ollama."""
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text}
    )
    return response.json()["embedding"]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot_product / (norm_a * norm_b)


# Sample knowledge base facts
SAMPLE_FACTS = [
    "The capital of France is Paris.",
    "The mitochondria is the powerhouse of the cell.",
    "Water has the chemical formula H2O, meaning two hydrogen atoms and one oxygen.",
    "Newton's first law states that an object at rest stays at rest.",
    "DNA stands for Deoxyribonucleic Acid.",
    "The speed of light is 299,792,458 meters per second.",
    "Python was created by Guido van Rossum in 1991.",
    "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.",
    "The quadratic formula is x = (-b ± √(b²-4ac)) / 2a.",
    "Photosynthesis converts sunlight, water, and CO2 into glucose and oxygen.",
]


def semantic_search(query: str, facts: List[str], top_k: int = 3) -> List[Tuple[str, float]]:
    """Find most similar facts to query."""
    query_embedding = get_embedding(query)
    
    similarities = []
    for fact in facts:
        fact_embedding = get_embedding(fact)
        sim = cosine_similarity(query_embedding, fact_embedding)
        similarities.append((fact, sim))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def main():
    print("=" * 70)
    print("NEWTON EMBEDDINGS DEMO")
    print("Semantic Search with Ollama (nomic-embed-text)")
    print("=" * 70)
    
    # Pre-embed all facts
    print("\n📚 Pre-embedding knowledge base facts...")
    start = time.time()
    fact_embeddings = [(fact, get_embedding(fact)) for fact in SAMPLE_FACTS]
    print(f"   Embedded {len(SAMPLE_FACTS)} facts in {time.time() - start:.2f}s")
    print(f"   Vector dimensions: {len(fact_embeddings[0][1])}")
    
    # Test queries - including ones that DON'T match keywords
    test_queries = [
        # Exact keyword matches (current KB handles these)
        "What is the capital of France?",
        
        # SEMANTIC matches (current KB would MISS these)
        "What city is France's government located in?",
        "Tell me about the cell's energy factory",
        "Who created the Python programming language?",
        "What makes plants produce food?",
        "Explain the molecule that carries genetic code",
    ]
    
    print("\n" + "=" * 70)
    print("SEMANTIC SEARCH RESULTS")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        
        start = time.time()
        query_emb = get_embedding(query)
        
        # Calculate similarities
        results = []
        for fact, fact_emb in fact_embeddings:
            sim = cosine_similarity(query_emb, fact_emb)
            results.append((fact, sim))
        
        results.sort(key=lambda x: x[1], reverse=True)
        elapsed = (time.time() - start) * 1000
        
        print(f"   ⏱️  Search time: {elapsed:.1f}ms")
        print(f"   📊 Top matches:")
        for i, (fact, sim) in enumerate(results[:3], 1):
            marker = "✓" if sim > 0.7 else "○" if sim > 0.5 else "·"
            print(f"      {marker} [{sim:.3f}] {fact[:60]}...")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print("""
    Current Newton KB: Keyword matching only
      "capital of France" ✓ matches
      "France's government city" ✗ MISS
    
    With embeddings: Semantic understanding
      "capital of France" ✓ matches  
      "France's government city" ✓ MATCHES (same meaning!)
    
    Newton + Embeddings = Best of both worlds
      - Fast keyword lookup for exact matches
      - Semantic fallback for natural language
    """)


if __name__ == "__main__":
    main()
