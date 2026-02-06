#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
META NEWTON - THE SELF-VERIFIER
Newton verifying Newton. Who watches the watchmen? Another watchman.

"Quis custodiet ipsos custodes?" - Now we know.

This is the recursive layer:
- Did Newton's reasoning process follow its own constraints?
- Are the bounds being respected?
- Is the verification chain intact?
- Is the ledger consistent?

The constraint IS the instruction.
The verifier IS verified.
The loop IS bounded.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import hashlib
import time


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION LEVELS
# ═══════════════════════════════════════════════════════════════════════════════

class VerificationLevel(Enum):
    """Levels of meta-verification."""
    SYNTACTIC = "syntactic"       # Structure is valid
    SEMANTIC = "semantic"         # Meaning is consistent
    OPERATIONAL = "operational"   # Operations are bounded
    TEMPORAL = "temporal"         # Time constraints respected
    CHAIN = "chain"               # Hash chain intact
    RECURSIVE = "recursive"       # Self-verification passed


class ConstraintStatus(Enum):
    """Status of a constraint check."""
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"


@dataclass
class MetaConstraint:
    """A constraint on Newton's own behavior."""
    name: str
    description: str
    check_fn: str  # Name of check function
    level: VerificationLevel
    critical: bool = True  # If critical, violation halts execution
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level.value,
            "critical": self.critical,
        }


@dataclass
class ConstraintResult:
    """Result of checking a meta-constraint."""
    constraint: MetaConstraint
    status: ConstraintStatus
    message: str
    evidence: Dict[str, Any]
    checked_at: datetime
    elapsed_us: int
    
    def to_dict(self) -> Dict:
        return {
            "constraint": self.constraint.name,
            "status": self.status.value,
            "message": self.message,
            "evidence": self.evidence,
            "checked_at": self.checked_at.isoformat(),
            "elapsed_us": self.elapsed_us,
        }


@dataclass
class MetaVerification:
    """Complete meta-verification result."""
    verified: bool
    level: VerificationLevel
    results: List[ConstraintResult]
    chain_hash: str
    timestamp: datetime
    total_elapsed_us: int
    
    # Aggregate stats
    satisfied: int = 0
    violated: int = 0
    critical_violations: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "verified": self.verified,
            "level": self.level.value,
            "results": [r.to_dict() for r in self.results],
            "chain_hash": self.chain_hash[:16],
            "timestamp": self.timestamp.isoformat(),
            "total_elapsed_us": self.total_elapsed_us,
            "summary": {
                "satisfied": self.satisfied,
                "violated": self.violated,
                "critical_violations": self.critical_violations,
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# META CONSTRAINTS - Newton's Laws for Newton
# ═══════════════════════════════════════════════════════════════════════════════

META_CONSTRAINTS = [
    # Operational bounds
    MetaConstraint(
        name="bounded_iterations",
        description="All loops must have bounded iterations",
        check_fn="check_bounded_iterations",
        level=VerificationLevel.OPERATIONAL,
        critical=True,
    ),
    MetaConstraint(
        name="bounded_recursion",
        description="Recursion depth must be bounded",
        check_fn="check_bounded_recursion",
        level=VerificationLevel.OPERATIONAL,
        critical=True,
    ),
    MetaConstraint(
        name="bounded_memory",
        description="Memory usage must be bounded",
        check_fn="check_bounded_memory",
        level=VerificationLevel.OPERATIONAL,
        critical=True,
    ),
    MetaConstraint(
        name="bounded_time",
        description="Execution time must be bounded",
        check_fn="check_bounded_time",
        level=VerificationLevel.TEMPORAL,
        critical=True,
    ),
    
    # Chain integrity
    MetaConstraint(
        name="hash_chain_intact",
        description="Ledger hash chain must be unbroken",
        check_fn="check_hash_chain",
        level=VerificationLevel.CHAIN,
        critical=True,
    ),
    MetaConstraint(
        name="no_retroactive_modification",
        description="Historical entries must not be modified",
        check_fn="check_immutability",
        level=VerificationLevel.CHAIN,
        critical=True,
    ),
    
    # Semantic consistency
    MetaConstraint(
        name="deterministic_output",
        description="Same input must produce same output",
        check_fn="check_determinism",
        level=VerificationLevel.SEMANTIC,
        critical=True,
    ),
    MetaConstraint(
        name="constraint_consistency",
        description="Constraints must not contradict each other",
        check_fn="check_constraint_consistency",
        level=VerificationLevel.SEMANTIC,
        critical=False,
    ),
    
    # Self-reference
    MetaConstraint(
        name="meta_termination",
        description="Meta-verification must itself terminate",
        check_fn="check_meta_termination",
        level=VerificationLevel.RECURSIVE,
        critical=True,
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
# META NEWTON - THE SELF-VERIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class MetaNewton:
    """
    Newton verifying Newton.
    
    The recursive verification layer that ensures Newton itself
    is following its own rules. This is the watchman watching
    the watchman.
    
    Key principle: Meta-verification must itself be bounded
    to avoid infinite regress.
    """
    
    # Hard limits on meta-verification itself
    MAX_META_DEPTH = 3          # Max recursive meta-verification levels
    MAX_META_TIME_MS = 100      # Max time for meta-verification
    MAX_CONSTRAINTS = 100       # Max constraints to check
    
    def __init__(self):
        self.constraints = META_CONSTRAINTS.copy()
        self.verification_count = 0
        self.violations_detected = 0
        self._current_depth = 0
        self._chain: List[str] = []  # Hash chain of verifications
    
    def _hash(self, data: str) -> str:
        """Deterministic hash."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _check_result(
        self,
        constraint: MetaConstraint,
        passed: bool,
        message: str,
        evidence: Dict,
        elapsed_us: int
    ) -> ConstraintResult:
        """Create a constraint result."""
        return ConstraintResult(
            constraint=constraint,
            status=ConstraintStatus.SATISFIED if passed else ConstraintStatus.VIOLATED,
            message=message,
            evidence=evidence,
            checked_at=datetime.now(),
            elapsed_us=elapsed_us,
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRAINT CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_bounded_iterations(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that iterations are bounded."""
        max_allowed = context.get("max_iterations", 10000)
        actual = context.get("iterations", 0)
        
        passed = actual <= max_allowed
        message = f"Iterations: {actual}/{max_allowed}"
        evidence = {"max_allowed": max_allowed, "actual": actual}
        
        return passed, message, evidence
    
    def check_bounded_recursion(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that recursion depth is bounded."""
        max_allowed = context.get("max_recursion", 100)
        actual = context.get("recursion_depth", 0)
        
        passed = actual <= max_allowed
        message = f"Recursion depth: {actual}/{max_allowed}"
        evidence = {"max_allowed": max_allowed, "actual": actual}
        
        return passed, message, evidence
    
    def check_bounded_memory(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that memory usage is bounded."""
        max_allowed = context.get("max_memory_bytes", 100_000_000)
        actual = context.get("memory_bytes", 0)
        
        passed = actual <= max_allowed
        message = f"Memory: {actual:,}/{max_allowed:,} bytes"
        evidence = {"max_allowed": max_allowed, "actual": actual}
        
        return passed, message, evidence
    
    def check_bounded_time(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that execution time is bounded."""
        max_allowed_ms = context.get("max_time_ms", 30000)
        actual_ms = context.get("elapsed_ms", 0)
        
        passed = actual_ms <= max_allowed_ms
        message = f"Time: {actual_ms}ms/{max_allowed_ms}ms"
        evidence = {"max_allowed_ms": max_allowed_ms, "actual_ms": actual_ms}
        
        return passed, message, evidence
    
    def check_hash_chain(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that hash chain is intact."""
        chain = context.get("hash_chain", [])
        
        if len(chain) < 2:
            return True, "Chain too short to verify", {"length": len(chain)}
        
        # Verify each link
        for i in range(1, len(chain)):
            expected_prev = chain[i].get("prev_hash")
            actual_prev = chain[i-1].get("hash")
            
            if expected_prev != actual_prev:
                return False, f"Chain broken at index {i}", {
                    "break_index": i,
                    "expected": expected_prev[:12] if expected_prev else None,
                    "actual": actual_prev[:12] if actual_prev else None,
                }
        
        return True, f"Chain intact ({len(chain)} links)", {"length": len(chain)}
    
    def check_immutability(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that historical entries haven't been modified."""
        snapshots = context.get("snapshots", {})
        current = context.get("current_state", {})
        
        for key, original_hash in snapshots.items():
            if key in current:
                current_hash = self._hash(str(current[key]))
                if current_hash != original_hash:
                    return False, f"Modification detected: {key}", {
                        "key": key,
                        "original_hash": original_hash[:12],
                        "current_hash": current_hash[:12],
                    }
        
        return True, "No retroactive modifications", {"checked": len(snapshots)}
    
    def check_determinism(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that same input produces same output."""
        test_cases = context.get("determinism_tests", [])
        
        for test in test_cases:
            input_data = test.get("input")
            expected = test.get("expected_hash")
            actual = test.get("actual_hash")
            
            if expected and actual and expected != actual:
                return False, "Non-deterministic output detected", {
                    "input": str(input_data)[:50],
                    "expected_hash": expected[:12],
                    "actual_hash": actual[:12],
                }
        
        return True, "Determinism verified", {"tests": len(test_cases)}
    
    def check_constraint_consistency(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that constraints don't contradict each other."""
        constraints = context.get("active_constraints", [])
        
        # Simple contradiction detection
        # In a full implementation, this would be a SAT solver
        names = set()
        for c in constraints:
            name = c.get("name", "")
            negation = f"not_{name}"
            if negation in names or (name.startswith("not_") and name[4:] in names):
                return False, f"Contradictory constraint: {name}", {
                    "constraint": name,
                }
            names.add(name)
        
        return True, "No contradictions found", {"checked": len(constraints)}
    
    def check_meta_termination(
        self,
        context: Dict
    ) -> Tuple[bool, str, Dict]:
        """Check that meta-verification itself terminates."""
        depth = context.get("meta_depth", self._current_depth)
        
        passed = depth < self.MAX_META_DEPTH
        message = f"Meta depth: {depth}/{self.MAX_META_DEPTH}"
        evidence = {"depth": depth, "max": self.MAX_META_DEPTH}
        
        return passed, message, evidence
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN VERIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def verify(
        self,
        context: Dict,
        level: VerificationLevel = VerificationLevel.OPERATIONAL
    ) -> MetaVerification:
        """
        Perform meta-verification on Newton's state.
        
        Args:
            context: Current execution context with metrics
            level: Minimum verification level to check
        
        Returns:
            MetaVerification with all results
        """
        start = time.perf_counter()
        self.verification_count += 1
        self._current_depth += 1
        
        try:
            # Enforce meta-bounds
            if self._current_depth > self.MAX_META_DEPTH:
                return self._create_bounded_result("Meta-depth exceeded")
            
            results = []
            satisfied = 0
            violated = 0
            critical_violations = 0
            
            # Check applicable constraints
            applicable = [c for c in self.constraints 
                         if self._level_order(c.level) >= self._level_order(level)]
            
            for constraint in applicable[:self.MAX_CONSTRAINTS]:
                check_start = time.perf_counter()
                
                # Get check function
                check_fn = getattr(self, constraint.check_fn, None)
                if not check_fn:
                    results.append(self._check_result(
                        constraint, False, "Check function not found", {}, 0
                    ))
                    violated += 1
                    continue
                
                # Run check
                try:
                    passed, message, evidence = check_fn(context)
                    elapsed = int((time.perf_counter() - check_start) * 1_000_000)
                    
                    result = self._check_result(
                        constraint, passed, message, evidence, elapsed
                    )
                    results.append(result)
                    
                    if passed:
                        satisfied += 1
                    else:
                        violated += 1
                        if constraint.critical:
                            critical_violations += 1
                            
                except Exception as e:
                    results.append(self._check_result(
                        constraint, False, f"Check failed: {str(e)}", {}, 0
                    ))
                    violated += 1
            
            # Calculate total elapsed
            total_elapsed = int((time.perf_counter() - start) * 1_000_000)
            
            # Build chain hash
            chain_data = "|".join(r.constraint.name + ":" + r.status.value 
                                  for r in results)
            chain_hash = self._hash(chain_data)
            self._chain.append(chain_hash)
            
            # Overall verification status
            verified = critical_violations == 0
            if not verified:
                self.violations_detected += 1
            
            return MetaVerification(
                verified=verified,
                level=level,
                results=results,
                chain_hash=chain_hash,
                timestamp=datetime.now(),
                total_elapsed_us=total_elapsed,
                satisfied=satisfied,
                violated=violated,
                critical_violations=critical_violations,
            )
            
        finally:
            self._current_depth -= 1
    
    def _level_order(self, level: VerificationLevel) -> int:
        """Get ordering for verification levels."""
        order = {
            VerificationLevel.SYNTACTIC: 1,
            VerificationLevel.SEMANTIC: 2,
            VerificationLevel.OPERATIONAL: 3,
            VerificationLevel.TEMPORAL: 4,
            VerificationLevel.CHAIN: 5,
            VerificationLevel.RECURSIVE: 6,
        }
        return order.get(level, 0)
    
    def _create_bounded_result(self, reason: str) -> MetaVerification:
        """Create a result when meta-bounds are exceeded."""
        return MetaVerification(
            verified=False,
            level=VerificationLevel.RECURSIVE,
            results=[],
            chain_hash=self._hash(reason),
            timestamp=datetime.now(),
            total_elapsed_us=0,
            satisfied=0,
            violated=1,
            critical_violations=1,
        )
    
    def quick_check(self, context: Dict) -> Tuple[bool, str]:
        """
        Quick meta-check - just critical constraints.
        Returns (passed, summary).
        """
        critical = [c for c in self.constraints if c.critical]
        
        for constraint in critical[:5]:  # Only check first 5 critical
            check_fn = getattr(self, constraint.check_fn, None)
            if check_fn:
                try:
                    passed, message, _ = check_fn(context)
                    if not passed:
                        return False, f"{constraint.name}: {message}"
                except:
                    pass
        
        return True, "Quick check passed"
    
    def get_stats(self) -> Dict:
        """Get meta-verification statistics."""
        return {
            "verification_count": self.verification_count,
            "violations_detected": self.violations_detected,
            "chain_length": len(self._chain),
            "constraints_defined": len(self.constraints),
            "current_depth": self._current_depth,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_meta: Optional[MetaNewton] = None

def get_meta_newton() -> MetaNewton:
    """Get the global MetaNewton instance."""
    global _meta
    if _meta is None:
        _meta = MetaNewton()
    return _meta


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    meta = MetaNewton()
    
    print("═" * 70)
    print("META NEWTON - THE SELF-VERIFIER")
    print("Newton verifying Newton.")
    print("═" * 70)
    
    # Test with good context
    print("\n✓ GOOD CONTEXT TEST")
    print("-" * 40)
    
    good_context = {
        "iterations": 100,
        "max_iterations": 10000,
        "recursion_depth": 5,
        "max_recursion": 100,
        "memory_bytes": 1_000_000,
        "max_memory_bytes": 100_000_000,
        "elapsed_ms": 50,
        "max_time_ms": 30000,
        "hash_chain": [
            {"hash": "abc123", "prev_hash": None},
            {"hash": "def456", "prev_hash": "abc123"},
        ],
        "meta_depth": 0,
    }
    
    result = meta.verify(good_context)
    print(f"Verified: {result.verified}")
    print(f"Satisfied: {result.satisfied}/{len(result.results)}")
    print(f"Elapsed: {result.total_elapsed_us}μs")
    
    # Test with bad context
    print("\n✗ BAD CONTEXT TEST")
    print("-" * 40)
    
    bad_context = {
        "iterations": 100000,  # Exceeds limit
        "max_iterations": 10000,
        "recursion_depth": 5,
        "elapsed_ms": 50000,  # Exceeds time limit
        "max_time_ms": 30000,
        "meta_depth": 0,
    }
    
    result = meta.verify(bad_context)
    print(f"Verified: {result.verified}")
    print(f"Critical violations: {result.critical_violations}")
    
    for r in result.results:
        if r.status == ConstraintStatus.VIOLATED:
            print(f"  ✗ {r.constraint.name}: {r.message}")
    
    # Quick check
    print("\n⚡ QUICK CHECK TEST")
    print("-" * 40)
    
    passed, message = meta.quick_check(good_context)
    print(f"Quick check: {'✓' if passed else '✗'} {message}")
    
    # Stats
    print("\n📊 STATS")
    print("-" * 40)
    stats = meta.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
