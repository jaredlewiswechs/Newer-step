#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA OLLAMA INTEGRATION
Governed LLM fallback for queries KB can't answer

Ollama runs LOCALLY - we govern it. Trust level: VERIFIED (not TRUSTED)
Only used when KB returns no result. KB always takes precedence.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from typing import Optional, List, Dict, Generator
from dataclasses import dataclass

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class OllamaConfig:
    """Ollama configuration."""
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:3b"  # Default to qwen - fast and capable
    temperature: float = 0.3   # Lower temp for more factual responses
    max_tokens: int = 512      # Keep responses concise
    timeout: float = 60.0      # Increased timeout for slower responses
    
    # Nina-specific system prompt
    system_prompt: str = """You are Nina, a verified computation assistant.

IMPORTANT RULES:
1. Be concise and factual
2. If uncertain, say "I'm not certain, but..."
3. Never provide medical, legal, or financial advice
4. Prefer step-by-step explanations for how-to questions
5. You are a FALLBACK - the verified KB was checked first and had no answer

Keep responses under 200 words unless the question requires more detail."""


class NinaOllama:
    """
    Governed Ollama integration for Nina.
    
    This is a FALLBACK - KB always takes precedence.
    Trust level: VERIFIED (local, governed) not TRUSTED (authoritative).
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig(
            base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
            model=os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
        )
        self._client = None
        self._available = None
    
    @property
    def client(self):
        """Lazy init httpx client."""
        if self._client is None and HAS_HTTPX:
            self._client = httpx.Client(timeout=self.config.timeout)
        return self._client
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if not HAS_HTTPX:
            return False
        
        if self._available is not None:
            return self._available
        
        try:
            resp = self.client.get(f"{self.config.base_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check if our model (or base name) is available
                model_base = self.config.model.split(":")[0]
                self._available = any(model_base in m for m in models)
                return self._available
        except:
            pass
        
        self._available = False
        return False
    
    def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Generate a response using Ollama.
        
        Returns None if Ollama is not available.
        """
        if not self.is_available():
            return None
        
        messages = [{"role": "system", "content": self.config.system_prompt}]
        
        # Add context if provided
        if context:
            for turn in context[-6:]:  # Last 6 turns
                role = turn.get("role", "user")
                if role != "system":
                    messages.append({
                        "role": role,
                        "content": turn.get("content", "")
                    })
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            resp = self.client.post(
                f"{self.config.base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    }
                },
                timeout=self.config.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            print(f"[NINA] Ollama error: {e}")
            return None
    
    def generate_stream(self, prompt: str, context: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """Stream a response from Ollama."""
        if not self.is_available():
            yield "Ollama not available"
            return
        
        messages = [{"role": "system", "content": self.config.system_prompt}]
        if context:
            for turn in context[-6:]:
                role = turn.get("role", "user")
                if role != "system":
                    messages.append({"role": role, "content": turn.get("content", "")})
        messages.append({"role": "user", "content": prompt})
        
        try:
            import json
            with self.client.stream(
                "POST",
                f"{self.config.base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    }
                }
            ) as response:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
        except Exception as e:
            yield f"Error: {e}"
    
    def get_status(self) -> Dict:
        """Get Ollama status."""
        return {
            "available": self.is_available(),
            "model": self.config.model,
            "url": self.config.base_url,
            "httpx_installed": HAS_HTTPX
        }


# Global instance
_ollama: Optional[NinaOllama] = None

def get_nina_ollama() -> NinaOllama:
    """Get global Ollama instance."""
    global _ollama
    if _ollama is None:
        _ollama = NinaOllama()
    return _ollama


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("NINA OLLAMA TEST")
    print("=" * 60)
    
    ollama = NinaOllama()
    print(f"\nStatus: {ollama.get_status()}")
    
    if ollama.is_available():
        print("\n✓ Ollama is available!")
        
        test_prompts = [
            "How do I make a website?",
            "What is Python?",
            "Explain recursion in one sentence.",
        ]
        
        for prompt in test_prompts:
            print(f"\n❓ {prompt}")
            response = ollama.generate(prompt)
            if response:
                print(f"   → {response[:200]}...")
            else:
                print("   → No response")
    else:
        print("\n✗ Ollama not available. Run: ollama serve")
