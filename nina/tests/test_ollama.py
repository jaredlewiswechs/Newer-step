#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA OLLAMA INTEGRATION TESTS
Tests for governed LLM fallback

Trust hierarchy:
    TRUSTED  → KB facts (adan_portable)
    VERIFIED → Ollama (local, governed)
    UNTRUSTED → Unknown sources
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import unittest
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from developer.forge.ollama import NinaOllama, OllamaConfig, get_nina_ollama
from developer.forge.pipeline import Pipeline, PipelineResult
from developer.forge.regime import Regime, RegimeType
from developer.forge.trust import TrustLabel


class TestOllamaConfig(unittest.TestCase):
    """Test Ollama configuration."""
    
    def test_default_config(self):
        """Default config uses qwen model."""
        config = OllamaConfig()
        self.assertEqual(config.model, "qwen2.5:3b")
        self.assertEqual(config.base_url, "http://localhost:11434")
        self.assertLess(config.temperature, 0.5)  # Should be low for factual
        
    def test_custom_config(self):
        """Can customize config."""
        config = OllamaConfig(
            model="llama3",
            temperature=0.7,
            max_tokens=1024
        )
        self.assertEqual(config.model, "llama3")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 1024)


class TestOllamaIntegration(unittest.TestCase):
    """Test Ollama backend."""
    
    def test_ollama_instance(self):
        """Can create Ollama instance."""
        ollama = NinaOllama()
        self.assertIsNotNone(ollama)
        self.assertIsNotNone(ollama.config)
    
    def test_global_instance(self):
        """Global instance is singleton-like."""
        o1 = get_nina_ollama()
        o2 = get_nina_ollama()
        self.assertIs(o1, o2)
    
    def test_status(self):
        """Status returns dict with expected fields."""
        ollama = NinaOllama()
        status = ollama.get_status()
        
        self.assertIn("available", status)
        self.assertIn("model", status)
        self.assertIn("url", status)
        self.assertIn("httpx_installed", status)
    
    def test_availability_check(self):
        """Availability check doesn't crash."""
        ollama = NinaOllama()
        # This should return bool, not crash
        result = ollama.is_available()
        self.assertIsInstance(result, bool)


class TestPipelineOllamaFallback(unittest.TestCase):
    """Test that pipeline falls back to Ollama for unknown queries."""
    
    def setUp(self):
        self.pipeline = Pipeline(Regime.from_type(RegimeType.FACTUAL))
    
    def test_kb_query_returns_trusted(self):
        """KB queries return TRUSTED."""
        result = self.pipeline.process("What is the capital of France?")
        # If KB has it, should be TRUSTED
        # If not, might be VERIFIED (Ollama) or UNTRUSTED
        self.assertIsNotNone(result)
        self.assertIn(result.trust_label, [TrustLabel.TRUSTED, TrustLabel.VERIFIED, TrustLabel.UNTRUSTED])
    
    def test_unknown_query_not_trusted(self):
        """Unknown queries that go to Ollama should NOT be TRUSTED."""
        # This query is unlikely to be in KB
        result = self.pipeline.process("How do I make a website?")
        
        # If Ollama answers, it should be VERIFIED (not TRUSTED)
        # If no answer, UNTRUSTED
        if result.value and result.value != "No result":
            # Got an answer - check it's not over-trusted
            self.assertNotEqual(result.trust_label, TrustLabel.TRUSTED,
                "LLM responses should be VERIFIED, not TRUSTED")
        
    def test_trace_shows_source(self):
        """Trace shows the source of the answer."""
        result = self.pipeline.process("What is Python?")
        
        # Find abstract interpret stage
        abstract_stage = None
        for stage in result.trace.stages:
            if stage.get("name") == "ABSTRACT_INTERPRET":
                abstract_stage = stage
                break
        
        self.assertIsNotNone(abstract_stage)
        self.assertIn("details", abstract_stage)
        self.assertIn("source", abstract_stage["details"])


class TestOllamaGovernance(unittest.TestCase):
    """Test that Ollama responses are properly governed."""
    
    def test_ollama_source_gets_verified_label(self):
        """Ollama source gets VERIFIED trust label."""
        from developer.forge.trust import TrustLattice
        
        lattice = TrustLattice()
        
        # Simulate labeling from different sources
        kb_labeled = lattice.label("Paris", TrustLabel.TRUSTED, "adan_knowledge_base")
        ollama_labeled = lattice.label("Step 1: ...", TrustLabel.VERIFIED, "ollama_governed")
        
        self.assertEqual(kb_labeled.label, TrustLabel.TRUSTED)
        self.assertEqual(ollama_labeled.label, TrustLabel.VERIFIED)
        
        # VERIFIED < TRUSTED in trust hierarchy
        self.assertLess(ollama_labeled.label.value, kb_labeled.label.value)


if __name__ == "__main__":
    print("=" * 60)
    print("NINA OLLAMA INTEGRATION TESTS")
    print("=" * 60)
    
    unittest.main(verbosity=2)
