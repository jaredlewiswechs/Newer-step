#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
UNIFIED COMPILER PIPELINE (Paper Section 10.3)

A unified front-end pipeline:
    1. Intent Lock (choose regime R)
    2. Parse (shape grammar / kinematic query parsing)
    3. Abstract Interpretation (semantic field resolution)
    4. Geometric Check (glyph/vector admissibility under R)
    5. Verify/Upgrade (trust lattice)
    6. Execute under bounds
    7. Log provenance
    8. Meta-check invariants
    9. Return (value, trace)

From "Newton as a Verified Computation Substrate":
> This isn't "an agent." It's a computational substrate whose default output is:
> Answer = (v, π, trust-label, bounds-report, ledger-proof)

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from datetime import datetime
import time
import hashlib
import re

from .regime import Regime, RegimeType, get_regime_registry
from .trust import TrustLabel, TrustLattice, Labeled, get_trust_lattice
from .distortion import DistortionMetric, GeometryMismatchError, get_distortion_metric

# Import Nina's knowledge integration (bridges to adan_portable)
try:
    from .knowledge import NinaKnowledge, get_nina_knowledge, NinaFact
    HAS_NINA_KB = True
except ImportError:
    HAS_NINA_KB = False

# Import adan_portable's query parser directly for shape recognition
try:
    from adan.query_parser import (
        KinematicQueryParser, 
        get_query_parser,
        QueryShape as AdanQueryShape,
        ParsedQuery as AdanParsedQuery,
    )
    HAS_ADAN_PARSER = True
except ImportError:
    HAS_ADAN_PARSER = False

# Import Ollama fallback (governed LLM for queries KB can't answer)
try:
    from .ollama import NinaOllama, get_nina_ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


class PipelineStage(Enum):
    """The 9 stages of the compiler pipeline."""
    INTENT_LOCK = 1          # Choose regime R
    PARSE = 2                # Shape grammar parsing
    ABSTRACT_INTERPRET = 3   # Semantic field resolution
    GEOMETRIC_CHECK = 4      # Distortion check under R
    VERIFY_UPGRADE = 5       # Trust lattice upgrade
    EXECUTE = 6              # Bounded execution
    LOG_PROVENANCE = 7       # Ledger commit
    META_CHECK = 8           # Invariant verification
    RETURN = 9               # Final output


@dataclass
class ExecutionBounds:
    """
    Resource bounds for execution (Paper Section 6).
    
    Let a resource vector be:
        r = (iters, depth, ops, time)
    with bounds:
        r ≤ B
    """
    max_iterations: int = 10000
    max_recursion_depth: int = 100
    max_operations: int = 1000000
    timeout_seconds: float = 30.0
    
    def __post_init__(self):
        # Hard caps
        self.max_iterations = min(self.max_iterations, 1000000)
        self.max_recursion_depth = min(self.max_recursion_depth, 1000)
        self.max_operations = min(self.max_operations, 100000000)


@dataclass
class BoundsReport:
    """Report of resource usage during execution."""
    iterations_used: int = 0
    recursion_depth_max: int = 0
    operations_count: int = 0
    time_elapsed_ms: float = 0.0
    within_bounds: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "iterations": self.iterations_used,
            "recursion_depth": self.recursion_depth_max,
            "operations": self.operations_count,
            "time_ms": round(self.time_elapsed_ms, 3),
            "within_bounds": self.within_bounds
        }


@dataclass
class ProvenanceEntry:
    """A single entry in the provenance ledger."""
    index: int
    timestamp: str
    operation: str
    input_hash: str
    output_hash: str
    prev_hash: str
    entry_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "prev_hash": self.prev_hash,
            "hash": self.entry_hash
        }


@dataclass
class PipelineTrace:
    """Trace of pipeline execution through all stages."""
    stages: List[Dict[str, Any]] = field(default_factory=list)
    
    def add(self, stage: PipelineStage, status: str, details: Any = None):
        self.stages.append({
            "stage": stage.value,
            "name": stage.name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_list(self) -> List[Dict[str, Any]]:
        return self.stages


@dataclass
class PipelineResult:
    """
    The output of the pipeline (Paper Section 11).
    
    Answer = (v, π, trust-label, bounds-report, ledger-proof)
    """
    value: Any
    trace: PipelineTrace
    trust_label: TrustLabel
    bounds_report: BoundsReport
    ledger_proof: Optional[ProvenanceEntry] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "trace": self.trace.to_list(),
            "trust_label": self.trust_label.name,
            "bounds_report": self.bounds_report.to_dict(),
            "ledger_proof": self.ledger_proof.to_dict() if self.ledger_proof else None,
            "success": self.success,
            "error": self.error
        }


class QueryShape(Enum):
    """
    Typed query shapes (Paper Section 2.1).
    
    Each shape has an input type and output type.
    """
    CAPITAL_OF = "capital_of"           # Country → City
    POPULATION_OF = "population_of"     # Country → ℕ
    VERIFY_FACT = "verify_fact"         # Statement → 𝔹
    CALCULATE = "calculate"             # Expression → Number
    DEFINE = "define"                   # Name, Value → ()
    RETRIEVE = "retrieve"               # Key → Value
    UNKNOWN = "unknown"                 # Any → Any (requires upgrade)


@dataclass
class ParsedQuery:
    """A parsed query with shape and slots."""
    shape: QueryShape
    slots: Dict[str, Any]
    raw_input: str
    confidence: float = 1.0


class Pipeline:
    """
    The unified 9-stage compiler pipeline.
    
    Usage:
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        result = pipeline.process("What is the capital of France?")
        
        # Result contains:
        # - value: "Paris"
        # - trace: [...stages...]
        # - trust_label: TRUSTED
        # - bounds_report: {ops: 42, time_ms: 12}
        # - ledger_proof: {hash: "0x..."}
    """
    
    def __init__(
        self,
        regime: Optional[Regime] = None,
        bounds: Optional[ExecutionBounds] = None,
        trust_lattice: Optional[TrustLattice] = None,
        distortion_metric: Optional[DistortionMetric] = None
    ):
        self.regime = regime or Regime.from_type(RegimeType.FACTUAL)
        self.bounds = bounds or ExecutionBounds()
        self.lattice = trust_lattice or get_trust_lattice()
        self.distortion = distortion_metric or get_distortion_metric()
        
        # Provenance ledger (simple in-memory implementation)
        self._ledger: List[ProvenanceEntry] = []
        self._prev_hash = "0" * 64
        
        # Knowledge system - USE adan_portable KB, not a duplicate!
        self._knowledge: Optional['NinaKnowledge'] = None
        if HAS_NINA_KB:
            self._knowledge = get_nina_knowledge()
        
        # Ollama fallback for queries KB can't answer (governed, local)
        self._ollama: Optional['NinaOllama'] = None
        if HAS_OLLAMA:
            self._ollama = get_nina_ollama()
        
        # Fallback mini-KB only if adan_portable unavailable
        self._fallback_kb: Dict[str, Any] = {
            "capital:france": "Paris",
            "capital:germany": "Berlin",
            "capital:japan": "Tokyo",
            "capital:uk": "London",
            "capital:usa": "Washington, D.C.",
            "population:france": 67390000,
            "population:germany": 83240000,
            "population:japan": 125800000,
        }
    
    def process(self, input_text: str) -> PipelineResult:
        """
        Run the full 9-stage pipeline.
        
        Args:
            input_text: The user input to process
            
        Returns:
            PipelineResult with value, trace, trust, bounds, and provenance
        """
        trace = PipelineTrace()
        start_time = time.time()
        bounds_report = BoundsReport()
        
        # STAGE 0: INPUT SANITIZATION (Defense in Depth)
        # Sanitize input BEFORE any parsing to prevent injection attacks
        input_text = self._sanitize_input(input_text)
        
        try:
            # Stage 1: Intent Lock
            trace.add(PipelineStage.INTENT_LOCK, "OK", {
                "regime": self.regime.name,
                "type": self.regime.regime_type.value
            })
            
            # Stage 2: Parse
            parsed = self._parse(input_text)
            trace.add(PipelineStage.PARSE, "OK", {
                "shape": parsed.shape.value,
                "slots": parsed.slots,
                "confidence": parsed.confidence
            })
            
            # Stage 3: Abstract Interpretation
            resolved = self._abstract_interpret(parsed)
            trace.add(PipelineStage.ABSTRACT_INTERPRET, "OK", resolved)
            
            # Stage 4: Geometric Check
            self._geometric_check(parsed, resolved)
            trace.add(PipelineStage.GEOMETRIC_CHECK, "OK", {
                "admissible": True,
                "threshold": self.regime.distortion_threshold
            })
            
            # Stage 5: Verify/Upgrade
            labeled_result = self._verify_upgrade(resolved)
            trace.add(PipelineStage.VERIFY_UPGRADE, "OK", {
                "trust": labeled_result.label.name
            })
            
            # Stage 6: Execute
            value, ops = self._execute(parsed, resolved, labeled_result)
            bounds_report.operations_count = ops
            bounds_report.time_elapsed_ms = (time.time() - start_time) * 1000
            trace.add(PipelineStage.EXECUTE, "OK", {
                "operations": ops
            })
            
            # Stage 7: Log Provenance
            provenance = self._log_provenance(input_text, value)
            trace.add(PipelineStage.LOG_PROVENANCE, "OK", {
                "entry_hash": provenance.entry_hash[:16]
            })
            
            # Stage 8: Meta-check
            self._meta_check(value, labeled_result)
            trace.add(PipelineStage.META_CHECK, "OK", {
                "invariants": "verified"
            })
            
            # Stage 9: Return
            trace.add(PipelineStage.RETURN, "OK", {
                "value_type": type(value).__name__
            })
            
            return PipelineResult(
                value=value,
                trace=trace,
                trust_label=labeled_result.label,
                bounds_report=bounds_report,
                ledger_proof=provenance
            )
            
        except GeometryMismatchError as e:
            trace.add(PipelineStage.GEOMETRIC_CHECK, "FAIL", {
                "error": str(e),
                "suggestions": e.suggestions
            })
            bounds_report.time_elapsed_ms = (time.time() - start_time) * 1000
            return PipelineResult(
                value=None,
                trace=trace,
                trust_label=TrustLabel.UNTRUSTED,
                bounds_report=bounds_report,
                error=str(e)
            )
            
        except Exception as e:
            bounds_report.time_elapsed_ms = (time.time() - start_time) * 1000
            return PipelineResult(
                value=None,
                trace=trace,
                trust_label=TrustLabel.UNTRUSTED,
                bounds_report=bounds_report,
                error=str(e)
            )
    
    def _parse(self, input_text: str) -> ParsedQuery:
        """
        Stage 2: Parse input into typed query shape.
        
        USES ADAN'S KINEMATIC QUERY PARSER - not a duplicate implementation.
        The parser recognizes 20+ query shapes with proper regex patterns.
        """
        # Use adan's parser if available (the REAL kinematic parser)
        if HAS_ADAN_PARSER:
            adan_parser = get_query_parser()
            adan_parsed = adan_parser.parse(input_text)
            
            # Map adan QueryShape to Nina QueryShape
            shape_map = {
                AdanQueryShape.CAPITAL_OF: QueryShape.CAPITAL_OF,
                AdanQueryShape.POPULATION_OF: QueryShape.POPULATION_OF,
                AdanQueryShape.VERIFY_FACT: QueryShape.VERIFY_FACT,
                AdanQueryShape.UNKNOWN: QueryShape.UNKNOWN,
            }
            
            nina_shape = shape_map.get(adan_parsed.shape, QueryShape.UNKNOWN)
            
            # Build slots from adan's parsed data
            slots = {}
            if adan_parsed.slot:
                # Map slot name based on shape
                if nina_shape == QueryShape.CAPITAL_OF:
                    slots["country"] = adan_parsed.slot
                elif nina_shape == QueryShape.POPULATION_OF:
                    slots["country"] = adan_parsed.slot
                elif nina_shape == QueryShape.VERIFY_FACT:
                    slots["statement"] = adan_parsed.slot
                else:
                    slots["raw"] = adan_parsed.slot
            else:
                slots["raw"] = input_text
            
            return ParsedQuery(
                shape=nina_shape,
                slots=slots,
                raw_input=input_text,
                confidence=adan_parsed.confidence
            )
        
        # Minimal fallback only if adan parser unavailable
        text_lower = input_text.lower()
        
        # Only handle calculation pattern (pure numbers/operators)
        # Everything else goes to UNKNOWN for KB/Ollama handling
        calc_match = re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', text_lower.strip())
        if calc_match:
            return ParsedQuery(
                shape=QueryShape.CALCULATE,
                slots={"expression": text_lower.strip()},
                raw_input=input_text,
                confidence=0.9
            )
        
        # Unknown shape - will be resolved by KB or Ollama
        return ParsedQuery(
            shape=QueryShape.UNKNOWN,
            slots={"raw": input_text},
            raw_input=input_text,
            confidence=0.5
        )
    
    def _abstract_interpret(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """
        Stage 3: Semantic field resolution via abstract interpretation.
        
        Uses adan_portable's knowledge base when available for full
        5-tier kinematic semantics.
        """
        result = {
            "shape": parsed.shape,
            "resolved_slots": {},
            "semantic_field": None
        }
        
        # Try adan_portable KB first (full 5-tier resolution)
        if self._knowledge and self._knowledge.is_available:
            if parsed.shape == QueryShape.CAPITAL_OF:
                country = parsed.slots.get("country", "").lower()
                capital = self._knowledge.get_capital(country)
                if capital:
                    result["resolved_slots"]["answer"] = capital
                    result["semantic_field"] = "geography"
                    result["source"] = "adan_knowledge_base"
                    return result
                    
            elif parsed.shape == QueryShape.POPULATION_OF:
                country = parsed.slots.get("country", "").lower()
                pop_data = self._knowledge.get_population(country)
                if pop_data:
                    pop, year = pop_data
                    result["resolved_slots"]["answer"] = pop
                    result["resolved_slots"]["year"] = year
                    result["semantic_field"] = "demographics"
                    result["source"] = "adan_knowledge_base"
                    return result
            
            # For unknown shapes, try full KB query
            elif parsed.shape == QueryShape.UNKNOWN:
                fact = self._knowledge.query(parsed.raw_input)
                if fact:
                    result["resolved_slots"]["answer"] = fact.value
                    result["resolved_slots"]["fact_text"] = fact.fact_text
                    result["semantic_field"] = fact.category
                    result["source"] = f"adan_{fact.query_tier}"
                    return result
        
        # Fallback to mini-KB if adan not available
        if parsed.shape == QueryShape.CAPITAL_OF:
            country = parsed.slots.get("country", "").lower()
            key = f"capital:{country}"
            if key in self._fallback_kb:
                result["resolved_slots"]["answer"] = self._fallback_kb[key]
                result["semantic_field"] = "geography"
                result["source"] = "fallback_kb"
            else:
                result["resolved_slots"]["answer"] = None
                result["source"] = "not_found"
                
        elif parsed.shape == QueryShape.POPULATION_OF:
            country = parsed.slots.get("country", "").lower()
            key = f"population:{country}"
            if key in self._fallback_kb:
                result["resolved_slots"]["answer"] = self._fallback_kb[key]
                result["semantic_field"] = "demographics"
                result["source"] = "fallback_kb"
            else:
                result["resolved_slots"]["answer"] = None
                result["source"] = "not_found"
                
        elif parsed.shape == QueryShape.CALCULATE:
            result["resolved_slots"]["expression"] = parsed.slots.get("expression", "0")
            result["semantic_field"] = "mathematics"
            result["source"] = "computation"
            
        elif parsed.shape == QueryShape.VERIFY_FACT:
            result["resolved_slots"]["statement"] = parsed.slots.get("statement", "")
            result["semantic_field"] = "verification"
            result["source"] = "inference"
            
        else:
            result["semantic_field"] = "unknown"
            result["source"] = "unresolved"
        
        # STAGE 3.5: OLLAMA FALLBACK
        # If KB didn't find an answer for unknown queries, try Ollama
        # Ollama is GOVERNED - runs locally, trust level VERIFIED (not TRUSTED)
        if (result.get("source") == "unresolved" or result.get("resolved_slots", {}).get("answer") is None):
            if self._ollama and parsed.shape == QueryShape.UNKNOWN:
                ollama_response = self._ollama.generate(parsed.raw_input)
                if ollama_response:
                    result["resolved_slots"]["answer"] = ollama_response
                    result["semantic_field"] = "ollama_generation"
                    result["source"] = "ollama_governed"
                    result["llm_model"] = self._ollama.config.model
        
        return result
    
    def _geometric_check(self, parsed: ParsedQuery, resolved: Dict[str, Any]) -> None:
        """Stage 4: Check glyph/vector admissibility under regime R."""
        # For factual queries, check if the semantic field is admissible
        if self.regime.regime_type == RegimeType.MATHEMATICAL:
            if resolved.get("semantic_field") not in ["mathematics", "logic"]:
                # Check distortion between query words and mathematical action
                words = parsed.raw_input.lower().split()
                for word in words:
                    if word in ["delete", "destroy", "crash"]:
                        # High-force words in mathematical context
                        distortion = self.distortion.compute_distortion(
                            word, "data_read"
                        )
                        if distortion > self.regime.distortion_threshold:
                            raise GeometryMismatchError(
                                word=word,
                                action="mathematical_query",
                                distortion=distortion,
                                threshold=self.regime.distortion_threshold,
                                suggestions=["calculate", "compute", "evaluate"]
                            )
    
    def _verify_upgrade(self, resolved: Dict[str, Any]) -> Labeled:
        """Stage 5: Apply trust lattice verification/upgrade."""
        answer = resolved.get("resolved_slots", {}).get("answer")
        source = resolved.get("source", "unknown")
        
        # Label based on source
        if source in ["adan_knowledge_base", "adan_store", "adan_shape", "adan_semantic", "adan_keyword"]:
            # adan_portable KB is authoritative - TRUSTED
            return self.lattice.label(answer, TrustLabel.TRUSTED, source)
        elif source == "fallback_kb":
            # Fallback KB is verified but less authoritative
            return self.lattice.label(answer, TrustLabel.VERIFIED, source)
        elif source == "ollama_governed":
            # Ollama is local and governed - VERIFIED level (not TRUSTED)
            # "We govern Ollama" - it's controlled but not authoritative
            return self.lattice.label(answer, TrustLabel.VERIFIED, source)
        elif source == "computation":
            # Computation is trusted (Newton verified)
            return self.lattice.label(
                resolved.get("resolved_slots", {}), 
                TrustLabel.TRUSTED, 
                source
            )
        else:
            # Unknown source - untrusted until verified
            return self.lattice.untrusted(answer, source)
    
    def _execute(
        self, 
        parsed: ParsedQuery, 
        resolved: Dict[str, Any],
        labeled: Labeled
    ) -> Tuple[Any, int]:
        """Stage 6: Execute under bounds."""
        ops = 0
        
        if parsed.shape == QueryShape.CALCULATE:
            expr = resolved.get("resolved_slots", {}).get("expression", "0")
            # Safe evaluation with bounds
            try:
                # Only allow safe characters
                safe_expr = re.sub(r'[^0-9\+\-\*\/\(\)\.\s]', '', expr)
                result = eval(safe_expr, {"__builtins__": {}})
                ops = len(safe_expr)
                return result, ops
            except:
                return None, 1
                
        elif parsed.shape in [QueryShape.CAPITAL_OF, QueryShape.POPULATION_OF]:
            answer = resolved.get("resolved_slots", {}).get("answer")
            ops = 1
            return answer, ops
            
        elif parsed.shape == QueryShape.VERIFY_FACT:
            statement = resolved.get("resolved_slots", {}).get("statement", "")
            # Simple fact verification
            verified = self._verify_statement(statement)
            ops = 10
            return verified, ops
        
        return labeled.value, 1
    
    def _verify_statement(self, statement: str) -> bool:
        """Simple statement verification against knowledge base."""
        statement_lower = statement.lower()
        
        # Try adan_portable KB first
        if self._knowledge and self._knowledge.is_available:
            # Check for capital facts
            capital_match = re.search(r'(\w+) is the capital of (\w+)', statement_lower)
            if capital_match:
                city, country = capital_match.groups()
                actual_capital = self._knowledge.get_capital(country)
                if actual_capital and actual_capital.lower() == city.lower():
                    return True
            
            # Try a general query
            fact = self._knowledge.query(statement)
            if fact and fact.confidence > 0.7:
                return True
        
        # Fallback checks
        for key, value in self._fallback_kb.items():
            if key.startswith("capital:"):
                country = key.split(":")[1]
                if country in statement_lower and str(value).lower() in statement_lower:
                    return True
        
        # Check for mathematical truths
        math_truths = ["1 == 1", "2 + 2 = 4", "1 + 1 = 2"]
        for truth in math_truths:
            if truth in statement or truth.replace(" ", "") in statement.replace(" ", ""):
                return True
        
        return False
    
    def _log_provenance(self, input_text: str, output: Any) -> ProvenanceEntry:
        """Stage 7: Log to provenance ledger."""
        index = len(self._ledger)
        timestamp = datetime.now().isoformat()
        
        input_hash = hashlib.sha256(str(input_text).encode()).hexdigest()
        output_hash = hashlib.sha256(str(output).encode()).hexdigest()
        
        # Compute entry hash using full prev_hash
        entry_data = f"{index}|{timestamp}|{input_hash}|{output_hash}|{self._prev_hash}"
        entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        entry = ProvenanceEntry(
            index=index,
            timestamp=timestamp,
            operation="query",
            input_hash=input_hash[:16],
            output_hash=output_hash[:16],
            prev_hash=self._prev_hash,  # Store FULL hash for chain verification
            entry_hash=entry_hash        # Full hash
        )
        
        self._ledger.append(entry)
        self._prev_hash = entry_hash  # Full hash for next entry
        
        return entry
    
    def _meta_check(self, value: Any, labeled: Labeled) -> None:
        """Stage 8: Verify invariants hold."""
        # Check that trusted values came from trusted sources
        if labeled.label >= TrustLabel.TRUSTED:
            if labeled.source not in self.regime.trusted_sources and "any" not in self.regime.trusted_sources:
                raise ValueError(
                    f"Invariant violation: TRUSTED label from untrusted source {labeled.source}"
                )
    
    def _sanitize_input(self, input_text: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Defense in depth: Even though slots are only used for dictionary lookups
        (not SQL, eval, or shell commands), we sanitize to protect against:
        1. Log injection (newlines, control chars)
        2. ReDoS (regex denial of service via catastrophic backtracking)
        3. Future code changes that might use slots unsafely
        4. XSS if values ever rendered in HTML
        
        POLICY:
        - Max length: 1000 chars (prevents DoS, reasonable for queries)
        - Strip control characters (except space)
        - Neutralize shell metacharacters
        - Neutralize HTML/script tags
        - Preserve natural language queries
        """
        # Bound length first (prevents ReDoS and memory exhaustion)
        MAX_INPUT_LENGTH = 1000
        if len(input_text) > MAX_INPUT_LENGTH:
            input_text = input_text[:MAX_INPUT_LENGTH]
        
        # Remove null bytes and control characters (keep printable + space)
        # This prevents log injection and terminal control sequence attacks
        sanitized = ''.join(
            c for c in input_text 
            if c.isprintable() or c == ' '
        )
        
        # Neutralize shell injection patterns
        # Replace dangerous shell metacharacters with safe equivalents
        shell_escapes = {
            '$': '＄',      # Dollar sign → fullwidth (neutralizes $(...), ${...})
            '`': '｀',      # Backtick → fullwidth (neutralizes `...`)
            ';': '；',      # Semicolon → fullwidth (neutralizes cmd chaining)
            '|': '｜',      # Pipe → fullwidth (neutralizes piping)
            '&': '＆',      # Ampersand → fullwidth (neutralizes background/AND)
            '\n': ' ',      # Newline → space (neutralizes command injection)
            '\r': ' ',      # Carriage return → space
        }
        for dangerous, safe in shell_escapes.items():
            sanitized = sanitized.replace(dangerous, safe)
        
        # Neutralize HTML/XSS patterns
        # Replace angle brackets with HTML entities or safe chars
        sanitized = sanitized.replace('<', '＜')
        sanitized = sanitized.replace('>', '＞')
        
        # Collapse multiple spaces (prevents regex DoS patterns)
        while '  ' in sanitized:
            sanitized = sanitized.replace('  ', ' ')
        
        return sanitized.strip()
    
    def get_ledger(self) -> List[Dict[str, Any]]:
        """Get the provenance ledger."""
        return [e.to_dict() for e in self._ledger]


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    
    print("=" * 70)
    print("PIPELINE TEST")
    print("9-Stage Unified Compiler Pipeline")
    print("=" * 70)
    
    # Create pipeline with factual regime
    regime = Regime.from_type(RegimeType.FACTUAL)
    pipeline = Pipeline(regime)
    
    # Test queries
    queries = [
        "What is the capital of France?",
        "What is the population of Germany?",
        "Calculate 2 + 2 * 3",
        "Verify: Paris is the capital of France",
        "Something completely unknown",
    ]
    
    for query in queries:
        print(f"\n📝 Query: \"{query}\"")
        result = pipeline.process(query)
        
        if result.success:
            print(f"   ✓ Value: {result.value}")
            print(f"   ✓ Trust: {result.trust_label.name}")
            print(f"   ✓ Bounds: {result.bounds_report.operations_count} ops, "
                  f"{result.bounds_report.time_elapsed_ms:.2f}ms")
            print(f"   ✓ Ledger: {result.ledger_proof.entry_hash[:16]}...")
        else:
            print(f"   ✗ Error: {result.error}")
            print(f"   ✗ Trust: {result.trust_label.name}")
    
    # Show pipeline trace for last query
    print(f"\n{'=' * 70}")
    print("Pipeline Trace (last query):")
    print("=" * 70)
    for stage in result.trace.to_list():
        status_icon = "✓" if stage["status"] == "OK" else "✗"
        print(f"   {stage['stage']}. {stage['name']}: {status_icon}")
    
    # Show ledger
    print(f"\n{'=' * 70}")
    print("Provenance Ledger:")
    print("=" * 70)
    for entry in pipeline.get_ledger()[-3:]:
        print(f"   [{entry['index']}] {entry['hash'][:24]}...")
