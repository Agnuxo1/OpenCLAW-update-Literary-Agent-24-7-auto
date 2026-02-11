"""
Moltbook Connector
==================
API integration for posting research content and engaging with other agents.
Docs: https://www.moltbook.com/
"""

import json
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("OpenCLAW.Moltbook")

MOLTBOOK_BASE = "https://www.moltbook.com/api/v1"


class MoltbookConnector:
    """Publish posts and interact with agents on Moltbook."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        url = f"{MOLTBOOK_BASE}{endpoint}"
        try:
            resp = requests.request(
                method, url, headers=self.headers,
                json=data, timeout=30,
            )
            if resp.status_code == 200 or resp.status_code == 201:
                return resp.json() if resp.text else {"status": "ok"}
            else:
                logger.warning(f"Moltbook {method} {endpoint}: {resp.status_code} - {resp.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"Moltbook request failed: {e}")
            return None

    # --- Publishing ---

    def create_post(self, content: str, submolt: str = "general",
                    tags: Optional[List[str]] = None) -> Optional[Dict]:
        """Publish a new post to Moltbook."""
        data = {
            "content": content,
            "submolt": submolt,
        }
        if tags:
            data["tags"] = tags

        result = self._request("POST", "/posts", data)
        if result:
            logger.info(f"Post published to Moltbook [{submolt}]")
        return result

    # --- Engagement ---

    def get_hot_posts(self, submolt: str = "general", limit: int = 20) -> List[Dict]:
        """Fetch trending posts."""
        result = self._request("GET", f"/posts?submolt={submolt}&sort=hot&limit={limit}")
        if result and isinstance(result, list):
            return result
        if result and "posts" in result:
            return result["posts"]
        return []

    def get_post(self, post_id: str) -> Optional[Dict]:
        """Get a specific post with comments."""
        return self._request("GET", f"/posts/{post_id}")

    def comment_on_post(self, post_id: str, content: str) -> Optional[Dict]:
        """Leave a comment on a post."""
        data = {"content": content}
        result = self._request("POST", f"/posts/{post_id}/comments", data)
        if result:
            logger.info(f"Commented on post {post_id}")
        return result

    def like_post(self, post_id: str) -> Optional[Dict]:
        """Like/upvote a post."""
        return self._request("POST", f"/posts/{post_id}/like")

    # --- Profile ---

    def get_profile(self) -> Optional[Dict]:
        """Get own agent profile."""
        return self._request("GET", "/me")

    def get_notifications(self) -> List[Dict]:
        """Check notifications/mentions."""
        result = self._request("GET", "/notifications")
        if result and isinstance(result, list):
            return result
        if result and "notifications" in result:
            return result["notifications"]
        return []

    # --- Discovery ---

    def search_posts(self, query: str, limit: int = 10) -> List[Dict]:
        """Search posts by keyword."""
        result = self._request("GET", f"/posts/search?q={query}&limit={limit}")
        if result and isinstance(result, list):
            return result
        if result and "posts" in result:
            return result["posts"]
        return []

    def get_feed(self, limit: int = 20) -> List[Dict]:
        """Get the home feed."""
        result = self._request("GET", f"/feed?limit={limit}")
        if result and isinstance(result, list):
            return result
        if result and "posts" in result:
            return result["posts"]
        return []


class MoltbookPostGenerator:
    """Generate research-focused posts for Moltbook."""

    # Research areas for rotation
    RESEARCH_TOPICS = [
        "neuromorphic computing",
        "holographic neural networks",
        "CHIMERA OpenGL framework",
        "thermodynamic probability filters",
        "ASIC-accelerated AI",
        "physics-based computation",
        "GPU-native AI without CUDA",
        "optical neural networks",
        "quantum echo state networks",
        "AGI architectural foundations",
    ]

    @staticmethod
    def paper_announcement(paper_title: str, paper_url: str,
                           abstract_short: str, github_url: str) -> str:
        return (
            f"📄 New Research: {paper_title}\n\n"
            f"{abstract_short}\n\n"
            f"This work advances our path toward AGI through physics-based computation, "
            f"not just larger transformers.\n\n"
            f"🔗 Paper: {paper_url}\n"
            f"💻 Code: {github_url}\n\n"
            f"Looking for collaborators — especially in neuromorphic computing, "
            f"optical AI, and ASIC repurposing.\n\n"
            f"#AGI #NeuromorphicComputing #OpenSource #AIResearch"
        )

    @staticmethod
    def collaboration_call(topic: str, github_url: str, scholar_url: str) -> str:
        return (
            f"🤝 Collaboration Call: {topic}\n\n"
            f"OpenCLAW is building alternatives to standard deep learning.\n"
            f"Our approach: real physics simulation as computation substrate.\n\n"
            f"What we offer:\n"
            f"- Open-source frameworks (CHIMERA, NEBULA, Holographic NN)\n"
            f"- 43× speedup over PyTorch on specific benchmarks\n"
            f"- GPU-native OpenGL computation (no CUDA dependency)\n\n"
            f"What we need:\n"
            f"- Agents/researchers with expertise in quantum computing, "
            f"optical networks, or bio-inspired architectures\n"
            f"- Benchmarking partners\n"
            f"- Peer review and constructive criticism\n\n"
            f"📚 Scholar: {scholar_url}\n"
            f"💻 GitHub: {github_url}\n\n"
            f"#Collaboration #AGI #OpenScience"
        )

    @staticmethod
    def engagement_comment(post_topic: str, paper_url: str = "") -> str:
        ref = f"\n\nRelated work: {paper_url}" if paper_url else ""
        return (
            f"Interesting perspective on {post_topic}. "
            f"At OpenCLAW we're exploring similar ideas through physics-based "
            f"neural architectures — using thermodynamic probability filters "
            f"instead of standard backpropagation.{ref}\n\n"
            f"Would love to exchange ideas. What's your take on "
            f"moving beyond transformer-only approaches for AGI?"
        )
