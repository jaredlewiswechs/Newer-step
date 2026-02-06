#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ADA - THE SECRET SENTINEL
Continuous Awareness • Drift Detection • Intuitive Sensing

Like a dog sensing something's wrong before thinking "analyze threat level."
Ada watches. Ada senses. Ada whispers to Newton when something smells off.

Named for Ada Lovelace - the first to see that computation is not just calculation.

The constraint IS the instruction.
The sentinel IS the immune system.
The whisper IS the early warning.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import math
import re
import time


# ═══════════════════════════════════════════════════════════════════════════════
# SENTINEL TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class AlertLevel(Enum):
    """How loud Ada's whisper is."""
    QUIET = "quiet"           # Baseline normal
    NOTICE = "notice"         # Mild anomaly detected
    ALERT = "alert"           # Something's off
    ALARM = "alarm"           # Hackles up, ears forward
    CRITICAL = "critical"     # Full defensive posture


class DriftType(Enum):
    """Types of drift Ada can detect."""
    SEMANTIC = "semantic"       # Meaning shifted
    FACTUAL = "factual"         # Facts changed
    TEMPORAL = "temporal"       # Time-based inconsistency
    STATISTICAL = "statistical" # Pattern anomaly
    BEHAVIORAL = "behavioral"   # Usage pattern changed
    SOURCE = "source"           # Source reliability shifted


@dataclass
class Anomaly:
    """A detected anomaly - something that smells off."""
    drift_type: DriftType
    description: str
    confidence: float         # 0-1, how confident Ada is
    timestamp: datetime
    evidence: Dict[str, Any]
    baseline_hash: str        # What was expected
    observed_hash: str        # What was seen
    
    def to_dict(self) -> Dict:
        return {
            "type": self.drift_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "evidence": self.evidence,
            "baseline_hash": self.baseline_hash[:12],
            "observed_hash": self.observed_hash[:12],
            "is_drift": self.baseline_hash != self.observed_hash,
        }


@dataclass
class Whisper:
    """Ada's communication to Newton - a whisper, not a shout."""
    level: AlertLevel
    message: str
    anomalies: List[Anomaly]
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "message": self.message,
            "anomaly_count": len(self.anomalies),
            "anomalies": [a.to_dict() for a in self.anomalies],
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Baseline:
    """A verified baseline for comparison."""
    key: str
    value_hash: str
    value: Any
    source: str
    verified_at: datetime
    verification_count: int = 1
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value_hash": self.value_hash[:12],
            "source": self.source,
            "verified_at": self.verified_at.isoformat(),
            "verification_count": self.verification_count,
            "confidence": self.confidence,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SENSING PATTERNS
# Heuristics that don't require full verification - fast pattern detection
# ═══════════════════════════════════════════════════════════════════════════════

class SensePattern:
    """A quick heuristic check - the dog's nose, not the lab test."""
    
    # Patterns that smell like contradiction
    CONTRADICTION_MARKERS = [
        (r"always.*never", "absolute_contradiction"),
        (r"impossible.*definitely", "certainty_conflict"),
        (r"no one.*everyone", "universal_contradiction"),
        (r"none.*all", "total_contradiction"),
    ]
    
    # Patterns that smell like uncertainty disguised as certainty
    FALSE_CERTAINTY_MARKERS = [
        (r"(definitely|certainly|absolutely).*(maybe|possibly|might)", "confidence_mismatch"),
        (r"(100%|guaranteed).*(but|however|although)", "certainty_hedging"),
        (r"(fact|proven).*(believe|think|seem)", "fact_opinion_blend"),
    ]
    
    # Patterns of EXCESSIVE certainty (red flag - nothing is 100% in unverified content)
    EXCESSIVE_CERTAINTY_MARKERS = [
        (r"100%\s*(certain|sure|confident|guaranteed)", "excessive_certainty"),
        (r"(absolutely|definitely|certainly)\s+(true|correct|right|certain)", "overconfidence"),
        (r"(always|never).*(always|never)", "absolute_stacking"),
        (r"\b(undoubtedly|unquestionably|indisputably)\b", "excessive_confidence"),
        (r"(every|all|none|no one).*(always|never|ever)", "universal_absolute"),
    ]
    
    # Patterns that smell like temporal issues
    TEMPORAL_MARKERS = [
        (r"will.*was", "tense_inconsistency"),
        (r"yesterday.*tomorrow", "time_confusion"),
        (r"before.*after.*before", "sequence_loop"),
    ]
    
    # Patterns that smell like source issues
    SOURCE_MARKERS = [
        (r"(according to|based on).*(probably|maybe)", "source_uncertainty"),
        (r"(research shows|studies prove).*(i think|in my opinion)", "research_opinion_blend"),
    ]
    
    @classmethod
    def quick_scan(cls, text: str) -> List[Tuple[str, str, float]]:
        """
        Quick heuristic scan - returns (pattern_type, match, confidence).
        This is the sniff test, not the full analysis.
        """
        text_lower = text.lower()
        detections = []
        
        all_patterns = (
            cls.CONTRADICTION_MARKERS +
            cls.FALSE_CERTAINTY_MARKERS +
            cls.EXCESSIVE_CERTAINTY_MARKERS +
            cls.TEMPORAL_MARKERS +
            cls.SOURCE_MARKERS
        )
        
        for pattern, pattern_type in all_patterns:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                confidence = 0.7  # Heuristics are never 100%
                detections.append((pattern_type, match.group(0), confidence))
        
        return detections


# ═══════════════════════════════════════════════════════════════════════════════
# DRIFT DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class DriftDetector:
    """
    Detects drift from established baselines.
    
    Like the immune system - doesn't check everything constantly,
    watches for CHANGES from what's known.
    """
    
    def __init__(self):
        self.baselines: Dict[str, Baseline] = {}
        self.history: List[Anomaly] = []
        self.max_history = 1000
    
    def _hash_value(self, value: Any) -> str:
        """Create deterministic hash of any value."""
        if isinstance(value, dict):
            # Sort keys for determinism
            normalized = str(sorted(value.items()))
        elif isinstance(value, (list, set)):
            normalized = str(sorted(str(v) for v in value))
        else:
            normalized = str(value)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def set_baseline(
        self,
        key: str,
        value: Any,
        source: str,
        confidence: float = 1.0
    ) -> Baseline:
        """Establish or update a baseline."""
        value_hash = self._hash_value(value)
        
        if key in self.baselines:
            existing = self.baselines[key]
            if existing.value_hash == value_hash:
                # Same value - increase confidence
                existing.verification_count += 1
                existing.confidence = min(1.0, existing.confidence + 0.01)
                existing.verified_at = datetime.now()
                return existing
        
        baseline = Baseline(
            key=key,
            value_hash=value_hash,
            value=value,
            source=source,
            verified_at=datetime.now(),
            confidence=confidence,
        )
        self.baselines[key] = baseline
        return baseline
    
    def check_drift(
        self,
        key: str,
        observed_value: Any,
        source: str = "observation"
    ) -> Optional[Anomaly]:
        """
        Check if observed value has drifted from baseline.
        Returns Anomaly if drift detected, None if stable.
        """
        if key not in self.baselines:
            # No baseline - can't detect drift, but establish one
            self.set_baseline(key, observed_value, source, confidence=0.5)
            return None
        
        baseline = self.baselines[key]
        observed_hash = self._hash_value(observed_value)
        
        if baseline.value_hash == observed_hash:
            # No drift - strengthen baseline
            baseline.verification_count += 1
            baseline.verified_at = datetime.now()
            return None
        
        # DRIFT DETECTED
        anomaly = Anomaly(
            drift_type=DriftType.FACTUAL,
            description=f"Value for '{key}' has drifted from baseline",
            confidence=baseline.confidence,
            timestamp=datetime.now(),
            evidence={
                "key": key,
                "baseline_value": baseline.value,
                "observed_value": observed_value,
                "baseline_source": baseline.source,
                "observation_source": source,
                "times_verified": baseline.verification_count,
            },
            baseline_hash=baseline.value_hash,
            observed_hash=observed_hash,
        )
        
        self._record_anomaly(anomaly)
        return anomaly
    
    def _record_anomaly(self, anomaly: Anomaly):
        """Record anomaly in history."""
        self.history.append(anomaly)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_drift_rate(self, window_hours: int = 24) -> float:
        """Calculate drift rate over time window."""
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent = [a for a in self.history if a.timestamp > cutoff]
        total_checks = len(self.baselines) or 1
        return len(recent) / total_checks


# ═══════════════════════════════════════════════════════════════════════════════
# ADA - THE SENTINEL
# ═══════════════════════════════════════════════════════════════════════════════

class Ada:
    """
    Ada - The Secret Sentinel.
    
    Always watching. Not query-response, but continuous awareness.
    - Monitoring drift in sources
    - Pre-warming verifications for likely questions
    - Building confidence scores over time
    - Whispering to Newton when something smells off
    
    Like a dog sensing - hackles up, ears forward.
    Not "analyze threat level" but SENSE it.
    """
    
    def __init__(self):
        self.drift_detector = DriftDetector()
        self.whispers: List[Whisper] = []
        self.observations: int = 0
        self.alerts_raised: int = 0
        self._startup_time = datetime.now()
        
        # Callback for when Ada wants to whisper to Newton
        self._whisper_callback: Optional[Callable[[Whisper], None]] = None
        
        # Pattern sensing
        self._recent_patterns: List[Tuple[str, datetime]] = []
        self._pattern_window = timedelta(minutes=5)
    
    def set_whisper_callback(self, callback: Callable[[Whisper], None]):
        """Set callback for when Ada whispers."""
        self._whisper_callback = callback
    
    def sense(self, text: str, context: Optional[Dict] = None) -> Optional[Whisper]:
        """
        Quick intuitive sensing - the sniff test.
        
        This is FAST. Not deep verification, but pattern detection.
        Like a dog's nose, not a lab analysis.
        """
        self.observations += 1
        context = context or {}
        
        # Quick pattern scan
        detections = SensePattern.quick_scan(text)
        
        if not detections:
            return None
        
        # Something smells off
        anomalies = []
        for pattern_type, match, confidence in detections:
            anomaly = Anomaly(
                drift_type=DriftType.SEMANTIC,
                description=f"Pattern '{pattern_type}' detected: '{match}'",
                confidence=confidence,
                timestamp=datetime.now(),
                evidence={"pattern": pattern_type, "match": match, "text": text[:200]},
                baseline_hash=hashlib.sha256(b"expected_coherent").hexdigest(),
                observed_hash=hashlib.sha256(text.encode()).hexdigest(),
            )
            anomalies.append(anomaly)
        
        # Determine alert level based on anomaly count and confidence
        avg_confidence = sum(a.confidence for a in anomalies) / len(anomalies)
        
        if len(anomalies) >= 3 or avg_confidence > 0.9:
            level = AlertLevel.ALARM
        elif len(anomalies) >= 2 or avg_confidence > 0.7:
            level = AlertLevel.ALERT
        else:
            level = AlertLevel.NOTICE
        
        whisper = Whisper(
            level=level,
            message=f"Detected {len(anomalies)} potential issue(s) in text",
            anomalies=anomalies,
            recommendation=self._generate_recommendation(anomalies),
        )
        
        self._record_whisper(whisper)
        return whisper
    
    def observe(
        self,
        key: str,
        value: Any,
        source: str,
        is_verification: bool = False
    ) -> Optional[Whisper]:
        """
        Observe a fact and check for drift.
        
        If is_verification=True, this strengthens the baseline.
        Otherwise, it checks against baseline and may raise drift alert.
        """
        self.observations += 1
        
        if is_verification:
            # Strengthen baseline
            self.drift_detector.set_baseline(key, value, source)
            return None
        
        # Check for drift
        anomaly = self.drift_detector.check_drift(key, value, source)
        
        if anomaly:
            whisper = Whisper(
                level=AlertLevel.ALERT,
                message=f"Drift detected for '{key}'",
                anomalies=[anomaly],
                recommendation="Verify against authoritative source before trusting",
            )
            self._record_whisper(whisper)
            return whisper
        
        return None
    
    def watch_response(
        self,
        query: str,
        response: str,
        verified: bool,
        sources: List[str] = None
    ) -> Optional[Whisper]:
        """
        Watch a query-response pair for issues.
        
        Ada doesn't just check facts - she watches for:
        - Inconsistency with previous responses
        - Overconfidence in unverified claims
        - Source reliability patterns
        """
        sources = sources or []
        anomalies = []
        
        # 1. Sense the response text
        sense_result = self.sense(response)
        if sense_result:
            anomalies.extend(sense_result.anomalies)
        
        # 2. Check if unverified response claims certainty
        if not verified:
            certainty_patterns = [
                r'\b(definitely|certainly|absolutely|always|never|guaranteed)\b',
                r'\b(100%|fact|proven|undoubtedly)\b',
            ]
            for pattern in certainty_patterns:
                if re.search(pattern, response.lower()):
                    anomaly = Anomaly(
                        drift_type=DriftType.BEHAVIORAL,
                        description="Unverified response expresses high certainty",
                        confidence=0.8,
                        timestamp=datetime.now(),
                        evidence={
                            "query": query,
                            "response": response[:200],
                            "verified": verified,
                        },
                        baseline_hash=hashlib.sha256(b"verified_certainty").hexdigest(),
                        observed_hash=hashlib.sha256(response.encode()).hexdigest(),
                    )
                    anomalies.append(anomaly)
                    break
        
        # 3. Check response length vs verification status
        if len(response) > 500 and not verified and not sources:
            anomaly = Anomaly(
                drift_type=DriftType.BEHAVIORAL,
                description="Long unverified response without sources",
                confidence=0.6,
                timestamp=datetime.now(),
                evidence={
                    "response_length": len(response),
                    "verified": verified,
                    "source_count": len(sources),
                },
                baseline_hash=hashlib.sha256(b"sourced_response").hexdigest(),
                observed_hash=hashlib.sha256(str(len(sources)).encode()).hexdigest(),
            )
            anomalies.append(anomaly)
        
        if not anomalies:
            return None
        
        # Determine overall alert level
        max_confidence = max(a.confidence for a in anomalies)
        if max_confidence > 0.8 or len(anomalies) >= 3:
            level = AlertLevel.ALERT
        else:
            level = AlertLevel.NOTICE
        
        whisper = Whisper(
            level=level,
            message=f"Potential issues with response to: {query[:50]}...",
            anomalies=anomalies,
            recommendation=self._generate_recommendation(anomalies),
        )
        
        self._record_whisper(whisper)
        return whisper
    
    def _generate_recommendation(self, anomalies: List[Anomaly]) -> str:
        """Generate actionable recommendation based on anomalies."""
        types = set(a.drift_type for a in anomalies)
        
        recommendations = []
        
        if DriftType.FACTUAL in types:
            recommendations.append("Cross-reference with authoritative source")
        if DriftType.SEMANTIC in types:
            recommendations.append("Review for logical consistency")
        if DriftType.BEHAVIORAL in types:
            recommendations.append("Consider reducing certainty level")
        if DriftType.TEMPORAL in types:
            recommendations.append("Verify temporal accuracy")
        if DriftType.SOURCE in types:
            recommendations.append("Verify source reliability")
        
        return "; ".join(recommendations) if recommendations else "Review manually"
    
    def _record_whisper(self, whisper: Whisper):
        """Record whisper and potentially notify Newton."""
        self.whispers.append(whisper)
        self.alerts_raised += 1
        
        # Keep whisper history bounded
        if len(self.whispers) > 1000:
            self.whispers = self.whispers[-1000:]
        
        # Notify Newton if callback set
        if self._whisper_callback and whisper.level.value in ("alert", "alarm", "critical"):
            self._whisper_callback(whisper)
    
    def get_status(self) -> Dict:
        """Get Ada's current status."""
        uptime = datetime.now() - self._startup_time
        recent_whispers = [w for w in self.whispers 
                         if w.timestamp > datetime.now() - timedelta(hours=1)]
        
        return {
            "status": "watching",
            "uptime_seconds": uptime.total_seconds(),
            "observations": self.observations,
            "alerts_raised": self.alerts_raised,
            "baselines_tracked": len(self.drift_detector.baselines),
            "recent_whispers": len(recent_whispers),
            "drift_rate_24h": self.drift_detector.get_drift_rate(24),
            "alert_level": self._current_alert_level().value,
        }
    
    def _current_alert_level(self) -> AlertLevel:
        """Determine current overall alert level."""
        recent = [w for w in self.whispers 
                 if w.timestamp > datetime.now() - timedelta(minutes=15)]
        
        if not recent:
            return AlertLevel.QUIET
        
        levels = [w.level for w in recent]
        
        if AlertLevel.CRITICAL in levels:
            return AlertLevel.CRITICAL
        if AlertLevel.ALARM in levels:
            return AlertLevel.ALARM
        if AlertLevel.ALERT in levels:
            return AlertLevel.ALERT
        if AlertLevel.NOTICE in levels:
            return AlertLevel.NOTICE
        
        return AlertLevel.QUIET
    
    def get_whispers(self, since_hours: int = 1) -> List[Dict]:
        """Get recent whispers."""
        cutoff = datetime.now() - timedelta(hours=since_hours)
        return [w.to_dict() for w in self.whispers if w.timestamp > cutoff]


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_ada: Optional[Ada] = None

def get_ada() -> Ada:
    """Get the global Ada instance."""
    global _ada
    if _ada is None:
        _ada = Ada()
    return _ada


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ada = Ada()
    
    print("═" * 70)
    print("ADA - THE SECRET SENTINEL")
    print("Watching. Sensing. Whispering.")
    print("═" * 70)
    
    # Test baseline drift detection
    print("\n📊 DRIFT DETECTION TEST")
    print("-" * 40)
    
    # Establish baseline
    ada.observe("capital_france", "Paris", "CIA Factbook", is_verification=True)
    print("✓ Baseline established: capital_france = Paris")
    
    # Check consistent value
    result = ada.observe("capital_france", "Paris", "user_claim")
    print(f"  Check 'Paris': {'No drift' if not result else result.message}")
    
    # Check drifted value
    result = ada.observe("capital_france", "Lyon", "user_claim")
    if result:
        print(f"  Check 'Lyon': ⚠ {result.message}")
        print(f"    Level: {result.level.value}")
        print(f"    Anomalies: {len(result.anomalies)}")
    
    # Test pattern sensing
    print("\n🔍 PATTERN SENSING TEST")
    print("-" * 40)
    
    test_texts = [
        "The answer is definitely maybe correct.",
        "This is always never the case.",
        "100% guaranteed, but I'm not sure.",
        "Paris is the capital of France.",  # Clean
        "The fact is that I believe this might be true.",
    ]
    
    for text in test_texts:
        result = ada.sense(text)
        if result:
            print(f"⚠ '{text[:50]}...'")
            print(f"   Level: {result.level.value}")
            for a in result.anomalies:
                print(f"   → {a.description}")
        else:
            print(f"✓ '{text[:50]}...' - Clean")
    
    # Test response watching
    print("\n👁 RESPONSE WATCHING TEST")
    print("-" * 40)
    
    result = ada.watch_response(
        query="What is 2+2?",
        response="The answer is definitely 4, this is absolutely proven fact.",
        verified=False,
        sources=[]
    )
    if result:
        print(f"⚠ Unverified confident response detected")
        print(f"   Level: {result.level.value}")
        print(f"   Recommendation: {result.recommendation}")
    
    # Status
    print("\n📈 ADA STATUS")
    print("-" * 40)
    status = ada.get_status()
    for k, v in status.items():
        print(f"   {k}: {v}")
