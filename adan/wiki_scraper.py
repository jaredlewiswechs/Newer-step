#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON WIKI SCRAPER
Intelligent Wikipedia scraper using kinematic linguistics + semantic search

Key Features:
- DIFF-BASED: Only stores facts not already in KB (memory efficient)
- LINK CHAINING: Follows related links with depth control
- KINEMATIC EXTRACTION: Uses shape-based fact parsing
- SEMANTIC DEDUP: Fuzzy matching to avoid duplicate facts
- RATE LIMITED: Respects Wikipedia's API guidelines

"The question has shape. The fact has shape. Match shapes."

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import httpx
import re
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any
from pathlib import Path
from collections import deque
import sys

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adan.knowledge_store import get_knowledge_store, StoredFact
from adan.language_mechanics import get_language_mechanics

# Try to import kinematic analyzer
try:
    from adan.query_parser import get_query_parser, QueryShape
    HAS_KINEMATIC = True
except ImportError:
    HAS_KINEMATIC = False
    print("[SCRAPER] Kinematic parser not available, using regex fallback")

# Try to import semantic resolver
try:
    from adan.semantic_resolver import SemanticResolver
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False
    print("[SCRAPER] Semantic resolver not available")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ScraperConfig:
    """Scraper configuration."""
    max_depth: int = 2                    # How deep to follow links
    max_pages: int = 50                   # Max pages to scrape
    max_facts_per_page: int = 20          # Max facts to extract per page
    min_fact_length: int = 20             # Minimum fact length
    max_fact_length: int = 500            # Maximum fact length
    rate_limit_ms: int = 100              # Delay between requests (be nice to Wikipedia)
    similarity_threshold: float = 0.85    # Threshold for duplicate detection
    follow_categories: bool = True        # Follow category links
    follow_see_also: bool = True          # Follow "See also" links
    extract_infobox: bool = True          # Extract infobox facts
    extract_intro: bool = True            # Extract intro paragraph facts
    user_agent: str = "NewtonAgent/1.0 (Educational Research; contact@adacomputing.com)"


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC FACT PATTERNS
# Shape-based patterns for extracting structured facts from text
# ═══════════════════════════════════════════════════════════════════════════════

# Pattern: "X is Y" - Definition facts
PATTERN_IS = re.compile(
    r"(?P<subject>[A-Z][^.]*?)\s+(?:is|are|was|were)\s+(?:a|an|the)?\s*(?P<predicate>[^.]+)",
    re.IGNORECASE
)

# Pattern: "X, known as Y" - Alias facts  
PATTERN_KNOWN_AS = re.compile(
    r"(?P<subject>[^,]+),?\s+(?:also\s+)?(?:known|called|named)\s+(?:as|)\s+(?P<alias>[^,\.]+)",
    re.IGNORECASE
)

# Pattern: "X was born in Y" - Biographical facts
PATTERN_BORN = re.compile(
    r"(?P<subject>[A-Z][^.]*?)\s+was\s+born\s+(?:in|on)\s+(?P<date_place>[^.]+)",
    re.IGNORECASE
)

# Pattern: "X died in Y" - Death facts
PATTERN_DIED = re.compile(
    r"(?P<subject>[A-Z][^.]*?)\s+died\s+(?:in|on)\s+(?P<date_place>[^.]+)",
    re.IGNORECASE
)

# Pattern: "The capital of X is Y" - Geographic facts
PATTERN_CAPITAL = re.compile(
    r"(?:The\s+)?capital\s+(?:of|city\s+of)\s+(?P<country>[^.]+?)\s+is\s+(?P<capital>[^.]+)",
    re.IGNORECASE
)

# Pattern: "X has a population of Y" - Demographic facts
PATTERN_POPULATION = re.compile(
    r"(?P<place>[A-Z][^.]*?)\s+has\s+(?:a\s+)?population\s+of\s+(?:approximately\s+)?(?P<pop>[0-9,\.]+(?:\s*(?:million|billion|thousand))?)",
    re.IGNORECASE
)

# Pattern: "X founded/invented/discovered Y" - Historical facts
PATTERN_FOUNDED = re.compile(
    r"(?P<subject>[A-Z][^.]*?)\s+(?:founded|invented|discovered|created)\s+(?P<object>[^.]+)",
    re.IGNORECASE
)

# Pattern: "In YEAR, X" - Dated events
PATTERN_DATED = re.compile(
    r"In\s+(?P<year>\d{4}),?\s+(?P<event>[^.]+)",
    re.IGNORECASE
)

# Pattern: "X located in Y" - Location facts
PATTERN_LOCATED = re.compile(
    r"(?P<place>[A-Z][^.]*?)\s+(?:is\s+)?(?:located|situated)\s+in\s+(?P<location>[^.]+)",
    re.IGNORECASE
)

# All patterns with their fact types
FACT_PATTERNS = [
    (PATTERN_CAPITAL, "geography", "capital"),
    (PATTERN_POPULATION, "demographics", "population"),
    (PATTERN_BORN, "biography", "birth"),
    (PATTERN_DIED, "biography", "death"),
    (PATTERN_FOUNDED, "history", "founding"),
    (PATTERN_DATED, "history", "event"),
    (PATTERN_LOCATED, "geography", "location"),
    (PATTERN_KNOWN_AS, "general", "alias"),
    (PATTERN_IS, "general", "definition"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTED FACT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExtractedFact:
    """A fact extracted from Wikipedia."""
    key: str                    # Normalized key for lookup
    fact: str                   # The fact text
    category: str               # Category (geography, history, etc.)
    fact_type: str              # Specific type (capital, birth, etc.)
    source_page: str            # Wikipedia page title
    source_url: str             # Full URL
    confidence: float           # Extraction confidence
    hash: str = ""              # Content hash for dedup
    
    def __post_init__(self):
        # Generate content hash
        content = f"{self.key}:{self.fact}".lower()
        self.hash = hashlib.md5(content.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════════════════════════════
# SCRAPER STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ScraperStats:
    """Statistics for a scraping session."""
    pages_scraped: int = 0
    facts_extracted: int = 0
    facts_new: int = 0              # New facts (diff)
    facts_duplicate: int = 0        # Already in KB
    facts_similar: int = 0          # Similar to existing (fuzzy match)
    links_found: int = 0
    links_followed: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time
    
    @property
    def facts_per_second(self) -> float:
        if self.elapsed_seconds > 0:
            return self.facts_extracted / self.elapsed_seconds
        return 0


# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON WIKI SCRAPER
# ═══════════════════════════════════════════════════════════════════════════════

class NewtonWikiScraper:
    """
    Intelligent Wikipedia scraper using Newton's kinematic linguistics.
    
    Features:
    - Diff-based: Only stores NEW facts not in existing KB
    - Semantic dedup: Uses fuzzy matching to avoid duplicates
    - Link chaining: Follows related articles with depth control
    - Kinematic extraction: Shape-based fact parsing
    """
    
    WIKI_API = "https://en.wikipedia.org/w/api.php"
    WIKI_URL = "https://en.wikipedia.org/wiki/"
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.knowledge_store = get_knowledge_store()
        self.language_mechanics = get_language_mechanics()
        
        # Seen hashes for dedup
        self._seen_hashes: Set[str] = set()
        self._seen_pages: Set[str] = set()
        
        # Build hash set from existing KB
        self._load_existing_hashes()
        
        # HTTP client
        self._client: Optional[httpx.AsyncClient] = None
        
        # Stats
        self.stats = ScraperStats()
    
    def _load_existing_hashes(self):
        """Load hashes of existing facts for fast diff detection."""
        for fact in self.knowledge_store.get_all():
            content = f"{fact.key}:{fact.fact}".lower()
            h = hashlib.md5(content.encode()).hexdigest()[:12]
            self._seen_hashes.add(h)
        print(f"[SCRAPER] Loaded {len(self._seen_hashes)} existing fact hashes")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"User-Agent": self.config.user_agent},
                timeout=30.0
            )
        return self._client
    
    async def _fetch_page(self, title: str) -> Optional[Dict]:
        """Fetch a Wikipedia page via the API."""
        client = await self._get_client()
        
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts|links|categories",
            "exintro": False,  # Get full text
            "explaintext": True,
            "pllimit": 50,  # Links limit
            "cllimit": 20,  # Categories limit
            "format": "json",
            "redirects": 1
        }
        
        try:
            resp = await client.get(self.WIKI_API, params=params)
            data = resp.json()
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return None  # Page not found
                return page_data
            return None
            
        except Exception as e:
            print(f"[SCRAPER] Error fetching {title}: {e}")
            self.stats.errors += 1
            return None
    
    def _extract_facts_from_text(self, text: str, title: str) -> List[ExtractedFact]:
        """Extract structured facts from page text using kinematic patterns."""
        facts = []
        source_url = f"{self.WIKI_URL}{title.replace(' ', '_')}"
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # Skip short sentences
            if len(sentence) < self.config.min_fact_length:
                continue
            if len(sentence) > self.config.max_fact_length:
                continue
                
            # Try each pattern
            for pattern, category, fact_type in FACT_PATTERNS:
                match = pattern.search(sentence)
                if match:
                    # Build fact key and text based on pattern
                    groups = match.groupdict()
                    
                    if fact_type == "capital":
                        key = f"Capital of {groups.get('country', '').strip()}"
                        fact_text = f"The capital of {groups.get('country', '').strip()} is {groups.get('capital', '').strip()}."
                    elif fact_type == "population":
                        key = f"Population of {groups.get('place', '').strip()}"
                        fact_text = f"{groups.get('place', '').strip()} has a population of {groups.get('pop', '').strip()}."
                    elif fact_type == "birth":
                        key = f"Birth of {groups.get('subject', '').strip()}"
                        fact_text = sentence.strip()
                    elif fact_type == "death":
                        key = f"Death of {groups.get('subject', '').strip()}"
                        fact_text = sentence.strip()
                    elif fact_type == "event":
                        key = f"Event in {groups.get('year', '')}"
                        fact_text = sentence.strip()
                    else:
                        # Generic fact
                        subject = groups.get('subject', groups.get('place', title))
                        key = f"{subject.strip()[:50]}"
                        fact_text = sentence.strip()
                    
                    # Clean up
                    key = re.sub(r'\s+', ' ', key).strip()
                    fact_text = re.sub(r'\s+', ' ', fact_text).strip()
                    
                    if key and fact_text:
                        facts.append(ExtractedFact(
                            key=key,
                            fact=fact_text,
                            category=category.title(),
                            fact_type=fact_type,
                            source_page=title,
                            source_url=source_url,
                            confidence=0.8
                        ))
                    
                    break  # One pattern match per sentence
            
            # Limit facts per page
            if len(facts) >= self.config.max_facts_per_page:
                break
        
        return facts
    
    def _extract_links(self, page_data: Dict) -> List[str]:
        """Extract links to follow from page data."""
        links = []
        
        # Regular links
        for link in page_data.get("links", []):
            title = link.get("title", "")
            # Skip meta pages
            if ":" in title:
                continue
            links.append(title)
        
        self.stats.links_found += len(links)
        return links[:20]  # Limit links per page
    
    def _is_new_fact(self, fact: ExtractedFact) -> Tuple[bool, str]:
        """
        Check if fact is new using diff detection.
        
        Returns (is_new, reason)
        """
        # Check exact hash
        if fact.hash in self._seen_hashes:
            return False, "exact_duplicate"
        
        # Check fuzzy match against existing facts
        existing_keys = [f.key for f in self.knowledge_store.get_all()]
        
        # Use language mechanics for fuzzy matching
        match = self.language_mechanics.fuzzy_match(
            fact.key, 
            existing_keys, 
            threshold=self.config.similarity_threshold
        )
        
        if match:
            return False, f"similar_to:{match}"
        
        return True, "new"
    
    async def _store_fact(self, fact: ExtractedFact) -> bool:
        """Store a new fact in the knowledge store."""
        is_new, reason = self._is_new_fact(fact)
        
        if not is_new:
            if "duplicate" in reason:
                self.stats.facts_duplicate += 1
            else:
                self.stats.facts_similar += 1
            return False
        
        # Store it
        self.knowledge_store.add(
            key=fact.key,
            fact=fact.fact,
            category=fact.category,
            source=f"Wikipedia: {fact.source_page}",
            source_url=fact.source_url,
            confidence=fact.confidence,
            added_by="scraper"
        )
        
        # Mark as seen
        self._seen_hashes.add(fact.hash)
        self.stats.facts_new += 1
        
        return True
    
    async def scrape_page(self, title: str) -> List[ExtractedFact]:
        """Scrape a single Wikipedia page."""
        if title in self._seen_pages:
            return []
        self._seen_pages.add(title)
        
        # Rate limiting
        await asyncio.sleep(self.config.rate_limit_ms / 1000)
        
        print(f"[SCRAPER] Fetching: {title}")
        page_data = await self._fetch_page(title)
        
        if not page_data:
            return []
        
        self.stats.pages_scraped += 1
        
        # Extract text
        text = page_data.get("extract", "")
        if not text:
            return []
        
        # Extract facts
        facts = self._extract_facts_from_text(text, title)
        self.stats.facts_extracted += len(facts)
        
        # Store new facts
        for fact in facts:
            await self._store_fact(fact)
        
        return facts
    
    async def scrape_chain(
        self, 
        seed_title: str, 
        max_depth: int = None,
        max_pages: int = None
    ) -> ScraperStats:
        """
        Scrape Wikipedia starting from seed, following links.
        
        Uses BFS to explore related articles up to max_depth.
        """
        max_depth = max_depth or self.config.max_depth
        max_pages = max_pages or self.config.max_pages
        
        # BFS queue: (title, depth)
        queue = deque([(seed_title, 0)])
        
        print(f"\n{'='*60}")
        print(f"NEWTON WIKI SCRAPER")
        print(f"Seed: {seed_title}")
        print(f"Max Depth: {max_depth}, Max Pages: {max_pages}")
        print(f"{'='*60}\n")
        
        while queue and self.stats.pages_scraped < max_pages:
            title, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            # Scrape page
            facts = await self.scrape_page(title)
            
            # Get links to follow
            if depth < max_depth:
                page_data = await self._fetch_page(title)
                if page_data:
                    links = self._extract_links(page_data)
                    for link in links:
                        if link not in self._seen_pages:
                            queue.append((link, depth + 1))
                            self.stats.links_followed += 1
        
        # Cleanup
        if self._client:
            await self._client.aclose()
        
        return self.stats
    
    def print_stats(self):
        """Print scraping statistics."""
        s = self.stats
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Pages Scraped:    {s.pages_scraped}")
        print(f"Facts Extracted:  {s.facts_extracted}")
        print(f"  - New (diff):   {s.facts_new}")
        print(f"  - Duplicate:    {s.facts_duplicate}")
        print(f"  - Similar:      {s.facts_similar}")
        print(f"Links Found:      {s.links_found}")
        print(f"Links Followed:   {s.links_followed}")
        print(f"Errors:           {s.errors}")
        print(f"Time:             {s.elapsed_seconds:.1f}s")
        print(f"Speed:            {s.facts_per_second:.1f} facts/sec")
        print(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Test the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Newton Wikipedia Scraper")
    parser.add_argument("seed", nargs="?", default=None, 
                        help="Seed Wikipedia article title")
    parser.add_argument("--depth", type=int, default=1, help="Max link depth")
    parser.add_argument("--pages", type=int, default=10, help="Max pages to scrape")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()
    
    config = ScraperConfig(
        max_depth=args.depth,
        max_pages=args.pages,
        rate_limit_ms=150  # Be nice to Wikipedia
    )
    
    scraper = NewtonWikiScraper(config)
    
    if args.interactive or args.seed is None:
        # Interactive mode
        print("\n" + "="*60)
        print("NEWTON WIKI SCRAPER - Interactive Mode")
        print("="*60)
        print("Commands:")
        print("  <topic>       - Scrape Wikipedia for topic")
        print("  stats         - Show current statistics")
        print("  count         - Show total fact count")
        print("  search <q>    - Search stored facts")
        print("  quit          - Exit")
        print("="*60 + "\n")
        
        while True:
            try:
                cmd = input("wiki> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not cmd:
                continue
            
            if cmd.lower() == "quit":
                break
            elif cmd.lower() == "stats":
                scraper.print_stats()
            elif cmd.lower() == "count":
                store = get_knowledge_store()
                print(f"Total facts: {store.count()}")
            elif cmd.lower().startswith("search "):
                query = cmd[7:]
                store = get_knowledge_store()
                results = store.search(query)
                print(f"\nFound {len(results)} results for '{query}':")
                for fact, score in results[:10]:
                    print(f"  [{score:.2f}] {fact.key}: {fact.fact[:60]}...")
                print()
            else:
                # Scrape topic
                print(f"\nScraping: {cmd}")
                await scraper.scrape_chain(cmd)
                scraper.print_stats()
    else:
        try:
            await scraper.scrape_chain(args.seed)
        finally:
            scraper.print_stats()


if __name__ == "__main__":
    asyncio.run(main())
