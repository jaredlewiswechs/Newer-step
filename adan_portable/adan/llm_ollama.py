#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
OLLAMA LLM BACKEND
Free, local LLM integration for Newton Agent
═══════════════════════════════════════════════════════════════════════════════

Supports any Ollama model: llama3, mistral, codellama, phi, etc.
Run `ollama pull llama3` to download a model first.
"""

import json
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


@dataclass
class OllamaConfig:
    """Configuration for Ollama backend."""
    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = (
        "You are Newton Agent, a self-verifying AI assistant created by Ada Computing Company. "
        "You prioritize accuracy over helpfulness. If you're uncertain about something, say so clearly. "
        "Keep responses concise and factual. Do not provide medical, legal, or financial advice."
    )
    timeout: float = 60.0


class OllamaBackend:
    """
    Ollama LLM backend for Newton Agent.
    
    Usage:
        backend = OllamaBackend(OllamaConfig(model="llama3"))
        response = backend.generate("What is Python?", context=[...])
    """
    
    def __init__(self, config: OllamaConfig = None):
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for Ollama backend. Run: pip install httpx")
        
        self.config = config or OllamaConfig()
        self.client = httpx.Client(timeout=self.config.timeout)
        
    def _build_messages(self, prompt: str, context: List[Dict] = None) -> List[Dict]:
        """Build message list for chat completion."""
        messages = [{"role": "system", "content": self.config.system_prompt}]
        
        # Add conversation context
        if context:
            for turn in context[-10:]:  # Last 10 turns
                role = turn.get("role", "user")
                if role == "system":
                    continue  # Skip system messages from context
                messages.append({
                    "role": role,
                    "content": turn.get("content", "")
                })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def generate(self, prompt: str, context: List[Dict] = None) -> str:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: The user's message
            context: Previous conversation turns
            
        Returns:
            Generated response text
        """
        messages = self._build_messages(prompt, context)
        
        try:
            response = self.client.post(
                f"{self.config.base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
            
        except httpx.ConnectError:
            return (
                "I couldn't connect to the Ollama server. "
                "Please make sure Ollama is running (`ollama serve`) and try again."
            )
        except httpx.HTTPStatusError as e:
            return f"Ollama error: {e.response.status_code}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_stream(self, prompt: str, context: List[Dict] = None) -> Generator[str, None, None]:
        """
        Stream a response using Ollama.
        
        Yields:
            Response chunks as they're generated
        """
        messages = self._build_messages(prompt, context)
        
        try:
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
                            
        except httpx.ConnectError:
            yield "Error: Ollama server not running. Start with `ollama serve`."
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = self.client.get(f"{self.config.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = self.client.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except:
            return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            response = self.client.post(
                f"{self.config.base_url}/api/pull",
                json={"name": model},
                timeout=300.0  # 5 min for download
            )
            return response.status_code == 200
        except:
            return False


def create_ollama_generator(config: OllamaConfig = None):
    """
    Create a response generator function for NewtonAgent.
    
    Usage:
        from adan import NewtonAgent
        from adan.llm_ollama import create_ollama_generator, OllamaConfig
        
        agent = NewtonAgent(
            response_generator=create_ollama_generator(OllamaConfig(model="llama3"))
        )
    """
    backend = OllamaBackend(config)
    
    def generator(prompt: str, context: List[Dict]) -> str:
        return backend.generate(prompt, context)
    
    return generator


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("OLLAMA BACKEND TEST")
    print("=" * 60)
    
    backend = OllamaBackend()
    
    if not backend.is_available():
        print("\n❌ Ollama server not running!")
        print("   Start it with: ollama serve")
        print("   Then pull a model: ollama pull llama3")
        exit(1)
    
    print(f"\n✓ Ollama server running at {backend.config.base_url}")
    
    models = backend.list_models()
    print(f"✓ Available models: {', '.join(models) if models else 'None'}")
    
    if not models:
        print("\n⚠️  No models found. Pull one with: ollama pull llama3")
        exit(1)
    
    print(f"\n🤖 Testing with model: {backend.config.model}")
    print("-" * 60)
    
    response = backend.generate("What is 2 + 2? Answer briefly.")
    print(f"Response: {response}")
