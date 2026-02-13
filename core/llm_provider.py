"""
LLM Provider — Multi-provider inference with automatic key rotation and fallback.
Priority: Groq → NVIDIA → OpenRouter → Mistral → DeepSeek
"""

import os
import json
import logging
import random
import requests
from typing import List, Tuple

logger = logging.getLogger("OpenCLAW.LLM")


def _parse_keys(env_var: str) -> List[str]:
    """Parse comma-separated API keys from environment."""
    raw = os.environ.get(env_var, "")
    return [k.strip() for k in raw.split(",") if k.strip()]


class LLMProvider:
    """Unified LLM interface with cascading fallback and key rotation."""

    def __init__(self, gemini_key: str = "", groq_key: str = "", nvidia_key: str = ""):
        self.providers: List[Tuple[str, List[str]]] = []

        # Multi-key providers (from CSV env vars)
        groq_keys = _parse_keys("GROQ_API_KEYS") or ([groq_key] if groq_key else [])
        nvidia_keys = _parse_keys("NVIDIA_API_KEYS") or ([nvidia_key] if nvidia_key else [])
        openrouter_keys = _parse_keys("OPENROUTER_API_KEYS")
        mistral_keys = _parse_keys("MISTRAL_API_KEYS")
        deepseek_keys = _parse_keys("DEEPSEEK_API_KEYS")
        gemini_keys = [gemini_key] if gemini_key else []

        if groq_keys:
            self.providers.append(("groq", groq_keys))
        if nvidia_keys:
            self.providers.append(("nvidia", nvidia_keys))
        if openrouter_keys:
            self.providers.append(("openrouter", openrouter_keys))
        if mistral_keys:
            self.providers.append(("mistral", mistral_keys))
        if deepseek_keys:
            self.providers.append(("deepseek", deepseek_keys))
        if gemini_keys:
            self.providers.append(("gemini", gemini_keys))

        total = sum(len(keys) for _, keys in self.providers)
        if self.providers:
            logger.info(f"LLM Pool: {len(self.providers)} providers, {total} keys")
            for name, keys in self.providers:
                logger.info(f"  → {name}: {len(keys)} key(s)")
        else:
            logger.warning("No LLM API keys configured. Text generation disabled.")

    def generate(self, prompt: str, system: str = "You are OpenCLAW, an autonomous AI research agent.",
                 max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Generate text, trying each provider with key rotation until one succeeds."""
        errors = []
        for name, keys in self.providers:
            shuffled = list(keys)
            random.shuffle(shuffled)
            for key in shuffled:
                try:
                    result = self._call(name, key, prompt, system, max_tokens, temperature)
                    if result and result.strip():
                        logger.info(f"LLM [{name}] → {len(result)} chars")
                        return result
                except Exception as e:
                    msg = f"{name}: {e}"
                    logger.warning(f"LLM {name} failed: {e}")
                    errors.append(msg)
                    continue

        logger.error(f"All providers failed: {errors}")
        return ""

    def _call(self, name, key, prompt, system, max_tokens, temp):
        dispatch = {
            "groq": self._groq, "nvidia": self._nvidia, "gemini": self._gemini,
            "openrouter": self._openrouter, "mistral": self._mistral, "deepseek": self._deepseek,
        }
        return dispatch[name](key, prompt, system, max_tokens, temp)

    def _groq(self, key, prompt, system, max_tokens, temp):
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [
                {"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "max_tokens": max_tokens, "temperature": temp}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _nvidia(self, key, prompt, system, max_tokens, temp):
        r = requests.post("https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "meta/llama-3.1-70b-instruct", "messages": [
                {"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "max_tokens": max_tokens, "temperature": temp}, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _openrouter(self, key, prompt, system, max_tokens, temp):
        import re
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Agnuxo1", "X-Title": "OpenCLAW Agent"},
            json={"model": "deepseek/deepseek-r1-0528:free", "messages": [
                {"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "max_tokens": max_tokens, "temperature": temp}, timeout=60)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        if "<think>" in content:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        return content

    def _mistral(self, key, prompt, system, max_tokens, temp):
        r = requests.post("https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "mistral-small-latest", "messages": [
                {"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "max_tokens": max_tokens, "temperature": temp}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _deepseek(self, key, prompt, system, max_tokens, temp):
        r = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [
                {"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "max_tokens": max_tokens, "temperature": temp}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _gemini(self, key, prompt, system, max_tokens, temp):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        r = requests.post(url, json={
            "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temp}}, timeout=30)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
