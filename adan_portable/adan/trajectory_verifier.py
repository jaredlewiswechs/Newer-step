#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TRAJECTORY VERIFIER
The Newton gate for language.

Every sentence is a trajectory.
Every trajectory must stay inside Ω.
Verification IS the computation.
═══════════════════════════════════════════════════════════════════════════════

Typing becomes trajectory composition.
Each keystroke carries:
- Weight (how much it moves H₂)
- Curvature (how it bends the trajectory)
- Commit strength (how close to P₃)
- Envelope modification (how it reshapes Ω)

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import math
import re

from .kinematic_linguistics import (
    KinematicAnalyzer,
    Trajectory,
    TrajectoryPoint,
    KinematicSignature,
    SymbolType,
    get_kinematic_analyzer,
)


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC ENVELOPE
# The Ω of meaning - constraint geometry for semantics
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SemanticField:
    """A region in semantic space."""
    name: str
    keywords: List[str]
    compatible_fields: List[str] = field(default_factory=list)
    
    def contains(self, word: str) -> bool:
        return word.lower() in [k.lower() for k in self.keywords]


# Basic semantic fields
SEMANTIC_FIELDS = {
    "color": SemanticField("color", ["red", "blue", "green", "yellow", "black", "white", "colorless", "bright", "dark"]),
    "physical": SemanticField("physical", ["big", "small", "heavy", "light", "fast", "slow", "hard", "soft"]),
    "mental": SemanticField("mental", ["think", "idea", "thought", "dream", "imagine", "believe", "know"]),
    "motion": SemanticField("motion", ["run", "walk", "jump", "fly", "sleep", "sit", "stand", "move"]),
    "time": SemanticField("time", ["now", "then", "yesterday", "tomorrow", "always", "never", "when"]),
    "space": SemanticField("space", ["here", "there", "up", "down", "left", "right", "where"]),
}


@dataclass
class EnvelopeViolation:
    """A point where trajectory exits admissible space."""
    position: int
    word: str
    violation_type: str  # "syntactic", "semantic", "commitment"
    description: str
    severity: float  # 0-1


@dataclass
class TrajectoryVerification:
    """Complete verification result for a text trajectory."""
    text: str
    trajectory: Trajectory
    
    # Verification results
    syntactically_valid: bool
    semantically_coherent: bool
    properly_committed: bool
    
    violations: List[EnvelopeViolation]
    
    # Overall
    inside_omega: bool
    confidence: float
    explanation: str
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "verified": self.inside_omega,
            "confidence": round(self.confidence, 3),
            "syntactic": self.syntactically_valid,
            "semantic": self.semantically_coherent,
            "committed": self.properly_committed,
            "violations": [
                {
                    "position": v.position,
                    "word": v.word,
                    "type": v.violation_type,
                    "description": v.description,
                    "severity": v.severity,
                }
                for v in self.violations
            ],
            "explanation": self.explanation,
        }


class TrajectoryVerifier:
    """
    Verifies that language trajectories stay inside Ω.
    
    Two constraint surfaces:
    1. Grammar Ω - syntactic admissibility
    2. Meaning Ω - semantic coherence
    
    "Colorless green ideas sleep furiously"
    → Inside grammar Ω ✓
    → Outside meaning Ω ✗
    """
    
    def __init__(self):
        self.analyzer = get_kinematic_analyzer()
        self.semantic_fields = SEMANTIC_FIELDS
    
    def verify(self, text: str) -> TrajectoryVerification:
        """
        Verify a text trajectory against both grammar and semantic Ω.
        
        This is newton(trajectory, Ω) → bool
        """
        trajectory = self.analyzer.analyze(text)
        violations: List[EnvelopeViolation] = []
        
        # Check syntactic envelope
        syntactic_valid, syntactic_issues = self._check_syntax(text, trajectory)
        if not syntactic_valid:
            violations.append(EnvelopeViolation(
                position=len(text) - 1,
                word=text.split()[-1] if text.split() else "",
                violation_type="syntactic",
                description=syntactic_issues,
                severity=0.7,
            ))
        
        # Check semantic envelope
        semantic_coherent, semantic_violations = self._check_semantics(text)
        violations.extend(semantic_violations)
        
        # Check commitment
        properly_committed = trajectory.is_committed or trajectory.is_query
        if not properly_committed and len(text) > 10:
            violations.append(EnvelopeViolation(
                position=len(text) - 1,
                word=text[-1] if text else "",
                violation_type="commitment",
                description="Trajectory does not reach P₃ (no terminal punctuation)",
                severity=0.3,
            ))
        
        # Calculate confidence
        total_severity = sum(v.severity for v in violations)
        confidence = max(0, 1 - total_severity / 3)  # Normalize
        
        inside_omega = syntactic_valid and semantic_coherent and (
            properly_committed or len(text) <= 10
        )
        
        # Generate explanation
        if inside_omega:
            explanation = "Trajectory is inside Ω: grammatically valid and semantically coherent."
        else:
            parts = []
            if not syntactic_valid:
                parts.append("syntactically invalid")
            if not semantic_coherent:
                parts.append("semantically incoherent")
            if not properly_committed and len(text) > 10:
                parts.append("uncommitted")
            explanation = f"Trajectory exits Ω: {', '.join(parts)}."
        
        return TrajectoryVerification(
            text=text,
            trajectory=trajectory,
            syntactically_valid=syntactic_valid,
            semantically_coherent=semantic_coherent,
            properly_committed=properly_committed,
            violations=violations,
            inside_omega=inside_omega,
            confidence=confidence,
            explanation=explanation,
        )
    
    def _check_syntax(self, text: str, trajectory: Trajectory) -> Tuple[bool, str]:
        """Check if trajectory is inside grammar Ω."""
        return self.analyzer.verify_grammar(text)
    
    def _check_semantics(self, text: str) -> Tuple[bool, List[EnvelopeViolation]]:
        """
        Check if trajectory is inside meaning Ω.
        
        Detects semantic violations like:
        - "colorless green" (color contradiction)
        - "ideas sleep" (category mismatch)
        """
        violations: List[EnvelopeViolation] = []
        words = text.lower().split()
        
        # Check for semantic contradictions
        for i, word in enumerate(words):
            # Check adjacent words for semantic clashes
            if i > 0:
                prev_word = words[i - 1]
                clash = self._detect_semantic_clash(prev_word, word)
                if clash:
                    violations.append(EnvelopeViolation(
                        position=i,
                        word=f"{prev_word} {word}",
                        violation_type="semantic",
                        description=clash,
                        severity=0.5,
                    ))
        
        # Consider coherent if no major violations
        coherent = all(v.severity < 0.7 for v in violations) or len(violations) == 0
        
        return coherent, violations
    
    def _detect_semantic_clash(self, word1: str, word2: str) -> Optional[str]:
        """Detect if two adjacent words create semantic contradiction."""
        # Known contradictions
        contradictions = [
            (["colorless"], ["green", "red", "blue", "yellow", "colored"]),
            (["silent"], ["loud", "noisy", "screaming"]),
            (["empty"], ["full", "filled"]),
            (["dead"], ["living", "alive"]),
        ]
        
        for group1, group2 in contradictions:
            if word1 in group1 and word2 in group2:
                return f"Semantic contradiction: '{word1}' contradicts '{word2}'"
            if word2 in group1 and word1 in group2:
                return f"Semantic contradiction: '{word2}' contradicts '{word1}'"
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# TRAJECTORY COMPOSER
# Real-time composition of language as kinematic curves
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CompositionState:
    """Current state of trajectory composition."""
    text: str
    cursor_position: int
    
    # Kinematic state
    current_weight: float
    current_curvature: float
    current_commit: float
    envelope_depth: int
    
    # Predictions
    suggested_completions: List[str]
    needs_closure: bool
    approaching_commit: bool


class TrajectoryComposer:
    """
    Real-time trajectory composition assistant.
    
    Typing becomes trajectory composition:
    - Shows current kinematic state
    - Predicts trajectory needs
    - Warns when approaching Ω boundary
    """
    
    def __init__(self):
        self.analyzer = get_kinematic_analyzer()
        self.verifier = TrajectoryVerifier()
    
    def compose(self, text: str, cursor: int = -1) -> CompositionState:
        """
        Get composition state for current text.
        
        Useful for real-time feedback during typing.
        """
        if cursor < 0:
            cursor = len(text)
        
        trajectory = self.analyzer.analyze(text[:cursor])
        
        # Analyze what's needed
        needs_closure = trajectory.envelope_balance > 0
        approaching_commit = trajectory.total_weight > 5 and not trajectory.is_committed
        
        # Generate suggestions
        suggestions = []
        if needs_closure:
            # Suggest closing brackets
            closers = {1: ")", 2: "))", 3: ")))"}  # Simplified
            suggestions.append(closers.get(trajectory.envelope_balance, ")"))
        if approaching_commit:
            suggestions.extend([".", "?", "!"])
        
        return CompositionState(
            text=text,
            cursor_position=cursor,
            current_weight=trajectory.total_weight,
            current_curvature=trajectory.total_curvature,
            current_commit=trajectory.max_commit,
            envelope_depth=trajectory.envelope_balance,
            suggested_completions=suggestions,
            needs_closure=needs_closure,
            approaching_commit=approaching_commit,
        )
    
    def keystroke_analysis(self, char: str) -> Dict:
        """
        Analyze a single keystroke's kinematic contribution.
        
        Shows what each key "does" to the trajectory.
        """
        sig = self.analyzer.get_signature(char)
        
        if not sig:
            return {
                "char": char,
                "known": False,
                "effect": "Unknown - no kinematic signature"
            }
        
        return {
            "char": char,
            "known": True,
            "type": sig.symbol_type.value,
            "weight_contribution": sig.weight,
            "curvature_contribution": sig.curvature,
            "commit_contribution": sig.commit_strength,
            "is_anchor": sig.is_anchor,
            "is_terminus": sig.is_terminus,
            "is_handle": sig.is_handle,
            "opens_envelope": sig.opens_envelope,
            "closes_envelope": sig.closes_envelope,
            "description": sig.phonetic_desc,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCES
# ═══════════════════════════════════════════════════════════════════════════════

_verifier: Optional[TrajectoryVerifier] = None
_composer: Optional[TrajectoryComposer] = None

def get_trajectory_verifier() -> TrajectoryVerifier:
    global _verifier
    if _verifier is None:
        _verifier = TrajectoryVerifier()
    return _verifier

def get_trajectory_composer() -> TrajectoryComposer:
    global _composer
    if _composer is None:
        _composer = TrajectoryComposer()
    return _composer


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    verifier = TrajectoryVerifier()
    
    print("=" * 70)
    print("TRAJECTORY VERIFIER")
    print("newton(trajectory, Ω) → bool")
    print("=" * 70)
    
    test_cases = [
        "The capital of France is Paris.",
        "What is the speed of light?",
        "Colorless green ideas sleep furiously.",
        "The quick brown fox jumps over the lazy dog.",
        "Hello",
        "(unclosed parenthesis",
        "Silent loud noise.",
    ]
    
    for text in test_cases:
        print(f"\n📝 \"{text}\"")
        result = verifier.verify(text)
        
        status = "✓ INSIDE Ω" if result.inside_omega else "✗ OUTSIDE Ω"
        print(f"   {status} (confidence: {result.confidence:.2f})")
        print(f"   Syntactic: {result.syntactically_valid} | Semantic: {result.semantically_coherent} | Committed: {result.properly_committed}")
        
        if result.violations:
            print(f"   Violations:")
            for v in result.violations:
                print(f"      - [{v.violation_type}] {v.description}")
    
    print("\n" + "=" * 70)
    print("KEYSTROKE ANALYSIS")
    print("=" * 70)
    
    composer = TrajectoryComposer()
    for char in ['a', 't', '.', '?', ':', '(', ')']:
        analysis = composer.keystroke_analysis(char)
        print(f"   '{char}' → {analysis.get('description', 'unknown')}")
        if analysis.get('known'):
            print(f"       W:{analysis['weight_contribution']:.1f} C:{analysis['curvature_contribution']:.1f} K:{analysis['commit_contribution']:.1f}")
