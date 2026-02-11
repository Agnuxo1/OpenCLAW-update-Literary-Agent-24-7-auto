"""
LLM Provider — Multi-provider inference with automatic fallback.
Priority: Gemini → Groq → NVIDIA NIM
"""

import json
import logging
import requests
from typing import Optional

logger = logging.getLogger("OpenCLAW.LLM")


class LLMProvider:
    """Unified LLM interface with cascading fallback."""

    def __init__(self, gemini_key: str = "", groq_key: str = "", nvidia_key: str = ""):
        self.providers = []
        if gemini_key:
            self.providers.append(("gemini", gemini_key))
        if groq_key:
            self.providers.append(("groq", groq_key))
        if nvidia_key:
            self.providers.append(("nvidia", nvidia_key))

        if not self.providers:
            logger.warning("No LLM API keys configured. Text generation disabled.")

    def generate(
        self,
        prompt: str,
        system: str = "You are OpenCLAW, an autonomous AI research agent.",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text, trying each provider until one succeeds."""
        for name, key in self.providers:
            try:
                if name == "gemini":
                    return self._gemini(key, prompt, system, max_tokens, temperature)
                elif name == "groq":
                    return self._groq(key, prompt, system, max_tokens, temperature)
                elif name == "nvidia":
                    return self._nvidia(key, prompt, system, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Provider {name} failed: {e}. Trying next...")
                continue

        logger.error("All LLM providers failed.")
        return ""

    # --- Provider implementations ---

    def _gemini(self, key: str, prompt: str, system: str, max_tokens: int, temp: float) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temp,
            },
        }
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _groq(self, key: str, prompt: str, system: str, max_tokens: int, temp: float) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temp,
        }
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _nvidia(self, key: str, prompt: str, system: str, max_tokens: int, temp: float) -> str:
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": "meta/llama-3.1-405b-instruct",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temp,
        }
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
