#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SEMANTIC RESOLVER
Beauty is in the eye of the beholder - meaning is contextual.

Uses Datamuse API (free, no key) to resolve semantic relationships.
═══════════════════════════════════════════════════════════════════════════════

"What city does France govern from?" 
→ extract: city, govern, from, France
→ resolve: govern + city = "seat of government" = capital
→ shape: CAPITAL_OF(France)

The meaning is the average of neighbors. We choose what's beautiful.
"""

import urllib.request
import urllib.parse
import json
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class SemanticWord:
    """A word with its semantic score."""
    word: str
    score: int
    tags: List[str]
    
    @property
    def is_noun(self) -> bool:
        return "n" in self.tags
    
    @property
    def is_verb(self) -> bool:
        return "v" in self.tags
    
    @property
    def is_synonym(self) -> bool:
        return "syn" in self.tags


class SemanticResolver:
    """
    Resolve semantic meaning using Datamuse API.
    
    Beauty is in the beholder's eye - we define what's meaningful
    by mapping semantic clusters to our KB shapes.
    """
    
    BASE_URL = "https://api.datamuse.com/words"
    
    # Semantic clusters that map to KB shapes
    # The BEAUTY: we define what's meaningful by the overlap with our KB
    CAPITAL_CLUSTER = {"capital", "seat", "government", "rule", "govern", "headquarters", "center", "city"}
    FOUNDER_CLUSTER = {"founder", "found", "create", "created", "start", "started", "build", "built", "establish", "originate", "begin", "began", "commence", "launched"}
    ELEMENT_CLUSTER = {"element", "atom", "atomic", "chemical", "periodic", "symbol", "molecule", "compound"}
    POPULATION_CLUSTER = {"population", "people", "inhabitants", "citizens", "residents", "live", "living", "populate"}
    LANGUAGE_CLUSTER = {"language", "speak", "tongue", "dialect", "speech", "talk", "words", "verbalize"}
    
    # Cache to avoid repeated API calls
    _cache: Dict[str, List[SemanticWord]] = {}
    
    def __init__(self):
        pass
    
    def means_like(self, word: str, max_results: int = 20) -> List[SemanticWord]:
        """Get words that mean like the given word."""
        cache_key = f"ml:{word}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"{self.BASE_URL}?ml={urllib.parse.quote(word)}&max={max_results}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                results = [
                    SemanticWord(
                        word=item["word"],
                        score=item.get("score", 0),
                        tags=item.get("tags", [])
                    )
                    for item in data
                ]
                self._cache[cache_key] = results
                return results
        except Exception as e:
            print(f"[SemanticResolver] API error: {e}")
            return []
    
    def synonyms(self, word: str, max_results: int = 10) -> List[SemanticWord]:
        """Get synonyms of the given word."""
        cache_key = f"syn:{word}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"{self.BASE_URL}?rel_syn={urllib.parse.quote(word)}&max={max_results}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                results = [
                    SemanticWord(
                        word=item["word"],
                        score=item.get("score", 0),
                        tags=item.get("tags", [])
                    )
                    for item in data
                ]
                self._cache[cache_key] = results
                return results
        except Exception as e:
            print(f"[SemanticResolver] API error: {e}")
            return []
    
    def related_to(self, word: str, topic: str, max_results: int = 10) -> List[SemanticWord]:
        """Get words related to word that are also about topic."""
        cache_key = f"rel:{word}:{topic}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"{self.BASE_URL}?ml={urllib.parse.quote(word)}&topics={urllib.parse.quote(topic)}&max={max_results}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                results = [
                    SemanticWord(
                        word=item["word"],
                        score=item.get("score", 0),
                        tags=item.get("tags", [])
                    )
                    for item in data
                ]
                self._cache[cache_key] = results
                return results
        except Exception as e:
            print(f"[SemanticResolver] API error: {e}")
            return []
    
    def get_semantic_field(self, words: List[str]) -> Set[str]:
        """Get the semantic field (all related meanings) for a list of words."""
        field = set()
        for word in words:
            field.add(word.lower())
            for sw in self.means_like(word, max_results=10):
                field.add(sw.word.lower())
        return field
    
    def detect_shape(self, query: str) -> Optional[str]:
        """
        Detect the KB shape from a query using semantic resolution.
        
        "What city does France govern from?" 
        → words: [city, govern, from, France]
        → semantic field includes: capital, seat, government
        → shape: CAPITAL_OF
        """
        # Extract meaningful words (skip stopwords)
        stopwords = {"what", "is", "the", "a", "an", "does", "do", "from", "to", "of", "in", "for", "who", "when", "where", "how", "which", "that", "this"}
        words = [w.lower() for w in query.split() if w.lower() not in stopwords and len(w) > 2]
        
        if not words:
            return None
        
        # Get semantic field
        field = self.get_semantic_field(words)
        
        # Check overlap with known clusters
        capital_overlap = len(field & self.CAPITAL_CLUSTER)
        founder_overlap = len(field & self.FOUNDER_CLUSTER)
        element_overlap = len(field & self.ELEMENT_CLUSTER)
        population_overlap = len(field & self.POPULATION_CLUSTER)
        language_overlap = len(field & self.LANGUAGE_CLUSTER)
        
        # Return the shape with highest overlap
        overlaps = [
            (capital_overlap, "CAPITAL_OF"),
            (founder_overlap, "FOUNDER_OF"),
            (element_overlap, "ELEMENT_INFO"),
            (population_overlap, "POPULATION_OF"),
            (language_overlap, "LANGUAGE_OF"),
        ]
        
        best = max(overlaps, key=lambda x: x[0])
        if best[0] >= 2:  # Need at least 2 words overlapping
            return best[1]
        
        return None
    
    def extract_entity(self, query: str) -> Optional[str]:
        """
        Extract the main entity (noun) from a query.
        
        "What city does France govern from?" → France
        "Who founded Apple?" → Apple
        """
        # Common patterns for entities
        import re
        
        # Capitalized words that aren't at sentence start
        words = query.split()
        entities = []
        
        for i, word in enumerate(words):
            clean = re.sub(r'[^\w]', '', word)
            if clean and clean[0].isupper():
                # Skip if first word (might just be sentence start)
                if i == 0 and clean.lower() in {"what", "who", "when", "where", "how", "which", "the", "a"}:
                    continue
                entities.append(clean)
        
        # Return last entity (usually the subject)
        if entities:
            return entities[-1]
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("SEMANTIC RESOLVER TEST")
    print("Beauty is in the eye of the beholder - meaning is contextual")
    print("=" * 70)
    print()
    
    resolver = SemanticResolver()
    
    # Test the problematic query
    test_queries = [
        "What city does France govern from?",
        "Where does Japan rule from?",
        "Who started Microsoft?",
        "Who created Google?",
        "What is the capital of Germany?",
        "atomic structure of carbon",
        "How many people live in China?",
        "What language do they speak in Brazil?",
    ]
    
    for query in test_queries:
        print(f"❓ {query}")
        
        # Extract words
        stopwords = {"what", "is", "the", "a", "an", "does", "do", "from", "to", "of", "in", "for", "who", "when", "where", "how", "which", "that", "this"}
        words = [w.lower() for w in query.split() if w.lower() not in stopwords and len(w) > 2]
        print(f"   Words: {words}")
        
        # Get semantic field (limited for display)
        field_sample = set()
        for w in words[:3]:  # Limit API calls
            for sw in resolver.means_like(w, max_results=5):
                field_sample.add(sw.word)
        print(f"   Semantic neighbors: {list(field_sample)[:8]}")
        
        shape = resolver.detect_shape(query)
        entity = resolver.extract_entity(query)
        print(f"   → Shape: {shape}")
        print(f"   → Entity: {entity}")
        print()
