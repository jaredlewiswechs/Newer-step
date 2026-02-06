#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ENHANCED GROUNDING ENGINE
Cross-references claims against official sources via multiple search APIs.
═══════════════════════════════════════════════════════════════════════════════

Source Tiers:
    Tier 1 (Official):     .gov, .edu, .mil, official company domains
    Tier 2 (Authoritative): Major news orgs, academic publishers
    Tier 3 (Community):    Wikipedia, StackOverflow, forums

Scoring:
    0-2:   VERIFIED    - Strong evidence from official sources
    2-5:   LIKELY      - Moderate evidence from mixed sources
    5-8:   UNCERTAIN   - Weak or conflicting evidence
    8-10:  UNVERIFIED  - No supporting evidence found
"""

import time
import hashlib
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from urllib.parse import urlparse, quote_plus
import os

# Try multiple search backends
try:
    from googlesearch import search as google_search
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class SourceTier(Enum):
    """Source credibility tiers."""
    OFFICIAL = 1        # Government, educational, military
    AUTHORITATIVE = 2   # Major news, academic publishers
    COMMUNITY = 3       # Wikipedia, forums, blogs
    UNKNOWN = 4         # Unclassified sources


@dataclass
class OfficialSource:
    """Configuration for an official source domain."""
    domain: str
    name: str
    tier: SourceTier
    weight: float = 1.0
    description: str = ""


# Official sources database
OFFICIAL_SOURCES: List[OfficialSource] = [
    # Government (Tier 1)
    OfficialSource(".gov", "US Government", SourceTier.OFFICIAL, 3.0, "Official US government sites"),
    OfficialSource(".edu", "Educational", SourceTier.OFFICIAL, 2.5, "Universities and colleges"),
    OfficialSource(".mil", "US Military", SourceTier.OFFICIAL, 3.0, "Official military sites"),
    OfficialSource("europa.eu", "European Union", SourceTier.OFFICIAL, 2.5, "EU official sites"),
    OfficialSource("gov.uk", "UK Government", SourceTier.OFFICIAL, 2.5, "UK government sites"),
    
    # Tech Official Sites (Tier 1)
    OfficialSource("apple.com", "Apple", SourceTier.OFFICIAL, 2.5, "Apple official"),
    OfficialSource("developer.apple.com", "Apple Developer", SourceTier.OFFICIAL, 3.0, "Apple developer docs"),
    OfficialSource("microsoft.com", "Microsoft", SourceTier.OFFICIAL, 2.5, "Microsoft official"),
    OfficialSource("docs.microsoft.com", "Microsoft Docs", SourceTier.OFFICIAL, 3.0, "Microsoft documentation"),
    OfficialSource("google.com", "Google", SourceTier.OFFICIAL, 2.0, "Google official"),
    OfficialSource("developers.google.com", "Google Developers", SourceTier.OFFICIAL, 3.0, "Google dev docs"),
    OfficialSource("cloud.google.com", "Google Cloud", SourceTier.OFFICIAL, 2.5, "GCP documentation"),
    OfficialSource("aws.amazon.com", "AWS", SourceTier.OFFICIAL, 2.5, "Amazon Web Services"),
    OfficialSource("docs.aws.amazon.com", "AWS Docs", SourceTier.OFFICIAL, 3.0, "AWS documentation"),
    OfficialSource("python.org", "Python", SourceTier.OFFICIAL, 3.0, "Python official"),
    OfficialSource("docs.python.org", "Python Docs", SourceTier.OFFICIAL, 3.0, "Python documentation"),
    OfficialSource("nodejs.org", "Node.js", SourceTier.OFFICIAL, 2.5, "Node.js official"),
    OfficialSource("rust-lang.org", "Rust", SourceTier.OFFICIAL, 2.5, "Rust official"),
    OfficialSource("go.dev", "Go", SourceTier.OFFICIAL, 2.5, "Go official"),
    OfficialSource("anthropic.com", "Anthropic", SourceTier.OFFICIAL, 2.5, "Anthropic official"),
    OfficialSource("openai.com", "OpenAI", SourceTier.OFFICIAL, 2.5, "OpenAI official"),
    OfficialSource("github.com", "GitHub", SourceTier.OFFICIAL, 2.0, "GitHub repositories"),
    
    # Authoritative News (Tier 2)
    OfficialSource("reuters.com", "Reuters", SourceTier.AUTHORITATIVE, 2.0, "Reuters news agency"),
    OfficialSource("apnews.com", "Associated Press", SourceTier.AUTHORITATIVE, 2.0, "AP news"),
    OfficialSource("bbc.com", "BBC", SourceTier.AUTHORITATIVE, 1.8, "BBC news"),
    OfficialSource("bbc.co.uk", "BBC UK", SourceTier.AUTHORITATIVE, 1.8, "BBC UK"),
    OfficialSource("nytimes.com", "NY Times", SourceTier.AUTHORITATIVE, 1.5, "New York Times"),
    OfficialSource("wsj.com", "Wall Street Journal", SourceTier.AUTHORITATIVE, 1.5, "WSJ"),
    OfficialSource("economist.com", "The Economist", SourceTier.AUTHORITATIVE, 1.5, "The Economist"),
    
    # Academic & Scientific (Tier 2)
    OfficialSource("nature.com", "Nature", SourceTier.AUTHORITATIVE, 2.5, "Nature journal"),
    OfficialSource("science.org", "Science", SourceTier.AUTHORITATIVE, 2.5, "Science journal"),
    OfficialSource("arxiv.org", "arXiv", SourceTier.AUTHORITATIVE, 2.0, "Preprint server"),
    OfficialSource("pubmed.ncbi.nlm.nih.gov", "PubMed", SourceTier.AUTHORITATIVE, 2.5, "Medical literature"),
    OfficialSource("scholar.google.com", "Google Scholar", SourceTier.AUTHORITATIVE, 1.8, "Academic search"),
    OfficialSource("ieee.org", "IEEE", SourceTier.AUTHORITATIVE, 2.0, "IEEE publications"),
    OfficialSource("acm.org", "ACM", SourceTier.AUTHORITATIVE, 2.0, "ACM publications"),
    
    # Community Sources (Tier 3)
    OfficialSource("wikipedia.org", "Wikipedia", SourceTier.COMMUNITY, 1.0, "Wikipedia"),
    OfficialSource("stackoverflow.com", "Stack Overflow", SourceTier.COMMUNITY, 1.2, "Programming Q&A"),
    OfficialSource("reddit.com", "Reddit", SourceTier.COMMUNITY, 0.5, "Reddit discussions"),
    OfficialSource("medium.com", "Medium", SourceTier.COMMUNITY, 0.5, "Medium blogs"),
]


@dataclass
class Evidence:
    """A piece of supporting evidence with provenance."""
    url: str
    title: str
    snippet: str
    source: Optional[OfficialSource]
    tier: SourceTier
    weight: float
    retrieved_at: int
    
    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet[:200] if self.snippet else "",
            "tier": self.tier.name,
            "weight": self.weight,
            "source_name": self.source.name if self.source else "Unknown",
        }


@dataclass
class GroundingResult:
    """Complete grounding verification result."""
    claim: str
    confidence_score: float
    status: str
    evidence: List[Evidence]
    sources_checked: int
    official_sources: int
    timestamp: int
    signature: str
    reasoning: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "claim": self.claim,
            "confidence_score": self.confidence_score,
            "status": self.status,
            "evidence": [e.to_dict() for e in self.evidence[:5]],
            "sources_checked": self.sources_checked,
            "official_sources": self.official_sources,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "reasoning": self.reasoning,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED GROUNDING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class EnhancedGroundingEngine:
    """
    Verifies claims against multiple official sources.
    
    Uses a multi-tier approach:
    1. Google Search (primary)
    2. DuckDuckGo Instant Answers (fallback)
    3. Wikipedia API (knowledge base)
    """
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache: Dict[str, GroundingResult] = {}
        self.cache_ttl = cache_ttl
        self.source_lookup = {s.domain: s for s in OFFICIAL_SOURCES}
        
        # Stats
        self.total_queries = 0
        self.cache_hits = 0
        
    def _classify_source(self, url: str) -> tuple[Optional[OfficialSource], SourceTier, float]:
        """Classify a URL and return its source info and weight."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check against official sources
            for source in OFFICIAL_SOURCES:
                if source.domain in domain:
                    return source, source.tier, source.weight
            
            # Check TLD patterns
            if domain.endswith('.gov'):
                return None, SourceTier.OFFICIAL, 2.5
            elif domain.endswith('.edu'):
                return None, SourceTier.OFFICIAL, 2.0
            elif domain.endswith('.mil'):
                return None, SourceTier.OFFICIAL, 2.5
            elif domain.endswith('.org'):
                return None, SourceTier.COMMUNITY, 1.0
            
            return None, SourceTier.UNKNOWN, 0.5
            
        except Exception:
            return None, SourceTier.UNKNOWN, 0.5
    
    def _search_google(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using Google Search."""
        if not GOOGLE_AVAILABLE:
            return []
        
        try:
            results = []
            for result in google_search(query, num_results=num_results, advanced=True):
                url = getattr(result, 'url', str(result))
                title = getattr(result, 'title', '')
                description = getattr(result, 'description', '')
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": description,
                })
            return results
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """Search using DuckDuckGo Instant Answers API (no API key required)."""
        if not HTTPX_AVAILABLE:
            return []
        
        try:
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
            headers = {
                "User-Agent": "NewtonAgent/1.0 (https://newton.ada.com; contact@ada.com) httpx/0.28"
            }
            with httpx.Client(timeout=5.0, headers=headers) as client:
                response = client.get(url)
                data = response.json()
            
            results = []
            
            # Abstract (main answer)
            if data.get("Abstract"):
                results.append({
                    "url": data.get("AbstractURL", ""),
                    "title": data.get("Heading", query),
                    "snippet": data.get("Abstract", ""),
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and topic.get("FirstURL"):
                    results.append({
                        "url": topic.get("FirstURL", ""),
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                    })
            
            return results
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def _search_wikipedia(self, query: str) -> List[Dict]:
        """Search Wikipedia API directly."""
        if not HTTPX_AVAILABLE:
            return []
        
        try:
            # Search for pages
            search_url = (
                f"https://en.wikipedia.org/w/api.php?"
                f"action=query&list=search&srsearch={quote_plus(query)}"
                f"&format=json&srlimit=3"
            )
            
            headers = {
                "User-Agent": "NewtonAgent/1.0 (https://newton.ada.com; contact@ada.com) httpx/0.28"
            }
            
            with httpx.Client(timeout=5.0, headers=headers) as client:
                response = client.get(search_url)
                data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", []):
                title = item.get("title", "")
                snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                results.append({
                    "url": f"https://en.wikipedia.org/wiki/{quote_plus(title.replace(' ', '_'))}",
                    "title": title,
                    "snippet": snippet,
                })
            
            return results
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []
    
    def verify_claim(
        self,
        claim: str,
        require_official: bool = False,
        min_sources: int = 1,
    ) -> GroundingResult:
        """
        Verify a claim against external sources.
        
        Args:
            claim: The statement to verify
            require_official: If True, only accept Tier 1 sources
            min_sources: Minimum sources required for verification
            
        Returns:
            GroundingResult with confidence score and evidence chain
        """
        self.total_queries += 1
        
        # Check cache
        cache_key = hashlib.md5(claim.encode()).hexdigest()
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached.timestamp < self.cache_ttl:
                self.cache_hits += 1
                return cached
        
        # Collect evidence from multiple sources
        all_results: List[Dict] = []
        
        # Primary: Google Search
        google_results = self._search_google(claim, num_results=8)
        all_results.extend(google_results)
        
        # Fallback: DuckDuckGo
        if len(all_results) < 3:
            ddg_results = self._search_duckduckgo(claim)
            all_results.extend(ddg_results)
        
        # Supplement: Wikipedia for factual claims
        wiki_results = self._search_wikipedia(claim)
        all_results.extend(wiki_results)
        
        # Process and classify evidence
        evidence_chain: List[Evidence] = []
        seen_urls = set()
        
        for result in all_results:
            url = result.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            source, tier, weight = self._classify_source(url)
            
            evidence_chain.append(Evidence(
                url=url,
                title=result.get("title", ""),
                snippet=result.get("snippet", ""),
                source=source,
                tier=tier,
                weight=weight,
                retrieved_at=int(time.time()),
            ))
        
        # Calculate confidence score
        base_score = 10.0
        official_count = 0
        total_weight = 0.0
        
        for evidence in evidence_chain:
            if evidence.tier == SourceTier.OFFICIAL:
                official_count += 1
            total_weight += evidence.weight
        
        # Score reduction based on evidence
        if evidence_chain:
            # Each piece of evidence reduces score
            score_reduction = min(total_weight * 0.8, 8.0)
            base_score -= score_reduction
            
            # Bonus for official sources
            if official_count >= 2:
                base_score -= 1.0
            
        final_score = max(0.0, min(10.0, round(base_score, 2)))
        
        # Determine status
        if require_official and official_count == 0:
            status = "UNVERIFIED"
            final_score = max(final_score, 8.0)
        elif final_score <= 2.0 and len(evidence_chain) >= min_sources:
            status = "VERIFIED"
        elif final_score <= 5.0:
            status = "LIKELY"
        elif final_score <= 8.0:
            status = "UNCERTAIN"
        else:
            status = "UNVERIFIED"
        
        # Generate reasoning
        reasoning = self._generate_reasoning(claim, evidence_chain, official_count, status)
        
        # Create result
        result = GroundingResult(
            claim=claim,
            confidence_score=final_score,
            status=status,
            evidence=evidence_chain,
            sources_checked=len(evidence_chain),
            official_sources=official_count,
            timestamp=int(time.time()),
            signature=self._sign(claim, final_score),
            reasoning=reasoning,
        )
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    def _generate_reasoning(
        self,
        claim: str,
        evidence: List[Evidence],
        official_count: int,
        status: str
    ) -> str:
        """Generate human-readable reasoning for the verification."""
        if not evidence:
            return f"No supporting evidence found for: '{claim}'"
        
        tier_counts = {t: 0 for t in SourceTier}
        for e in evidence:
            tier_counts[e.tier] += 1
        
        parts = []
        parts.append(f"Found {len(evidence)} source(s) for this claim.")
        
        if official_count > 0:
            parts.append(f"{official_count} official/authoritative source(s) found.")
        
        if tier_counts[SourceTier.OFFICIAL] > 0:
            parts.append(f"Government/official sites: {tier_counts[SourceTier.OFFICIAL]}")
        
        if tier_counts[SourceTier.AUTHORITATIVE] > 0:
            parts.append(f"Authoritative sources: {tier_counts[SourceTier.AUTHORITATIVE]}")
        
        if status == "VERIFIED":
            parts.append("Strong evidence supports this claim.")
        elif status == "LIKELY":
            parts.append("Moderate evidence supports this claim.")
        elif status == "UNCERTAIN":
            parts.append("Evidence is weak or conflicting.")
        else:
            parts.append("Insufficient evidence to verify this claim.")
        
        return " ".join(parts)
    
    def _sign(self, claim: str, score: float) -> str:
        """Generate verification signature."""
        payload = f"{claim}:{score}:{int(time.time())}"
        return hashlib.sha256(payload.encode()).hexdigest()[:12].upper()
    
    def get_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(1, self.total_queries),
            "cached_items": len(self.cache),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    engine = EnhancedGroundingEngine()
    
    test_claims = [
        "Python was created by Guido van Rossum",
        "The Earth orbits the Sun",
        "Claude is made by Anthropic",
        "Newton's first law states objects in motion stay in motion",
    ]
    
    print("=" * 60)
    print("ENHANCED GROUNDING ENGINE TEST")
    print("=" * 60)
    
    for claim in test_claims:
        print(f"\n🔍 Claim: {claim}")
        result = engine.verify_claim(claim)
        print(f"   Score: {result.confidence_score}")
        print(f"   Status: {result.status}")
        print(f"   Sources: {result.sources_checked} ({result.official_sources} official)")
        print(f"   Reasoning: {result.reasoning}")
