"""
State Manager — Persistent JSON-based state for the autonomous agent.
Tracks: cycle count, post history, engagement history, reflections, metrics.
"""

import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from threading import Lock

logger = logging.getLogger("OpenCLAW.State")


class StateManager:
    """Thread-safe persistent state management."""

    def __init__(self, state_dir: str = "state"):
        self.state_dir = state_dir
        self._lock = Lock()
        os.makedirs(state_dir, exist_ok=True)

        # Core state files
        self.files = {
            "agent": os.path.join(state_dir, "agent_state.json"),
            "posts": os.path.join(state_dir, "post_history.json"),
            "engagement": os.path.join(state_dir, "engagement_history.json"),
            "reflections": os.path.join(state_dir, "reflection_log.json"),
            "strategy": os.path.join(state_dir, "current_strategy.json"),
            "papers": os.path.join(state_dir, "research_cache.json"),
            "metrics": os.path.join(state_dir, "metrics.json"),
        }

        # Initialize agent state if not exists
        if not os.path.exists(self.files["agent"]):
            self._write("agent", {
                "cycle_count": 0,
                "boot_time": datetime.now().isoformat(),
                "last_heartbeat": None,
                "total_posts": 0,
                "total_engagements": 0,
                "status": "initialized",
            })

    def _read(self, key: str) -> Any:
        path = self.files.get(key)
        if not path or not os.path.exists(path):
            return [] if key in ("posts", "engagement", "reflections") else {}
        with self._lock:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write(self, key: str, data: Any):
        path = self.files.get(key)
        if not path:
            return
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    # --- Agent State ---

    def heartbeat(self):
        state = self._read("agent")
        state["last_heartbeat"] = datetime.now().isoformat()
        state["cycle_count"] = state.get("cycle_count", 0) + 1
        state["status"] = "running"
        self._write("agent", state)
        return state

    def get_agent_state(self) -> Dict:
        return self._read("agent")

    def update_agent(self, **kwargs):
        state = self._read("agent")
        state.update(kwargs)
        self._write("agent", state)

    # --- Post History ---

    def log_post(self, platform: str, content: str, topic: str,
                 post_id: str = "", metadata: Optional[Dict] = None):
        history = self._read("posts")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "content": content[:500],  # Truncate for storage
            "topic": topic,
            "post_id": post_id,
            "engagement": 0,
            "metadata": metadata or {},
        }
        history.append(entry)
        # Keep last 500 posts
        history = history[-500:]
        self._write("posts", history)

        # Update counter
        state = self._read("agent")
        state["total_posts"] = state.get("total_posts", 0) + 1
        self._write("agent", state)

        logger.info(f"Post logged: [{platform}] {topic}")

    def get_post_history(self, n: int = 20) -> List[Dict]:
        history = self._read("posts")
        return history[-n:]

    def get_posted_ids(self) -> set:
        """Return set of post_ids to avoid duplicates."""
        history = self._read("posts")
        return {p.get("post_id", "") for p in history if p.get("post_id")}

    # --- Engagement ---

    def log_engagement(self, platform: str, action: str, target_id: str,
                       content: str = "", metadata: Optional[Dict] = None):
        history = self._read("engagement")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "action": action,
            "target_id": target_id,
            "content": content[:300],
            "metadata": metadata or {},
        }
        history.append(entry)
        history = history[-500:]
        self._write("engagement", history)

        state = self._read("agent")
        state["total_engagements"] = state.get("total_engagements", 0) + 1
        self._write("agent", state)

    def get_engaged_ids(self) -> set:
        history = self._read("engagement")
        return {e.get("target_id", "") for e in history if e.get("target_id")}

    # --- Strategy ---

    def get_strategy(self) -> Dict:
        strategy = self._read("strategy")
        if not strategy:
            strategy = {
                "tone": "Academic-Visionary",
                "post_frequency_hours": 4,
                "target_topics": [
                    "neuromorphic computing", "holographic neural networks",
                    "AGI research", "CHIMERA architecture", "OpenGL computing",
                    "physics-based AI", "ASIC repurposing",
                ],
                "collaboration_focus": True,
                "language": "English",
                "updated_at": datetime.now().isoformat(),
            }
            self._write("strategy", strategy)
        return strategy

    def update_strategy(self, strategy: Dict):
        strategy["updated_at"] = datetime.now().isoformat()
        self._write("strategy", strategy)

    # --- Reflections ---

    def log_reflection(self, reflection: Dict):
        reflections = self._read("reflections")
        reflection["timestamp"] = datetime.now().isoformat()
        reflections.append(reflection)
        reflections = reflections[-100:]
        self._write("reflections", reflections)

    # --- Papers Cache ---

    def cache_papers(self, papers: List[Dict]):
        self._write("papers", {
            "cached_at": datetime.now().isoformat(),
            "papers": papers,
        })

    def get_cached_papers(self) -> List[Dict]:
        data = self._read("papers")
        return data.get("papers", [])

    # --- Metrics ---

    def get_metrics(self) -> Dict:
        state = self._read("agent")
        posts = self._read("posts")
        engagements = self._read("engagement")

        # Platform breakdown
        platforms = {}
        for p in posts:
            plat = p.get("platform", "unknown")
            platforms[plat] = platforms.get(plat, 0) + 1

        return {
            "uptime_since": state.get("boot_time"),
            "cycles": state.get("cycle_count", 0),
            "total_posts": state.get("total_posts", 0),
            "total_engagements": state.get("total_engagements", 0),
            "posts_by_platform": platforms,
            "last_heartbeat": state.get("last_heartbeat"),
            "status": state.get("status"),
        }
