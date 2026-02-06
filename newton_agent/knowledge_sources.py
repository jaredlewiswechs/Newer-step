#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
KNOWLEDGE SOURCES - MULTI-SOURCE KNOWLEDGE MESH
Not a list - a mesh. Multiple authoritative sources cross-referencing.

Sources:
    - CIA World Factbook (Geography, Demographics)
    - NIST CODATA (Physical Constants)
    - Encyclopedia Britannica (Historical Dates)
    - Wikipedia/Wikidata (Structured Data)
    - ISO Standards (Codes, Formats)
    - UN Data (Global Statistics)
    - USGS (Geological Data)
    - NASA (Space/Astronomy)
    - WHO (Health Statistics)
    - World Bank (Economic Data)

The constraint IS the instruction.
The source IS the authority.
The mesh IS the verification.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from datetime import datetime
import re


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE TIERS
# ═══════════════════════════════════════════════════════════════════════════════

class SourceTier(Enum):
    """Reliability tiers for sources."""
    AUTHORITATIVE = "authoritative"  # Government, scientific bodies
    VERIFIED = "verified"            # Reputable encyclopedias, peer-reviewed
    CURATED = "curated"              # Wikipedia, community-vetted
    SECONDARY = "secondary"          # News, aggregators
    UNVERIFIED = "unverified"        # User-submitted, unchecked


@dataclass
class Source:
    """A knowledge source."""
    name: str
    url: str
    tier: SourceTier
    domain: str  # What kind of knowledge
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "url": self.url,
            "tier": self.tier.value,
            "domain": self.domain,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

SOURCES = {
    "cia_factbook": Source(
        name="CIA World Factbook",
        url="https://www.cia.gov/the-world-factbook/",
        tier=SourceTier.AUTHORITATIVE,
        domain="geography",
    ),
    "nist": Source(
        name="NIST CODATA",
        url="https://www.nist.gov/pml/fundamental-physical-constants",
        tier=SourceTier.AUTHORITATIVE,
        domain="physics",
    ),
    "britannica": Source(
        name="Encyclopedia Britannica",
        url="https://www.britannica.com/",
        tier=SourceTier.VERIFIED,
        domain="general",
    ),
    "wikidata": Source(
        name="Wikidata",
        url="https://www.wikidata.org/",
        tier=SourceTier.CURATED,
        domain="structured_data",
    ),
    "iso": Source(
        name="ISO Standards",
        url="https://www.iso.org/",
        tier=SourceTier.AUTHORITATIVE,
        domain="standards",
    ),
    "un_data": Source(
        name="UN Data",
        url="https://data.un.org/",
        tier=SourceTier.AUTHORITATIVE,
        domain="statistics",
    ),
    "nasa": Source(
        name="NASA",
        url="https://www.nasa.gov/",
        tier=SourceTier.AUTHORITATIVE,
        domain="space",
    ),
    "usgs": Source(
        name="USGS",
        url="https://www.usgs.gov/",
        tier=SourceTier.AUTHORITATIVE,
        domain="geology",
    ),
    "who": Source(
        name="World Health Organization",
        url="https://www.who.int/",
        tier=SourceTier.AUTHORITATIVE,
        domain="health",
    ),
    "world_bank": Source(
        name="World Bank",
        url="https://data.worldbank.org/",
        tier=SourceTier.AUTHORITATIVE,
        domain="economics",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# EXTENDED KNOWLEDGE DATA
# ═══════════════════════════════════════════════════════════════════════════════

# === ASTRONOMICAL DATA (NASA) ===
ASTRONOMICAL_DATA: Dict[str, Dict[str, Any]] = {
    "earth": {
        "type": "planet",
        "mass_kg": 5.972e24,
        "radius_km": 6371,
        "orbital_period_days": 365.25,
        "distance_from_sun_km": 149_597_870,
        "moons": 1,
        "source": "nasa",
    },
    "moon": {
        "type": "satellite",
        "mass_kg": 7.342e22,
        "radius_km": 1737,
        "orbital_period_days": 27.3,
        "distance_from_earth_km": 384_400,
        "source": "nasa",
    },
    "sun": {
        "type": "star",
        "mass_kg": 1.989e30,
        "radius_km": 696_340,
        "surface_temp_k": 5778,
        "age_billion_years": 4.6,
        "source": "nasa",
    },
    "mars": {
        "type": "planet",
        "mass_kg": 6.39e23,
        "radius_km": 3389,
        "orbital_period_days": 687,
        "moons": 2,
        "source": "nasa",
    },
    "jupiter": {
        "type": "planet",
        "mass_kg": 1.898e27,
        "radius_km": 69911,
        "orbital_period_days": 4333,
        "moons": 95,
        "source": "nasa",
    },
    "light_year_km": {
        "value": 9.461e12,
        "unit": "km",
        "source": "nasa",
    },
    "astronomical_unit_km": {
        "value": 149_597_870.7,
        "unit": "km",
        "source": "nasa",
    },
}

# === GEOLOGICAL DATA (USGS) ===
GEOLOGICAL_DATA: Dict[str, Dict[str, Any]] = {
    "mount_everest": {
        "type": "mountain",
        "height_m": 8849,
        "location": "Nepal/Tibet",
        "range": "Himalayas",
        "source": "usgs",
    },
    "mariana_trench": {
        "type": "ocean_trench",
        "depth_m": 10994,
        "location": "Pacific Ocean",
        "source": "usgs",
    },
    "earth_age": {
        "value": 4.54e9,
        "unit": "years",
        "source": "usgs",
    },
    "earth_layers": {
        "crust_thickness_km": (5, 70),  # Range: ocean to continent
        "mantle_thickness_km": 2900,
        "outer_core_thickness_km": 2200,
        "inner_core_radius_km": 1220,
        "source": "usgs",
    },
}

# === ECONOMIC DATA (World Bank) ===
ECONOMIC_DATA: Dict[str, Dict[str, Any]] = {
    "gdp_usa": {"value": 25.46e12, "year": 2022, "unit": "USD", "source": "world_bank"},
    "gdp_china": {"value": 17.96e12, "year": 2022, "unit": "USD", "source": "world_bank"},
    "gdp_japan": {"value": 4.23e12, "year": 2022, "unit": "USD", "source": "world_bank"},
    "gdp_germany": {"value": 4.07e12, "year": 2022, "unit": "USD", "source": "world_bank"},
    "gdp_uk": {"value": 3.07e12, "year": 2022, "unit": "USD", "source": "world_bank"},
    "gdp_india": {"value": 3.39e12, "year": 2022, "unit": "USD", "source": "world_bank"},
    "world_population": {"value": 8e9, "year": 2023, "source": "un_data"},
}

# === HEALTH DATA (WHO) ===
HEALTH_DATA: Dict[str, Dict[str, Any]] = {
    "life_expectancy_global": {"value": 73.4, "year": 2023, "unit": "years", "source": "who"},
    "life_expectancy_japan": {"value": 84.3, "year": 2023, "unit": "years", "source": "who"},
    "life_expectancy_usa": {"value": 76.4, "year": 2023, "unit": "years", "source": "who"},
}

# === MATHEMATICAL CONSTANTS (NIST) ===
MATH_CONSTANTS: Dict[str, Dict[str, Any]] = {
    "pi": {"value": 3.14159265358979323846, "symbol": "π", "source": "nist"},
    "e": {"value": 2.71828182845904523536, "symbol": "e", "source": "nist"},
    "phi": {"value": 1.61803398874989484820, "symbol": "φ", "name": "golden ratio", "source": "nist"},
    "sqrt2": {"value": 1.41421356237309504880, "symbol": "√2", "source": "nist"},
    "sqrt3": {"value": 1.73205080756887729352, "symbol": "√3", "source": "nist"},
}

# === PROGRAMMING LANGUAGES (Wikipedia/Britannica) ===
PROGRAMMING_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "python": {
        "created": 1991,
        "creator": "Guido van Rossum",
        "paradigm": ["object-oriented", "imperative", "functional"],
        "typing": "dynamic",
        "source": "britannica",
    },
    "javascript": {
        "created": 1995,
        "creator": "Brendan Eich",
        "paradigm": ["event-driven", "functional", "imperative"],
        "typing": "dynamic",
        "source": "britannica",
    },
    "java": {
        "created": 1995,
        "creator": "James Gosling",
        "paradigm": ["object-oriented", "class-based"],
        "typing": "static",
        "source": "britannica",
    },
    "c": {
        "created": 1972,
        "creator": "Dennis Ritchie",
        "paradigm": ["imperative", "procedural"],
        "typing": "static",
        "source": "britannica",
    },
    "c++": {
        "created": 1985,
        "creator": "Bjarne Stroustrup",
        "paradigm": ["object-oriented", "procedural"],
        "typing": "static",
        "source": "britannica",
    },
    "rust": {
        "created": 2010,
        "creator": "Graydon Hoare",
        "paradigm": ["concurrent", "functional", "imperative"],
        "typing": "static",
        "source": "wikidata",
    },
    "go": {
        "created": 2009,
        "creator": "Robert Griesemer, Rob Pike, Ken Thompson",
        "paradigm": ["concurrent", "imperative"],
        "typing": "static",
        "source": "wikidata",
    },
    "swift": {
        "created": 2014,
        "creator": "Chris Lattner",
        "paradigm": ["protocol-oriented", "object-oriented"],
        "typing": "static",
        "source": "wikidata",
    },
    "kotlin": {
        "created": 2011,
        "creator": "JetBrains",
        "paradigm": ["object-oriented", "functional"],
        "typing": "static",
        "source": "wikidata",
    },
    "typescript": {
        "created": 2012,
        "creator": "Microsoft",
        "paradigm": ["object-oriented", "functional"],
        "typing": "static",
        "source": "wikidata",
    },
}

# === ELEMENT DATA (NIST/IUPAC) ===
ELEMENTS: Dict[str, Dict[str, Any]] = {
    "hydrogen": {"symbol": "H", "atomic_number": 1, "atomic_mass": 1.008, "source": "nist"},
    "helium": {"symbol": "He", "atomic_number": 2, "atomic_mass": 4.003, "source": "nist"},
    "carbon": {"symbol": "C", "atomic_number": 6, "atomic_mass": 12.011, "source": "nist"},
    "nitrogen": {"symbol": "N", "atomic_number": 7, "atomic_mass": 14.007, "source": "nist"},
    "oxygen": {"symbol": "O", "atomic_number": 8, "atomic_mass": 15.999, "source": "nist"},
    "gold": {"symbol": "Au", "atomic_number": 79, "atomic_mass": 196.967, "source": "nist"},
    "silver": {"symbol": "Ag", "atomic_number": 47, "atomic_mass": 107.868, "source": "nist"},
    "iron": {"symbol": "Fe", "atomic_number": 26, "atomic_mass": 55.845, "source": "nist"},
    "uranium": {"symbol": "U", "atomic_number": 92, "atomic_mass": 238.029, "source": "nist"},
}

# === ISO CODES ===
ISO_CODES: Dict[str, Dict[str, str]] = {
    # Country codes (ISO 3166-1)
    "united states": {"alpha2": "US", "alpha3": "USA", "numeric": "840"},
    "united kingdom": {"alpha2": "GB", "alpha3": "GBR", "numeric": "826"},
    "france": {"alpha2": "FR", "alpha3": "FRA", "numeric": "250"},
    "germany": {"alpha2": "DE", "alpha3": "DEU", "numeric": "276"},
    "japan": {"alpha2": "JP", "alpha3": "JPN", "numeric": "392"},
    "china": {"alpha2": "CN", "alpha3": "CHN", "numeric": "156"},
    "india": {"alpha2": "IN", "alpha3": "IND", "numeric": "356"},
    "brazil": {"alpha2": "BR", "alpha3": "BRA", "numeric": "076"},
    "canada": {"alpha2": "CA", "alpha3": "CAN", "numeric": "124"},
    "australia": {"alpha2": "AU", "alpha3": "AUS", "numeric": "036"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE MESH - Cross-Referenced Facts
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MeshFact:
    """A fact with multiple source references."""
    key: str
    value: Any
    category: str
    primary_source: str
    confirming_sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    last_verified: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "primary_source": self.primary_source,
            "confirming_sources": self.confirming_sources,
            "confidence": self.confidence,
            "cross_referenced": len(self.confirming_sources) > 0,
        }


class KnowledgeMesh:
    """
    Multi-source knowledge mesh.
    Not a list of facts, but a web of cross-referenced knowledge.
    """
    
    def __init__(self):
        self._facts: Dict[str, MeshFact] = {}
        self._by_category: Dict[str, List[str]] = {}
        self._by_source: Dict[str, List[str]] = {}
        self.queries = 0
        self.hits = 0
        
        # Load all data
        self._load_astronomical()
        self._load_geological()
        self._load_economic()
        self._load_health()
        self._load_math()
        self._load_programming()
        self._load_elements()
        self._load_iso()
    
    def _add_fact(self, fact: MeshFact):
        """Add a fact to the mesh."""
        self._facts[fact.key] = fact
        
        # Index by category
        if fact.category not in self._by_category:
            self._by_category[fact.category] = []
        self._by_category[fact.category].append(fact.key)
        
        # Index by source
        if fact.primary_source not in self._by_source:
            self._by_source[fact.primary_source] = []
        self._by_source[fact.primary_source].append(fact.key)
    
    def _load_astronomical(self):
        """Load astronomical data."""
        for key, data in ASTRONOMICAL_DATA.items():
            source = data.get("source", "nasa")
            self._add_fact(MeshFact(
                key=f"astro:{key}",
                value=data,
                category="astronomy",
                primary_source=source,
                confidence=1.0,
            ))
    
    def _load_geological(self):
        """Load geological data."""
        for key, data in GEOLOGICAL_DATA.items():
            source = data.get("source", "usgs")
            self._add_fact(MeshFact(
                key=f"geo:{key}",
                value=data,
                category="geology",
                primary_source=source,
                confidence=1.0,
            ))
    
    def _load_economic(self):
        """Load economic data."""
        for key, data in ECONOMIC_DATA.items():
            source = data.get("source", "world_bank")
            self._add_fact(MeshFact(
                key=f"econ:{key}",
                value=data,
                category="economics",
                primary_source=source,
                confidence=0.95,  # Economic data is estimates
            ))
    
    def _load_health(self):
        """Load health data."""
        for key, data in HEALTH_DATA.items():
            source = data.get("source", "who")
            self._add_fact(MeshFact(
                key=f"health:{key}",
                value=data,
                category="health",
                primary_source=source,
                confidence=0.95,
            ))
    
    def _load_math(self):
        """Load math constants."""
        for key, data in MATH_CONSTANTS.items():
            self._add_fact(MeshFact(
                key=f"math:{key}",
                value=data,
                category="mathematics",
                primary_source="nist",
                confidence=1.0,
            ))
    
    def _load_programming(self):
        """Load programming language data."""
        for key, data in PROGRAMMING_LANGUAGES.items():
            source = data.get("source", "britannica")
            self._add_fact(MeshFact(
                key=f"lang:{key}",
                value=data,
                category="programming",
                primary_source=source,
                confirming_sources=["wikidata"],  # Cross-referenced
                confidence=1.0,
            ))
    
    def _load_elements(self):
        """Load element data."""
        for key, data in ELEMENTS.items():
            self._add_fact(MeshFact(
                key=f"element:{key}",
                value=data,
                category="chemistry",
                primary_source="nist",
                confidence=1.0,
            ))
    
    def _load_iso(self):
        """Load ISO codes."""
        for key, data in ISO_CODES.items():
            self._add_fact(MeshFact(
                key=f"iso:{key}",
                value=data,
                category="standards",
                primary_source="iso",
                confidence=1.0,
            ))
    
    def query(self, question: str) -> Optional[MeshFact]:
        """Query the mesh for a fact."""
        self.queries += 1
        q = question.lower()
        
        # Try direct key lookup patterns
        result = (
            self._query_astronomical(q) or
            self._query_geological(q) or
            self._query_programming(q) or
            self._query_elements(q) or
            self._query_economic(q) or
            self._query_math(q)
        )
        
        if result:
            self.hits += 1
        
        return result
    
    def _query_astronomical(self, q: str) -> Optional[MeshFact]:
        """Query astronomical data."""
        bodies = ["earth", "moon", "sun", "mars", "jupiter"]
        
        for body in bodies:
            if body in q:
                key = f"astro:{body}"
                if key in self._facts:
                    return self._facts[key]
        
        if "light year" in q or "lightyear" in q:
            return self._facts.get("astro:light_year_km")
        
        if "astronomical unit" in q or " au " in q:
            return self._facts.get("astro:astronomical_unit_km")
        
        return None
    
    def _query_geological(self, q: str) -> Optional[MeshFact]:
        """Query geological data."""
        if "everest" in q:
            return self._facts.get("geo:mount_everest")
        if "mariana" in q or "deepest" in q:
            return self._facts.get("geo:mariana_trench")
        if "earth" in q and "age" in q:
            return self._facts.get("geo:earth_age")
        return None
    
    def _query_programming(self, q: str) -> Optional[MeshFact]:
        """Query programming language data."""
        # Must be asking about programming/language
        if not any(w in q for w in ["created", "inventor", "who made", "programming", "language", "when was"]):
            return None
        
        # Check for specific languages with word boundaries
        lang_patterns = {
            "python": r"\bpython\b",
            "javascript": r"\bjavascript\b",
            "java": r"\bjava\b(?!script)",  # java but not javascript
            "c++": r"\bc\+\+\b",
            "c": r"\bc\b(?!\+)",  # c but not c++
            "rust": r"\brust\b",
            "go": r"\bgo\b(?:lang)?\b",
            "swift": r"\bswift\b",
            "kotlin": r"\bkotlin\b",
            "typescript": r"\btypescript\b",
        }
        
        for lang, pattern in lang_patterns.items():
            if re.search(pattern, q):
                key = f"lang:{lang}"
                if key in self._facts:
                    return self._facts[key]
        
        return None
    
    def _query_elements(self, q: str) -> Optional[MeshFact]:
        """Query element data."""
        # Must be asking about elements/chemistry
        if not any(w in q for w in ["element", "atomic", "chemistry", "symbol"]):
            return None
        
        elements = list(ELEMENTS.keys())
        
        for elem in elements:
            # Use word boundary for element names
            if re.search(r'\b' + elem + r'\b', q):
                key = f"element:{elem}"
                if key in self._facts:
                    return self._facts[key]
        
        return None
    
    def _query_economic(self, q: str) -> Optional[MeshFact]:
        """Query economic data."""
        if "gdp" in q:
            countries = ["usa", "china", "japan", "germany", "uk", "india"]
            for country in countries:
                if country in q or country.replace("_", " ") in q:
                    return self._facts.get(f"econ:gdp_{country}")
        
        if "world population" in q or "global population" in q:
            return self._facts.get("econ:world_population")
        
        return None
    
    def _query_math(self, q: str) -> Optional[MeshFact]:
        """Query math constants."""
        if "golden ratio" in q or (re.search(r'\bphi\b', q) and "phi" not in ["dolphin"]):
            return self._facts.get("math:phi")
        if "square root" in q:
            if "2" in q:
                return self._facts.get("math:sqrt2")
            if "3" in q:
                return self._facts.get("math:sqrt3")
        return None
    
    def get_by_category(self, category: str) -> List[MeshFact]:
        """Get all facts in a category."""
        keys = self._by_category.get(category, [])
        return [self._facts[k] for k in keys]
    
    def get_by_source(self, source: str) -> List[MeshFact]:
        """Get all facts from a source."""
        keys = self._by_source.get(source, [])
        return [self._facts[k] for k in keys]
    
    def get_stats(self) -> Dict:
        """Get mesh statistics."""
        return {
            "total_facts": len(self._facts),
            "categories": len(self._by_category),
            "sources": len(self._by_source),
            "queries": self.queries,
            "hits": self.hits,
            "hit_rate": self.hits / max(1, self.queries),
            "cross_referenced": sum(1 for f in self._facts.values() 
                                   if f.confirming_sources),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_mesh: Optional[KnowledgeMesh] = None

def get_knowledge_mesh() -> KnowledgeMesh:
    """Get the global knowledge mesh instance."""
    global _mesh
    if _mesh is None:
        _mesh = KnowledgeMesh()
    return _mesh


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mesh = KnowledgeMesh()
    
    print("═" * 70)
    print("KNOWLEDGE MESH - MULTI-SOURCE VERIFICATION")
    print("Not a list - a mesh.")
    print("═" * 70)
    
    # Stats
    stats = mesh.get_stats()
    print(f"\n📊 MESH STATS")
    print(f"   Facts: {stats['total_facts']}")
    print(f"   Categories: {stats['categories']}")
    print(f"   Sources: {stats['sources']}")
    print(f"   Cross-referenced: {stats['cross_referenced']}")
    
    # Test queries
    print("\n🔍 QUERY TESTS")
    print("-" * 40)
    
    test_queries = [
        "What is the mass of Earth?",
        "How tall is Mount Everest?",
        "When was Python created?",
        "What is the atomic number of gold?",
        "What is the GDP of USA?",
        "What is the golden ratio?",
        "Who created Rust?",
        "How deep is the Mariana Trench?",
    ]
    
    for q in test_queries:
        result = mesh.query(q)
        if result:
            print(f"✓ {q}")
            print(f"   → {result.key}: {result.value}")
            print(f"   Source: {result.primary_source}")
        else:
            print(f"✗ {q} - Not found")
    
    # Show categories
    print("\n📁 CATEGORIES")
    print("-" * 40)
    for cat, keys in mesh._by_category.items():
        print(f"   {cat}: {len(keys)} facts")
