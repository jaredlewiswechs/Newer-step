#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
KINEMATIC LINGUISTICS
Language IS a Bézier trajectory through meaning space.

The constraint IS the instruction.
The trajectory IS the sentence.
The envelope IS grammar.
═══════════════════════════════════════════════════════════════════════════════

Mapping:
    Subject     → P₀ (anchor, root)
    Verb        → The curve itself (motion, action)
    Object      → P₃ (terminus, commitment)
    Adjectives  → Handle adjustments (H₁, H₂)
    Syntax      → Ω (admissible region)
    
"Colorless green ideas sleep furiously"
    → Syntactically inside grammar Ω
    → Semantically outside meaning Ω
    → Two different constraint surfaces. Both geometric.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import math
import re


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC SIGNATURES
# Each symbol encodes: gesture, sound, meaning, operation
# ═══════════════════════════════════════════════════════════════════════════════

class SymbolType(Enum):
    """Types of symbols by their kinematic role."""
    VOWEL = "vowel"           # Open trajectories - the breath, the space
    CONSONANT = "consonant"   # Constraints on the breath
    DIGIT = "digit"           # Quantity as motion
    OPERATOR = "operator"     # Grammar of transformation
    COMMIT = "commit"         # P₃ markers
    QUERY = "query"           # Verification requests
    CONTAINER = "container"   # Local Ω definitions


@dataclass
class KinematicSignature:
    """The kinematic properties of a symbol."""
    symbol: str
    symbol_type: SymbolType
    
    # Bézier properties
    weight: float           # How much it moves H₂ (0-1)
    curvature: float        # How it bends the trajectory (-1 to 1)
    commit_strength: float  # How close to P₃ (0-1)
    
    # Trajectory role
    is_anchor: bool = False      # P₀
    is_terminus: bool = False    # P₃
    is_handle: bool = False      # H₁ or H₂
    
    # Semantic properties
    opens_envelope: bool = False   # Creates new Ω
    closes_envelope: bool = False  # Completes Ω
    
    # Phonetic motion
    phonetic_desc: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "type": self.symbol_type.value,
            "weight": self.weight,
            "curvature": self.curvature,
            "commit": self.commit_strength,
            "anchor": self.is_anchor,
            "terminus": self.is_terminus,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# THE KINEMATIC ALPHABET
# ═══════════════════════════════════════════════════════════════════════════════

SIGNATURES: Dict[str, KinematicSignature] = {
    # === VOWELS (Open trajectories - admissible space itself) ===
    'a': KinematicSignature('a', SymbolType.VOWEL, 0.7, 0.3, 0.5, 
                            is_anchor=True, phonetic_desc="Open mouth, front - origin"),
    'e': KinematicSignature('e', SymbolType.VOWEL, 0.5, 0.2, 0.4,
                            phonetic_desc="Mid-front, existence, presence"),
    'i': KinematicSignature('i', SymbolType.VOWEL, 0.3, 0.0, 0.8,
                            is_terminus=True, phonetic_desc="High front, self, identity - pure commitment"),
    'o': KinematicSignature('o', SymbolType.VOWEL, 0.8, 0.9, 0.6,
                            phonetic_desc="Back, rounded - full envelope, Ω as shape"),
    'u': KinematicSignature('u', SymbolType.VOWEL, 0.6, -0.4, 0.3,
                            phonetic_desc="Back, open - vessel, reception"),
    
    # === LABIALS (lips = P₀ anchor) ===
    'b': KinematicSignature('b', SymbolType.CONSONANT, 0.8, 0.5, 0.7,
                            is_anchor=True, phonetic_desc="Bilabial stop - bounded explosion"),
    'p': KinematicSignature('p', SymbolType.CONSONANT, 0.7, 0.4, 0.6,
                            is_anchor=True, phonetic_desc="Bilabial stop - thought-container"),
    'm': KinematicSignature('m', SymbolType.CONSONANT, 0.6, 0.3, 0.5,
                            phonetic_desc="Bilabial nasal - sustained closure"),
    'w': KinematicSignature('w', SymbolType.CONSONANT, 0.5, -0.5, 0.3,
                            phonetic_desc="Labio-velar glide - dual minima"),
    'f': KinematicSignature('f', SymbolType.CONSONANT, 0.4, 0.2, 0.2,
                            phonetic_desc="Labiodental - reaching without grounding"),
    'v': KinematicSignature('v', SymbolType.CONSONANT, 0.5, -0.3, 0.4,
                            phonetic_desc="Labiodental voiced - focus vector"),
    
    # === DENTALS/ALVEOLARS (tongue tip = H₁ handle) ===
    't': KinematicSignature('t', SymbolType.CONSONANT, 0.6, 0.0, 0.9,
                            is_handle=True, is_terminus=True,
                            phonetic_desc="Alveolar stop - decision gate (Newton gate!)"),
    'd': KinematicSignature('d', SymbolType.CONSONANT, 0.7, 0.4, 0.6,
                            phonetic_desc="Alveolar stop - bounded domain"),
    'n': KinematicSignature('n', SymbolType.CONSONANT, 0.5, 0.2, 0.5,
                            is_handle=True, phonetic_desc="Alveolar nasal - bridge trajectory"),
    'l': KinematicSignature('l', SymbolType.CONSONANT, 0.4, -0.2, 0.7,
                            phonetic_desc="Lateral - foundation, ground-finding"),
    'r': KinematicSignature('r', SymbolType.CONSONANT, 0.6, 0.3, 0.5,
                            phonetic_desc="Approximant - thought that walks"),
    's': KinematicSignature('s', SymbolType.CONSONANT, 0.5, 0.6, 0.4,
                            phonetic_desc="Fricative - sinusoidal flow"),
    'z': KinematicSignature('z', SymbolType.CONSONANT, 0.6, -0.6, 0.8,
                            is_terminus=True, phonetic_desc="Voiced fricative - terminal"),
    
    # === VELARS (back tongue = H₂ handle, leverage point) ===
    'k': KinematicSignature('k', SymbolType.CONSONANT, 0.8, 0.5, 0.6,
                            is_handle=True, phonetic_desc="Velar stop - branching"),
    'g': KinematicSignature('g', SymbolType.CONSONANT, 0.7, 0.6, 0.7,
                            phonetic_desc="Velar voiced - almost-closure with commitment"),
    'x': KinematicSignature('x', SymbolType.CONSONANT, 0.9, 0.0, 0.5,
                            phonetic_desc="Intersection, unknown, multiplication"),
    
    # === OTHER CONSONANTS ===
    'c': KinematicSignature('c', SymbolType.CONSONANT, 0.5, 0.4, 0.3,
                            phonetic_desc="Opening curvature - potential"),
    'h': KinematicSignature('h', SymbolType.CONSONANT, 0.3, 0.1, 0.2,
                            phonetic_desc="Breath-span - connection across gap"),
    'j': KinematicSignature('j', SymbolType.CONSONANT, 0.5, -0.3, 0.6,
                            phonetic_desc="Descent with hook - delay then return"),
    'q': KinematicSignature('q', SymbolType.CONSONANT, 0.8, 0.7, 0.5,
                            phonetic_desc="Completion with exception"),
    'y': KinematicSignature('y', SymbolType.CONSONANT, 0.4, -0.2, 0.7,
                            phonetic_desc="Convergence resolving to path"),
    
    # === DIGITS (Quantity as Motion) ===
    '0': KinematicSignature('0', SymbolType.DIGIT, 0.0, 1.0, 0.0,
                            opens_envelope=True, closes_envelope=True,
                            phonetic_desc="Empty Ω - container with no contents"),
    '1': KinematicSignature('1', SymbolType.DIGIT, 1.0, 0.0, 1.0,
                            is_anchor=True, is_terminus=True,
                            phonetic_desc="Unity - P₀ = P₃, handles collapsed"),
    '2': KinematicSignature('2', SymbolType.DIGIT, 0.6, 0.3, 0.7,
                            phonetic_desc="Pair - first non-trivial"),
    '3': KinematicSignature('3', SymbolType.DIGIT, 0.5, 0.5, 0.5,
                            phonetic_desc="Trinity - iterative opening"),
    '4': KinematicSignature('4', SymbolType.DIGIT, 0.8, 0.0, 0.8,
                            phonetic_desc="Stability - crossed constraints"),
    '5': KinematicSignature('5', SymbolType.DIGIT, 0.7, 0.4, 0.6,
                            phonetic_desc="Grasp - control then release"),
    '6': KinematicSignature('6', SymbolType.DIGIT, 0.6, 0.7, 0.4,
                            opens_envelope=True, phonetic_desc="Becoming - entering Ω"),
    '7': KinematicSignature('7', SymbolType.DIGIT, 0.5, -0.3, 0.7,
                            is_handle=True, phonetic_desc="Direction change - lever"),
    '8': KinematicSignature('8', SymbolType.DIGIT, 0.5, 1.0, 0.5,
                            phonetic_desc="Infinity - strange loop"),
    '9': KinematicSignature('9', SymbolType.DIGIT, 0.6, 0.7, 0.8,
                            closes_envelope=True, phonetic_desc="Release - exiting Ω"),
    
    # === OPERATORS (Grammar of Transformation) ===
    '.': KinematicSignature('.', SymbolType.COMMIT, 0.0, 0.0, 1.0,
                            is_terminus=True, closes_envelope=True,
                            phonetic_desc="P₃ COMMIT - terminus"),
    ',': KinematicSignature(',', SymbolType.OPERATOR, 0.2, 0.3, 0.3,
                            is_handle=True, phonetic_desc="Handle adjustment mid-trajectory"),
    ';': KinematicSignature(';', SymbolType.OPERATOR, 0.3, 0.3, 0.6,
                            phonetic_desc="Soft P₃ - allows continuation"),
    ':': KinematicSignature(':', SymbolType.OPERATOR, 0.5, 0.0, 0.5,
                            phonetic_desc="THE f/g RATIO - dimensional analysis"),
    '?': KinematicSignature('?', SymbolType.QUERY, 0.4, 0.5, 0.1,
                            phonetic_desc="VERIFICATION QUERY - is trajectory admissible?"),
    '!': KinematicSignature('!', SymbolType.COMMIT, 0.9, 0.0, 1.0,
                            is_terminus=True, phonetic_desc="Certainty - deep inside Ω"),
    '(': KinematicSignature('(', SymbolType.CONTAINER, 0.3, 0.5, 0.2,
                            opens_envelope=True, phonetic_desc="Open local Ω"),
    ')': KinematicSignature(')', SymbolType.CONTAINER, 0.3, 0.5, 0.8,
                            closes_envelope=True, phonetic_desc="Close local Ω"),
    '[': KinematicSignature('[', SymbolType.CONTAINER, 0.4, 0.2, 0.2,
                            opens_envelope=True, phonetic_desc="Indexed access to Ω"),
    ']': KinematicSignature(']', SymbolType.CONTAINER, 0.4, 0.2, 0.8,
                            closes_envelope=True, phonetic_desc="Close indexed Ω"),
    '{': KinematicSignature('{', SymbolType.CONTAINER, 0.5, 0.3, 0.1,
                            opens_envelope=True, phonetic_desc="Definition of Ω itself"),
    '}': KinematicSignature('}', SymbolType.CONTAINER, 0.5, 0.3, 0.9,
                            closes_envelope=True, phonetic_desc="Close Ω definition"),
    '+': KinematicSignature('+', SymbolType.OPERATOR, 0.7, 0.0, 0.5,
                            phonetic_desc="Handle superposition"),
    '-': KinematicSignature('-', SymbolType.OPERATOR, 0.3, 0.0, 0.5,
                            phonetic_desc="Handle retraction"),
    '*': KinematicSignature('*', SymbolType.OPERATOR, 0.8, 0.0, 0.5,
                            phonetic_desc="Handle scaling"),
    '/': KinematicSignature('/', SymbolType.OPERATOR, 0.5, -0.5, 0.5,
                            phonetic_desc="The f/g operation itself"),
    '=': KinematicSignature('=', SymbolType.OPERATOR, 0.5, 0.0, 0.8,
                            phonetic_desc="Constraint satisfaction"),
    '<': KinematicSignature('<', SymbolType.OPERATOR, 0.4, 0.3, 0.3,
                            phonetic_desc="Ordering on constraint boundary"),
    '>': KinematicSignature('>', SymbolType.OPERATOR, 0.4, -0.3, 0.7,
                            phonetic_desc="Ordering on constraint boundary"),
    '~': KinematicSignature('~', SymbolType.OPERATOR, 0.3, 0.8, 0.5,
                            phonetic_desc="Fuzzy ∂Ω - soft boundary"),
    '@': KinematicSignature('@', SymbolType.OPERATOR, 0.6, 0.9, 0.7,
                            phonetic_desc="Trajectory to specific point in Ω"),
    '#': KinematicSignature('#', SymbolType.OPERATOR, 0.7, 0.0, 0.5,
                            phonetic_desc="Grid over Ω - discretization"),
    '&': KinematicSignature('&', SymbolType.OPERATOR, 0.6, 0.7, 0.6,
                            phonetic_desc="Trajectory that references itself"),
    '|': KinematicSignature('|', SymbolType.OPERATOR, 0.8, 0.0, 0.5,
                            phonetic_desc="Alternation - boundary"),
    '^': KinematicSignature('^', SymbolType.OPERATOR, 0.7, 0.5, 0.7,
                            phonetic_desc="Curvature maximum"),
    '_': KinematicSignature('_', SymbolType.OPERATOR, 0.2, 0.0, 0.3,
                            phonetic_desc="Baseline of coordinate system"),
    ' ': KinematicSignature(' ', SymbolType.OPERATOR, 0.0, 0.0, 0.0,
                            phonetic_desc="Breath - space between trajectories"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# TRAJECTORY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TrajectoryPoint:
    """A point on the language trajectory."""
    position: int
    char: str
    signature: Optional[KinematicSignature]
    cumulative_weight: float
    cumulative_curvature: float
    commit_level: float
    envelope_depth: int  # How many Ω's deep


@dataclass
class Trajectory:
    """A complete language trajectory (word, sentence, etc.)."""
    text: str
    points: List[TrajectoryPoint]
    
    # Aggregate properties
    total_weight: float = 0.0
    total_curvature: float = 0.0
    max_commit: float = 0.0
    envelope_balance: int = 0  # Should be 0 if all Ω's closed
    
    # Trajectory classification
    is_committed: bool = False      # Ends with P₃
    is_query: bool = False          # Ends with ?
    is_balanced: bool = False       # All envelopes closed
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "length": len(self.text),
            "total_weight": round(self.total_weight, 3),
            "total_curvature": round(self.total_curvature, 3),
            "max_commit": round(self.max_commit, 3),
            "envelope_balance": self.envelope_balance,
            "is_committed": self.is_committed,
            "is_query": self.is_query,
            "is_balanced": self.is_balanced,
        }


class KinematicAnalyzer:
    """
    Analyzes text as kinematic trajectories through constraint space.
    
    Language is Bézier curves. This engine computes the trajectory.
    """
    
    def __init__(self):
        self.signatures = SIGNATURES
    
    def get_signature(self, char: str) -> Optional[KinematicSignature]:
        """Get kinematic signature for a character."""
        return self.signatures.get(char.lower())
    
    def analyze(self, text: str) -> Trajectory:
        """
        Analyze text as a kinematic trajectory.
        
        Returns trajectory with:
        - Point-by-point kinematic properties
        - Aggregate trajectory metrics
        - Envelope balance (grammar check)
        - Commitment status
        """
        points: List[TrajectoryPoint] = []
        
        cumulative_weight = 0.0
        cumulative_curvature = 0.0
        envelope_depth = 0
        max_commit = 0.0
        
        for i, char in enumerate(text):
            sig = self.get_signature(char)
            
            if sig:
                cumulative_weight += sig.weight
                cumulative_curvature += sig.curvature
                max_commit = max(max_commit, sig.commit_strength)
                
                if sig.opens_envelope:
                    envelope_depth += 1
                if sig.closes_envelope:
                    envelope_depth = max(0, envelope_depth - 1)
            
            points.append(TrajectoryPoint(
                position=i,
                char=char,
                signature=sig,
                cumulative_weight=cumulative_weight,
                cumulative_curvature=cumulative_curvature,
                commit_level=sig.commit_strength if sig else 0.0,
                envelope_depth=envelope_depth,
            ))
        
        # Determine trajectory properties
        last_sig = self.get_signature(text[-1]) if text else None
        
        trajectory = Trajectory(
            text=text,
            points=points,
            total_weight=cumulative_weight,
            total_curvature=cumulative_curvature,
            max_commit=max_commit,
            envelope_balance=envelope_depth,
            is_committed=(last_sig and last_sig.is_terminus) if last_sig else False,
            is_query=(last_sig and last_sig.symbol_type == SymbolType.QUERY) if last_sig else False,
            is_balanced=(envelope_depth == 0),
        )
        
        return trajectory
    
    def analyze_sentence(self, sentence: str) -> Dict:
        """
        Analyze a sentence with grammatical interpretation.
        
        Returns:
        - Trajectory metrics
        - Grammatical status (inside/outside Ω)
        - Semantic indicators
        """
        trajectory = self.analyze(sentence)
        
        # Grammatical analysis
        words = sentence.split()
        word_trajectories = [self.analyze(word) for word in words]
        
        # Find P₀ (subject), verb (curve), P₃ (object)
        # Simplified: first noun-like word = P₀, verb = curve, last = P₃
        
        return {
            "sentence": sentence,
            "trajectory": trajectory.to_dict(),
            "word_count": len(words),
            "words": [w.to_dict() for w in word_trajectories],
            "grammar_check": {
                "is_committed": trajectory.is_committed,
                "is_balanced": trajectory.is_balanced,
                "is_query": trajectory.is_query,
                "envelope_status": "closed" if trajectory.is_balanced else f"open ({trajectory.envelope_balance} deep)",
            },
            "kinematic_summary": {
                "average_weight": trajectory.total_weight / max(1, len(sentence)),
                "average_curvature": trajectory.total_curvature / max(1, len(sentence)),
                "commitment_profile": "strong" if trajectory.max_commit > 0.7 else "moderate" if trajectory.max_commit > 0.4 else "weak",
            }
        }
    
    def compare_trajectories(self, text1: str, text2: str) -> Dict:
        """Compare kinematic properties of two texts."""
        t1 = self.analyze(text1)
        t2 = self.analyze(text2)
        
        return {
            "text1": text1,
            "text2": text2,
            "weight_diff": abs(t1.total_weight - t2.total_weight),
            "curvature_diff": abs(t1.total_curvature - t2.total_curvature),
            "commit_diff": abs(t1.max_commit - t2.max_commit),
            "same_envelope_status": t1.is_balanced == t2.is_balanced,
            "same_termination": t1.is_committed == t2.is_committed,
        }
    
    def verify_grammar(self, sentence: str) -> Tuple[bool, str]:
        """
        Verify if sentence is grammatically admissible (inside grammar Ω).
        
        This is the Newton verifier for language.
        """
        trajectory = self.analyze(sentence)
        
        issues = []
        
        # Check envelope balance (all brackets/parentheses closed)
        if not trajectory.is_balanced:
            issues.append(f"Unclosed envelope (depth: {trajectory.envelope_balance})")
        
        # Check commitment (sentence should end with P₃ or ?)
        if not trajectory.is_committed and not trajectory.is_query:
            issues.append("No terminal commitment (missing . or ?)")
        
        # Check for content (not just whitespace)
        if trajectory.total_weight < 0.5:
            issues.append("Insufficient content weight")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Trajectory is inside grammar Ω"


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_analyzer: Optional[KinematicAnalyzer] = None

def get_kinematic_analyzer() -> KinematicAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = KinematicAnalyzer()
    return _analyzer


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    analyzer = KinematicAnalyzer()
    
    print("=" * 70)
    print("KINEMATIC LINGUISTICS")
    print("Language IS a Bézier trajectory through meaning space.")
    print("=" * 70)
    
    test_sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "What is the capital of France?",
        "Colorless green ideas sleep furiously.",
        "Hello world",
        "1 + 1 = 2",
        "f(x) = x² + 2x + 1",
        "(unclosed parenthesis",
    ]
    
    for sentence in test_sentences:
        print(f"\n📝 \"{sentence}\"")
        
        valid, reason = analyzer.verify_grammar(sentence)
        status = "✓ INSIDE Ω" if valid else "✗ OUTSIDE Ω"
        print(f"   {status}: {reason}")
        
        result = analyzer.analyze_sentence(sentence)
        t = result["trajectory"]
        print(f"   Weight: {t['total_weight']:.2f} | Curvature: {t['total_curvature']:.2f} | Commit: {t['max_commit']:.2f}")
        print(f"   Committed: {t['is_committed']} | Query: {t['is_query']} | Balanced: {t['is_balanced']}")
    
    print("\n" + "=" * 70)
    print("THE SACRED SYMBOLS")
    print("=" * 70)
    
    sacred = [':', '.', '?', '!', '=']
    for s in sacred:
        sig = analyzer.get_signature(s)
        if sig:
            print(f"   '{s}' → {sig.phonetic_desc}")
            print(f"       Weight: {sig.weight} | Curvature: {sig.curvature} | Commit: {sig.commit_strength}")
