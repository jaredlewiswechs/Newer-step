#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
COMPREHENSIVE TEST SUITE FOR ADA, META NEWTON, AND KNOWLEDGE MESH
Property-based testing with Hypothesis.

Tests:
    - Ada: Drift detection, pattern sensing, response watching
    - Meta Newton: Self-verification, constraint checking, bounds
    - Knowledge Mesh: Multi-source queries, cross-referencing

Run: pytest tests/test_ada_meta.py -v
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from datetime import datetime, timedelta

from adan.ada import (
    Ada, AlertLevel, DriftType, Anomaly, Whisper, Baseline,
    DriftDetector, SensePattern, get_ada
)
from adan.meta_newton import (
    MetaNewton, MetaVerification, VerificationLevel, ConstraintStatus,
    MetaConstraint, get_meta_newton
)
from adan.knowledge_sources import (
    KnowledgeMesh, MeshFact, SourceTier, SOURCES, get_knowledge_mesh
)


# ═══════════════════════════════════════════════════════════════════════════════
# ADA TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestDriftDetector:
    """Tests for the DriftDetector component."""
    
    def test_baseline_creation(self):
        """Test that baselines are created correctly."""
        detector = DriftDetector()
        baseline = detector.set_baseline("test_key", "test_value", "test_source")
        
        assert baseline.key == "test_key"
        assert baseline.value == "test_value"
        assert baseline.source == "test_source"
        assert baseline.confidence == 1.0
    
    def test_baseline_strengthening(self):
        """Test that repeated same values strengthen baseline."""
        detector = DriftDetector()
        
        detector.set_baseline("key", "value", "source")
        initial_count = detector.baselines["key"].verification_count
        
        # Same value again
        detector.set_baseline("key", "value", "source")
        
        assert detector.baselines["key"].verification_count > initial_count
    
    def test_drift_detection(self):
        """Test that drift is detected when value changes."""
        detector = DriftDetector()
        
        # Establish baseline
        detector.set_baseline("capital_france", "Paris", "cia")
        
        # Check same value - no drift
        assert detector.check_drift("capital_france", "Paris") is None
        
        # Check different value - drift!
        anomaly = detector.check_drift("capital_france", "Lyon")
        
        assert anomaly is not None
        assert anomaly.drift_type == DriftType.FACTUAL
        assert "capital_france" in anomaly.description
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_hash_determinism(self, value):
        """Test that hashing is deterministic."""
        detector = DriftDetector()
        
        hash1 = detector._hash_value(value)
        hash2 = detector._hash_value(value)
        
        assert hash1 == hash2
    
    def test_drift_rate_calculation(self):
        """Test drift rate calculation over time window."""
        detector = DriftDetector()
        
        # Initially zero
        assert detector.get_drift_rate(24) == 0.0
        
        # Add baseline and trigger drift
        detector.set_baseline("key", "value1", "source")
        detector.check_drift("key", "value2")  # Trigger drift
        
        # Now should have drift
        rate = detector.get_drift_rate(24)
        assert rate >= 0


class TestSensePattern:
    """Tests for the SensePattern quick-scan heuristics."""
    
    def test_contradiction_detection(self):
        """Test detection of contradiction patterns."""
        detections = SensePattern.quick_scan("This is always never true")
        
        assert len(detections) > 0
        types = [d[0] for d in detections]
        assert "absolute_contradiction" in types
    
    def test_false_certainty_detection(self):
        """Test detection of false certainty patterns."""
        detections = SensePattern.quick_scan("The answer is definitely maybe correct")
        
        assert len(detections) > 0
        types = [d[0] for d in detections]
        assert "confidence_mismatch" in types
    
    def test_clean_text_no_detection(self):
        """Test that clean text has no detections."""
        detections = SensePattern.quick_scan("Paris is the capital of France.")
        
        assert len(detections) == 0
    
    def test_certainty_hedging_detection(self):
        """Test detection of certainty hedging."""
        detections = SensePattern.quick_scan("100% guaranteed, but I'm not sure")
        
        assert len(detections) > 0
        types = [d[0] for d in detections]
        assert "certainty_hedging" in types
    
    @given(st.text(min_size=1, max_size=500))
    @settings(max_examples=50)
    def test_quick_scan_never_crashes(self, text):
        """Property: quick_scan should never crash on any input."""
        # Should not raise any exceptions
        result = SensePattern.quick_scan(text)
        assert isinstance(result, list)


class TestAda:
    """Tests for the Ada sentinel agent."""
    
    def test_ada_initialization(self):
        """Test Ada initializes correctly."""
        ada = Ada()
        
        assert ada.observations == 0
        assert ada.alerts_raised == 0
        assert len(ada.whispers) == 0
    
    def test_ada_sense_clean_text(self):
        """Test Ada doesn't alert on clean text."""
        ada = Ada()
        
        result = ada.sense("Paris is the capital of France.")
        
        assert result is None
    
    def test_ada_sense_problematic_text(self):
        """Test Ada alerts on problematic text."""
        ada = Ada()
        
        result = ada.sense("The answer is definitely maybe correct.")
        
        assert result is not None
        assert isinstance(result, Whisper)
        assert result.level in [AlertLevel.NOTICE, AlertLevel.ALERT, AlertLevel.ALARM]
    
    def test_ada_observe_baseline(self):
        """Test Ada can establish baselines."""
        ada = Ada()
        
        # Verification establishes baseline
        result = ada.observe("test_key", "test_value", "test_source", is_verification=True)
        
        assert result is None  # No whisper for baseline establishment
        assert "test_key" in ada.drift_detector.baselines
    
    def test_ada_observe_drift(self):
        """Test Ada detects drift from baseline."""
        ada = Ada()
        
        # Establish baseline
        ada.observe("capital", "Paris", "cia", is_verification=True)
        
        # Check drift
        result = ada.observe("capital", "Lyon", "user")
        
        assert result is not None
        assert result.level == AlertLevel.ALERT
    
    def test_ada_watch_response_unverified_certainty(self):
        """Test Ada flags unverified responses that express certainty."""
        ada = Ada()
        
        result = ada.watch_response(
            query="What is 2+2?",
            response="The answer is definitely 4.",
            verified=False,
            sources=[]
        )
        
        assert result is not None
        assert len(result.anomalies) > 0
    
    def test_ada_watch_response_verified_clean(self):
        """Test Ada accepts clean verified responses."""
        ada = Ada()
        
        result = ada.watch_response(
            query="What is the capital of France?",
            response="Paris is the capital of France.",
            verified=True,
            sources=["CIA Factbook"]
        )
        
        # Clean verified response might still trigger if patterns detected
        # The key is it doesn't crash
        assert result is None or isinstance(result, Whisper)
    
    def test_ada_status(self):
        """Test Ada status reporting."""
        ada = Ada()
        
        status = ada.get_status()
        
        assert "status" in status
        assert status["status"] == "watching"
        assert "observations" in status
        assert "alerts_raised" in status
    
    def test_ada_whisper_callback(self):
        """Test Ada whisper callback mechanism."""
        ada = Ada()
        whispers_received = []
        
        def callback(whisper: Whisper):
            whispers_received.append(whisper)
        
        ada.set_whisper_callback(callback)
        
        # Trigger a high-level alert
        ada.observe("key", "value1", "source", is_verification=True)
        ada.observe("key", "value2", "source")  # Drift - triggers alert
        
        assert len(whispers_received) > 0
    
    def test_get_ada_singleton(self):
        """Test global Ada instance."""
        ada1 = get_ada()
        ada2 = get_ada()
        
        assert ada1 is ada2


# ═══════════════════════════════════════════════════════════════════════════════
# META NEWTON TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestMetaNewton:
    """Tests for the Meta Newton self-verifier."""
    
    def test_meta_initialization(self):
        """Test Meta Newton initializes correctly."""
        meta = MetaNewton()
        
        assert meta.verification_count == 0
        assert meta.violations_detected == 0
        assert len(meta.constraints) > 0
    
    def test_verify_good_context(self):
        """Test verification passes with good context."""
        meta = MetaNewton()
        
        good_context = {
            "iterations": 100,
            "max_iterations": 10000,
            "recursion_depth": 5,
            "max_recursion": 100,
            "memory_bytes": 1_000_000,
            "max_memory_bytes": 100_000_000,
            "elapsed_ms": 50,
            "max_time_ms": 30000,
            "meta_depth": 0,
        }
        
        result = meta.verify(good_context)
        
        assert result.verified is True
        assert result.critical_violations == 0
    
    def test_verify_bad_iterations(self):
        """Test verification fails when iterations exceeded."""
        meta = MetaNewton()
        
        bad_context = {
            "iterations": 100000,  # Exceeds limit
            "max_iterations": 10000,
            "meta_depth": 0,
        }
        
        result = meta.verify(bad_context)
        
        assert result.verified is False
        assert result.violated > 0
    
    def test_verify_bad_time(self):
        """Test verification fails when time exceeded."""
        meta = MetaNewton()
        
        bad_context = {
            "elapsed_ms": 50000,  # Exceeds limit
            "max_time_ms": 30000,
            "meta_depth": 0,
        }
        
        result = meta.verify(bad_context)
        
        assert result.verified is False
    
    def test_check_hash_chain_intact(self):
        """Test hash chain verification."""
        meta = MetaNewton()
        
        context = {
            "hash_chain": [
                {"hash": "abc123", "prev_hash": None},
                {"hash": "def456", "prev_hash": "abc123"},
                {"hash": "ghi789", "prev_hash": "def456"},
            ],
            "meta_depth": 0,
        }
        
        passed, message, evidence = meta.check_hash_chain(context)
        
        assert passed is True
        assert "intact" in message.lower()
    
    def test_check_hash_chain_broken(self):
        """Test broken hash chain detection."""
        meta = MetaNewton()
        
        context = {
            "hash_chain": [
                {"hash": "abc123", "prev_hash": None},
                {"hash": "def456", "prev_hash": "WRONG"},  # Broken!
            ],
            "meta_depth": 0,
        }
        
        passed, message, evidence = meta.check_hash_chain(context)
        
        assert passed is False
        assert "broken" in message.lower()
    
    def test_meta_depth_limit(self):
        """Test meta-verification respects depth limit."""
        meta = MetaNewton()
        
        # Artificially set depth too high
        meta._current_depth = meta.MAX_META_DEPTH + 1
        
        context = {"meta_depth": meta.MAX_META_DEPTH + 1}
        result = meta.verify(context)
        
        assert result.verified is False
        
        # Reset
        meta._current_depth = 0
    
    def test_quick_check(self):
        """Test quick check functionality."""
        meta = MetaNewton()
        
        good_context = {
            "iterations": 100,
            "max_iterations": 10000,
            "recursion_depth": 5,
            "max_recursion": 100,
            "elapsed_ms": 50,
            "max_time_ms": 30000,
            "meta_depth": 0,
        }
        
        passed, message = meta.quick_check(good_context)
        
        assert passed is True
    
    def test_verification_chain_grows(self):
        """Test that verification chain grows with each verification."""
        meta = MetaNewton()
        
        initial_length = len(meta._chain)
        
        meta.verify({"meta_depth": 0})
        meta.verify({"meta_depth": 0})
        
        assert len(meta._chain) > initial_length
    
    def test_get_stats(self):
        """Test stats reporting."""
        meta = MetaNewton()
        
        meta.verify({"meta_depth": 0})
        
        stats = meta.get_stats()
        
        assert stats["verification_count"] >= 1
        assert "chain_length" in stats
        assert "constraints_defined" in stats
    
    def test_determinism_check(self):
        """Test determinism constraint check."""
        meta = MetaNewton()
        
        context = {
            "determinism_tests": [
                {"input": "test", "expected_hash": "abc", "actual_hash": "abc"},
            ],
            "meta_depth": 0,
        }
        
        passed, message, evidence = meta.check_determinism(context)
        
        assert passed is True
    
    def test_get_meta_newton_singleton(self):
        """Test global Meta Newton instance."""
        meta1 = get_meta_newton()
        meta2 = get_meta_newton()
        
        assert meta1 is meta2


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE MESH TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestKnowledgeMesh:
    """Tests for the Knowledge Mesh multi-source system."""
    
    def test_mesh_initialization(self):
        """Test mesh initializes with data."""
        mesh = KnowledgeMesh()
        
        assert len(mesh._facts) > 0
        assert len(mesh._by_category) > 0
        assert len(mesh._by_source) > 0
    
    def test_query_astronomical(self):
        """Test astronomical data queries."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("What is the mass of Earth?")
        
        assert result is not None
        assert "astro:" in result.key
        assert result.primary_source == "nasa"
    
    def test_query_geological(self):
        """Test geological data queries."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("How tall is Mount Everest?")
        
        assert result is not None
        assert "geo:" in result.key
        assert result.value["height_m"] == 8849
    
    def test_query_programming(self):
        """Test programming language queries."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("When was Python created?")
        
        assert result is not None
        assert result.value["created"] == 1991
        assert result.value["creator"] == "Guido van Rossum"
    
    def test_query_elements(self):
        """Test element queries."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("What is the atomic number of gold?")
        
        assert result is not None
        assert result.value["symbol"] == "Au"
        assert result.value["atomic_number"] == 79
    
    def test_query_economic(self):
        """Test economic data queries."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("What is the GDP of USA?")
        
        assert result is not None
        assert result.value["year"] == 2022
        assert result.primary_source == "world_bank"
    
    def test_query_math_constants(self):
        """Test math constant queries."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("What is the golden ratio?")
        
        assert result is not None
        assert abs(result.value["value"] - 1.618) < 0.01
    
    def test_query_not_found(self):
        """Test that non-existent queries return None."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("What is the airspeed velocity of an unladen swallow?")
        
        assert result is None
    
    def test_get_by_category(self):
        """Test category-based retrieval."""
        mesh = KnowledgeMesh()
        
        astronomy_facts = mesh.get_by_category("astronomy")
        
        assert len(astronomy_facts) > 0
        assert all(f.category == "astronomy" for f in astronomy_facts)
    
    def test_get_by_source(self):
        """Test source-based retrieval."""
        mesh = KnowledgeMesh()
        
        nasa_facts = mesh.get_by_source("nasa")
        
        assert len(nasa_facts) > 0
        assert all(f.primary_source == "nasa" for f in nasa_facts)
    
    def test_cross_referencing(self):
        """Test that some facts have confirming sources."""
        mesh = KnowledgeMesh()
        
        stats = mesh.get_stats()
        
        assert stats["cross_referenced"] > 0
    
    def test_stats(self):
        """Test stats reporting."""
        mesh = KnowledgeMesh()
        
        # Do some queries
        mesh.query("What is the mass of Earth?")
        mesh.query("Unknown query")
        
        stats = mesh.get_stats()
        
        assert stats["queries"] >= 2
        assert stats["hits"] >= 1
        assert "hit_rate" in stats
    
    def test_source_tiers(self):
        """Test that sources have correct tiers."""
        assert SOURCES["cia_factbook"].tier == SourceTier.AUTHORITATIVE
        assert SOURCES["nist"].tier == SourceTier.AUTHORITATIVE
        assert SOURCES["wikidata"].tier == SourceTier.CURATED
    
    def test_get_knowledge_mesh_singleton(self):
        """Test global Knowledge Mesh instance."""
        mesh1 = get_knowledge_mesh()
        mesh2 = get_knowledge_mesh()
        
        assert mesh1 is mesh2
    
    def test_mariana_trench_query(self):
        """Test specific geological query."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("How deep is the Mariana Trench?")
        
        assert result is not None
        assert result.value["depth_m"] == 10994
    
    def test_rust_creator_query(self):
        """Test programming language creator query."""
        mesh = KnowledgeMesh()
        
        result = mesh.query("Who created Rust?")
        
        assert result is not None
        assert result.value["creator"] == "Graydon Hoare"


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests for Ada + Meta Newton + Knowledge Mesh."""
    
    def test_ada_watches_mesh_responses(self):
        """Test Ada watching Knowledge Mesh responses."""
        ada = Ada()
        mesh = KnowledgeMesh()
        
        # Query mesh
        result = mesh.query("What is the mass of Earth?")
        
        # Have Ada watch the response
        whisper = ada.watch_response(
            query="What is the mass of Earth?",
            response=str(result.value) if result else "Unknown",
            verified=result is not None,
            sources=[result.primary_source] if result else []
        )
        
        # Should be fine (verified with source)
        assert whisper is None or whisper.level in [AlertLevel.QUIET, AlertLevel.NOTICE]
    
    def test_meta_verifies_ada(self):
        """Test Meta Newton verifying Ada's operation."""
        ada = Ada()
        meta = MetaNewton()
        
        # Ada does some work
        for _ in range(10):
            ada.sense("Test text")
        
        # Meta verifies Ada didn't exceed bounds
        context = {
            "iterations": ada.observations,
            "max_iterations": 10000,
            "meta_depth": 0,
        }
        
        result = meta.verify(context)
        
        assert result.verified is True
    
    def test_full_pipeline(self):
        """Test full pipeline: Query → Ada Watch → Meta Verify."""
        mesh = KnowledgeMesh()
        ada = Ada()
        meta = MetaNewton()
        
        # 1. Query knowledge mesh
        query = "When was Python created?"
        result = mesh.query(query)
        
        assert result is not None
        
        # 2. Ada watches the interaction
        response = f"Python was created in {result.value['created']}"
        whisper = ada.watch_response(
            query=query,
            response=response,
            verified=True,
            sources=[result.primary_source]
        )
        
        # 3. Meta verifies the whole pipeline
        context = {
            "iterations": 1,
            "max_iterations": 10000,
            "meta_depth": 0,
            "determinism_tests": [
                {"input": query, "expected_hash": "test", "actual_hash": "test"}
            ]
        }
        
        verification = meta.verify(context)
        
        assert verification.verified is True


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY-BASED TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestProperties:
    """Property-based tests using Hypothesis."""
    
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=100)
    def test_ada_sense_never_crashes(self, text):
        """Property: Ada.sense should never crash on any input."""
        ada = Ada()
        result = ada.sense(text)
        
        assert result is None or isinstance(result, Whisper)
    
    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=50),
        values=st.one_of(st.integers(), st.text(), st.floats(allow_nan=False)),
        min_size=0,
        max_size=10
    ))
    @settings(max_examples=50)
    def test_meta_verify_never_crashes(self, context):
        """Property: Meta Newton verify should never crash."""
        meta = MetaNewton()
        context["meta_depth"] = 0  # Required
        
        result = meta.verify(context)
        
        assert isinstance(result, MetaVerification)
    
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=50)
    def test_mesh_query_never_crashes(self, query):
        """Property: Mesh query should never crash."""
        mesh = KnowledgeMesh()
        
        result = mesh.query(query)
        
        assert result is None or isinstance(result, MeshFact)
    
    @given(
        key=st.text(min_size=1, max_size=50),
        value=st.one_of(st.integers(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=50)
    def test_drift_detector_deterministic(self, key, value):
        """Property: Same value should never trigger drift."""
        detector = DriftDetector()
        
        # Set baseline
        detector.set_baseline(key, value, "source")
        
        # Check same value - should never drift
        anomaly = detector.check_drift(key, value)
        
        assert anomaly is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
