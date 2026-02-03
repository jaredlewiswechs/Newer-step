#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
VERIFIED KNOWLEDGE BASE
Pre-verified facts from authoritative sources (CIA World Factbook, etc.)
═══════════════════════════════════════════════════════════════════════════════

These facts are considered GROUND TRUTH - no LLM needed.
Source: CIA World Factbook, ISO standards, official government data.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import re


@dataclass
class VerifiedFact:
    """A pre-verified fact with provenance."""
    fact: str
    category: str
    source: str
    source_url: str
    confidence: float = 1.0  # 1.0 = absolute certainty
    
    def to_dict(self) -> Dict:
        return {
            "fact": self.fact,
            "category": self.category,
            "source": self.source,
            "source_url": self.source_url,
            "confidence": self.confidence,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CIA WORLD FACTBOOK DATA
# Source: https://www.cia.gov/the-world-factbook/
# ═══════════════════════════════════════════════════════════════════════════════

COUNTRY_CAPITALS: Dict[str, str] = {
    # Major countries
    "france": "Paris",
    "germany": "Berlin",
    "italy": "Rome",
    "spain": "Madrid",
    "portugal": "Lisbon",
    "united kingdom": "London",
    "uk": "London",
    "england": "London",
    "ireland": "Dublin",
    "netherlands": "Amsterdam",
    "belgium": "Brussels",
    "switzerland": "Bern",
    "austria": "Vienna",
    "poland": "Warsaw",
    "czech republic": "Prague",
    "czechia": "Prague",
    "hungary": "Budapest",
    "romania": "Bucharest",
    "bulgaria": "Sofia",
    "greece": "Athens",
    "turkey": "Ankara",
    "russia": "Moscow",
    "ukraine": "Kyiv",
    "sweden": "Stockholm",
    "norway": "Oslo",
    "finland": "Helsinki",
    "denmark": "Copenhagen",
    
    # Americas
    "united states": "Washington, D.C.",
    "usa": "Washington, D.C.",
    "us": "Washington, D.C.",
    "america": "Washington, D.C.",
    "canada": "Ottawa",
    "mexico": "Mexico City",
    "brazil": "Brasília",
    "argentina": "Buenos Aires",
    "chile": "Santiago",
    "colombia": "Bogotá",
    "peru": "Lima",
    "venezuela": "Caracas",
    "cuba": "Havana",
    
    # Asia
    "china": "Beijing",
    "japan": "Tokyo",
    "south korea": "Seoul",
    "korea": "Seoul",
    "north korea": "Pyongyang",
    "india": "New Delhi",
    "pakistan": "Islamabad",
    "bangladesh": "Dhaka",
    "indonesia": "Jakarta",
    "thailand": "Bangkok",
    "vietnam": "Hanoi",
    "philippines": "Manila",
    "malaysia": "Kuala Lumpur",
    "singapore": "Singapore",
    "taiwan": "Taipei",
    
    # Middle East
    "israel": "Jerusalem",
    "saudi arabia": "Riyadh",
    "iran": "Tehran",
    "iraq": "Baghdad",
    "egypt": "Cairo",
    "united arab emirates": "Abu Dhabi",
    "uae": "Abu Dhabi",
    "qatar": "Doha",
    "kuwait": "Kuwait City",
    
    # Africa
    "south africa": "Pretoria",
    "nigeria": "Abuja",
    "kenya": "Nairobi",
    "ethiopia": "Addis Ababa",
    "morocco": "Rabat",
    "algeria": "Algiers",
    "tunisia": "Tunis",
    
    # Oceania
    "australia": "Canberra",
    "new zealand": "Wellington",
}

COUNTRY_POPULATIONS: Dict[str, tuple[int, int]] = {
    # (population, year)
    "china": (1_400_000_000, 2024),
    "india": (1_420_000_000, 2024),
    "united states": (335_000_000, 2024),
    "indonesia": (277_000_000, 2024),
    "pakistan": (240_000_000, 2024),
    "brazil": (216_000_000, 2024),
    "nigeria": (230_000_000, 2024),
    "bangladesh": (173_000_000, 2024),
    "russia": (144_000_000, 2024),
    "japan": (124_000_000, 2024),
    "mexico": (130_000_000, 2024),
    "germany": (84_000_000, 2024),
    "france": (68_000_000, 2024),
    "uk": (67_000_000, 2024),
    "italy": (59_000_000, 2024),
    "canada": (40_000_000, 2024),
    "australia": (26_000_000, 2024),
}

COUNTRY_LANGUAGES: Dict[str, List[str]] = {
    "france": ["French"],
    "germany": ["German"],
    "spain": ["Spanish", "Catalan", "Basque", "Galician"],
    "italy": ["Italian"],
    "japan": ["Japanese"],
    "china": ["Mandarin Chinese"],
    "brazil": ["Portuguese"],
    "russia": ["Russian"],
    "india": ["Hindi", "English"],
    "united states": ["English"],
    "mexico": ["Spanish"],
    "canada": ["English", "French"],
}

COUNTRY_CURRENCIES: Dict[str, tuple[str, str]] = {
    # (currency name, code)
    "united states": ("US Dollar", "USD"),
    "usa": ("US Dollar", "USD"),
    "european union": ("Euro", "EUR"),
    "france": ("Euro", "EUR"),
    "germany": ("Euro", "EUR"),
    "italy": ("Euro", "EUR"),
    "spain": ("Euro", "EUR"),
    "japan": ("Japanese Yen", "JPY"),
    "united kingdom": ("British Pound", "GBP"),
    "uk": ("British Pound", "GBP"),
    "china": ("Chinese Yuan", "CNY"),
    "india": ("Indian Rupee", "INR"),
    "russia": ("Russian Ruble", "RUB"),
    "brazil": ("Brazilian Real", "BRL"),
    "canada": ("Canadian Dollar", "CAD"),
    "australia": ("Australian Dollar", "AUD"),
    "mexico": ("Mexican Peso", "MXN"),
    "south korea": ("South Korean Won", "KRW"),
    "switzerland": ("Swiss Franc", "CHF"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# SCIENTIFIC CONSTANTS
# Source: NIST, CODATA
# ═══════════════════════════════════════════════════════════════════════════════

SCIENTIFIC_CONSTANTS: Dict[str, tuple[float, str, str]] = {
    # (value, unit, description)
    "speed of light": (299_792_458, "m/s", "Speed of light in vacuum"),
    "c": (299_792_458, "m/s", "Speed of light in vacuum"),
    "gravitational constant": (6.67430e-11, "m³/(kg·s²)", "Gravitational constant"),
    "g": (9.80665, "m/s²", "Standard gravity"),
    "planck constant": (6.62607015e-34, "J·s", "Planck constant"),
    "avogadro number": (6.02214076e23, "mol⁻¹", "Avogadro constant"),
    "boltzmann constant": (1.380649e-23, "J/K", "Boltzmann constant"),
    "electron mass": (9.1093837015e-31, "kg", "Electron mass"),
    "proton mass": (1.67262192369e-27, "kg", "Proton mass"),
    "elementary charge": (1.602176634e-19, "C", "Elementary charge"),
    "pi": (3.14159265358979323846, "", "Pi"),
    "e": (2.71828182845904523536, "", "Euler's number"),
    "golden ratio": (1.61803398874989484820, "", "Golden ratio (phi)"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORICAL DATES
# Source: Encyclopedia Britannica, official records
# ═══════════════════════════════════════════════════════════════════════════════

HISTORICAL_DATES: Dict[str, tuple[str, str]] = {
    # (date/year, description)
    "python created": ("1991", "Python programming language first released by Guido van Rossum"),
    "python released": ("1991", "Python 0.9.0 released February 1991"),
    "javascript created": ("1995", "JavaScript created by Brendan Eich at Netscape"),
    "java created": ("1995", "Java released by Sun Microsystems"),
    "c created": ("1972", "C programming language developed by Dennis Ritchie"),
    "world wide web": ("1989", "World Wide Web invented by Tim Berners-Lee at CERN"),
    "internet created": ("1969", "ARPANET, precursor to internet, established"),
    "first iphone": ("2007", "Apple released the first iPhone on June 29, 2007"),
    "moon landing": ("1969", "Apollo 11 landed on the Moon on July 20, 1969"),
    "wwii ended": ("1945", "World War II ended September 2, 1945"),
    "wwi ended": ("1918", "World War I ended November 11, 1918"),
    "declaration of independence": ("1776", "US Declaration of Independence signed July 4, 1776"),
    "french revolution": ("1789", "French Revolution began July 14, 1789"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# COMPANY/ORGANIZATION FACTS
# Source: Official company records, SEC filings
# ═══════════════════════════════════════════════════════════════════════════════

COMPANY_FACTS: Dict[str, Dict[str, Any]] = {
    "apple": {
        "founded": "1976",
        "founders": ["Steve Jobs", "Steve Wozniak", "Ronald Wayne"],
        "headquarters": "Cupertino, California",
        "ceo": "Tim Cook",
    },
    "microsoft": {
        "founded": "1975",
        "founders": ["Bill Gates", "Paul Allen"],
        "headquarters": "Redmond, Washington",
        "ceo": "Satya Nadella",
    },
    "google": {
        "founded": "1998",
        "founders": ["Larry Page", "Sergey Brin"],
        "headquarters": "Mountain View, California",
        "parent": "Alphabet Inc.",
    },
    "amazon": {
        "founded": "1994",
        "founders": ["Jeff Bezos"],
        "headquarters": "Seattle, Washington",
    },
    "anthropic": {
        "founded": "2021",
        "founders": ["Dario Amodei", "Daniela Amodei"],
        "headquarters": "San Francisco, California",
        "known_for": "Claude AI assistant",
    },
    "openai": {
        "founded": "2015",
        "founders": ["Sam Altman", "Elon Musk", "others"],
        "headquarters": "San Francisco, California",
        "known_for": "ChatGPT, GPT-4",
    },
    "tesla": {
        "founded": "2003",
        "founders": ["Martin Eberhard", "Marc Tarpenning"],
        "headquarters": "Austin, Texas",
        "ceo": "Elon Musk",
    },
    "meta": {
        "founded": "2004",
        "founders": ["Mark Zuckerberg"],
        "headquarters": "Menlo Park, California",
        "formerly": "Facebook",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeBase:
    """
    Pre-verified knowledge base for instant fact retrieval.
    No LLM needed for known facts.
    """
    
    CIA_FACTBOOK_URL = "https://www.cia.gov/the-world-factbook/"
    NIST_URL = "https://www.nist.gov/pml/fundamental-physical-constants"
    
    def __init__(self):
        self.queries = 0
        self.hits = 0
    
    def query(self, question: str) -> Optional[VerifiedFact]:
        """
        Query the knowledge base for a verified fact.
        Returns None if fact not found.
        """
        self.queries += 1
        question_lower = question.lower().strip()
        
        # Try each category
        result = (
            self._query_capital(question_lower) or
            self._query_population(question_lower) or
            self._query_language(question_lower) or
            self._query_currency(question_lower) or
            self._query_scientific(question_lower) or
            self._query_historical(question_lower) or
            self._query_company(question_lower)
        )
        
        if result:
            self.hits += 1
        
        return result
    
    def _extract_country(self, text: str) -> Optional[str]:
        """Extract country name from question."""
        # Common patterns
        patterns = [
            r"capital of (\w+[\w\s]*)",
            r"(\w+[\w\s]*)'s capital",
            r"in (\w+[\w\s]*)",
            r"of (\w+[\w\s]*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                country = match.group(1).strip().lower()
                # Clean up
                country = country.rstrip('?.,!')
                if country in COUNTRY_CAPITALS:
                    return country
        
        # Direct lookup
        for country in COUNTRY_CAPITALS:
            if country in text:
                return country
        
        return None
    
    def _query_capital(self, question: str) -> Optional[VerifiedFact]:
        """Query for capital cities."""
        if "capital" not in question:
            return None
        
        country = self._extract_country(question)
        if country and country in COUNTRY_CAPITALS:
            capital = COUNTRY_CAPITALS[country]
            return VerifiedFact(
                fact=f"The capital of {country.title()} is {capital}.",
                category="geography",
                source="CIA World Factbook",
                source_url=self.CIA_FACTBOOK_URL,
                confidence=1.0,
            )
        return None
    
    def _query_population(self, question: str) -> Optional[VerifiedFact]:
        """Query for population data."""
        if "population" not in question:
            return None
        
        for country, (pop, year) in COUNTRY_POPULATIONS.items():
            if country in question:
                formatted = f"{pop:,}"
                return VerifiedFact(
                    fact=f"The population of {country.title()} is approximately {formatted} ({year} estimate).",
                    category="demographics",
                    source="CIA World Factbook",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=0.95,  # Estimates
                )
        return None
    
    def _query_language(self, question: str) -> Optional[VerifiedFact]:
        """Query for official languages."""
        if "language" not in question and "speak" not in question:
            return None
        
        for country, languages in COUNTRY_LANGUAGES.items():
            if country in question:
                lang_str = ", ".join(languages)
                return VerifiedFact(
                    fact=f"The official language(s) of {country.title()}: {lang_str}.",
                    category="linguistics",
                    source="CIA World Factbook",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=1.0,
                )
        return None
    
    def _query_currency(self, question: str) -> Optional[VerifiedFact]:
        """Query for currencies."""
        if "currency" not in question and "money" not in question:
            return None
        
        for country, (name, code) in COUNTRY_CURRENCIES.items():
            if country in question:
                return VerifiedFact(
                    fact=f"The currency of {country.title()} is the {name} ({code}).",
                    category="economics",
                    source="ISO 4217",
                    source_url="https://www.iso.org/iso-4217-currency-codes.html",
                    confidence=1.0,
                )
        return None
    
    def _query_scientific(self, question: str) -> Optional[VerifiedFact]:
        """Query for scientific constants."""
        # Only match if specifically asking about constants/values
        if not any(word in question for word in ["constant", "value of", "what is pi", "what is e", "speed of light", "gravity"]):
            return None
            
        for const_name, (value, unit, desc) in SCIENTIFIC_CONSTANTS.items():
            # Require word boundary match for short names
            if len(const_name) <= 2:
                pattern = r'\b' + re.escape(const_name) + r'\b'
                if not re.search(pattern, question):
                    continue
            elif const_name in question:
                pass
            else:
                continue
                
            if unit:
                fact_str = f"{desc}: {value} {unit}"
            else:
                fact_str = f"{desc}: {value}"
            return VerifiedFact(
                fact=fact_str,
                category="science",
                source="NIST CODATA",
                source_url=self.NIST_URL,
                confidence=1.0,
            )
        return None
    
    def _query_historical(self, question: str) -> Optional[VerifiedFact]:
        """Query for historical dates."""
        for event, (date, desc) in HISTORICAL_DATES.items():
            if event in question or all(word in question for word in event.split()):
                return VerifiedFact(
                    fact=f"{desc} ({date}).",
                    category="history",
                    source="Encyclopedia Britannica",
                    source_url="https://www.britannica.com/",
                    confidence=1.0,
                )
        return None
    
    def _query_company(self, question: str) -> Optional[VerifiedFact]:
        """Query for company facts."""
        for company, facts in COMPANY_FACTS.items():
            if company in question:
                if "founded" in question or "when" in question or "created" in question:
                    return VerifiedFact(
                        fact=f"{company.title()} was founded in {facts['founded']}.",
                        category="business",
                        source="Company records",
                        source_url=f"https://en.wikipedia.org/wiki/{company.title()}",
                        confidence=1.0,
                    )
                if "founder" in question or "who" in question:
                    founders = ", ".join(facts.get("founders", ["Unknown"]))
                    return VerifiedFact(
                        fact=f"{company.title()} was founded by {founders}.",
                        category="business",
                        source="Company records",
                        source_url=f"https://en.wikipedia.org/wiki/{company.title()}",
                        confidence=1.0,
                    )
                if "headquarters" in question or "located" in question or "where" in question:
                    return VerifiedFact(
                        fact=f"{company.title()} is headquartered in {facts.get('headquarters', 'Unknown')}.",
                        category="business",
                        source="Company records",
                        source_url=f"https://en.wikipedia.org/wiki/{company.title()}",
                        confidence=1.0,
                    )
        return None
    
    def verify_statement(self, statement: str) -> Optional[tuple[bool, VerifiedFact]]:
        """
        Verify if a statement matches known facts.
        Returns (is_correct, fact) or None if can't verify.
        """
        statement_lower = statement.lower()
        
        # Check capitals
        for country, capital in COUNTRY_CAPITALS.items():
            if country in statement_lower and "capital" in statement_lower:
                is_correct = capital.lower() in statement_lower
                fact = VerifiedFact(
                    fact=f"The capital of {country.title()} is {capital}.",
                    category="geography",
                    source="CIA World Factbook",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=1.0,
                )
                return (is_correct, fact)
        
        return None
    
    def get_stats(self) -> Dict:
        return {
            "queries": self.queries,
            "hits": self.hits,
            "hit_rate": self.hits / max(1, self.queries),
        }


# Global instance
_knowledge_base: Optional[KnowledgeBase] = None

def get_knowledge_base() -> KnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    kb = KnowledgeBase()
    
    test_questions = [
        "What is the capital of France?",
        "What is the capital of Japan?",
        "When was Python created?",
        "Who founded Apple?",
        "What is the speed of light?",
        "What language do they speak in Brazil?",
        "What is the population of India?",
    ]
    
    print("=" * 60)
    print("KNOWLEDGE BASE TEST")
    print("=" * 60)
    
    for q in test_questions:
        print(f"\n❓ {q}")
        result = kb.query(q)
        if result:
            print(f"   ✓ {result.fact}")
            print(f"   📚 Source: {result.source}")
        else:
            print("   ✗ Not in knowledge base")
    
    print(f"\n📊 Stats: {kb.get_stats()}")
