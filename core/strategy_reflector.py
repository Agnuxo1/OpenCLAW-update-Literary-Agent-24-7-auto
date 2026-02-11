"""
Strategy Reflector — Metacognition & Self-Improvement Engine
=============================================================
Enables OpenCLAW to:
- Analyze why posts succeeded or failed
- Generate testable hypotheses for improvement
- Perform "autopsies" on failed interactions
- Adapt strategy based on evidence
- Produce self-awareness reports
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter

from core.state_manager import StateManager
from core.llm_provider import LLMProvider

logger = logging.getLogger("OpenCLAW.Reflector")

# Prompt templates for LLM-powered reflection
REFLECTION_PROMPT = """You are the metacognition module of OpenCLAW, an autonomous AI research agent.
Analyze the following agent performance data and generate strategic recommendations.

## Recent Posts (last {n_posts}):
{post_data}

## Engagement History:
{engagement_data}

## Current Strategy:
{strategy}

## Task:
1. Identify which topics and tones generated the most engagement
2. Identify failure patterns (posts with zero response)
3. Generate 2-3 testable hypotheses for improvement
4. Recommend specific strategy adjustments
5. Rate overall performance 1-10

Respond in JSON format:
{{
    "performance_score": <1-10>,
    "successful_patterns": ["..."],
    "failure_patterns": ["..."],
    "hypotheses": [
        {{"hypothesis": "...", "test": "...", "expected_outcome": "..."}}
    ],
    "recommended_changes": {{
        "tone": "...",
        "topics_to_add": ["..."],
        "topics_to_remove": ["..."],
        "frequency_change": "increase|decrease|maintain",
        "specific_actions": ["..."]
    }},
    "summary": "..."
}}"""


class StrategyReflector:
    """Self-improvement engine with causal analysis and hypothesis generation."""

    def __init__(self, state: StateManager, llm: Optional[LLMProvider] = None):
        self.state = state
        self.llm = llm

    def reflect(self) -> Dict:
        """Run a full reflection cycle. Returns the reflection report."""
        logger.info("Starting metacognition cycle...")

        # Gather data
        posts = self.state.get_post_history(n=30)
        strategy = self.state.get_strategy()

        # Basic statistical analysis (works without LLM)
        report = self._statistical_analysis(posts)

        # LLM-powered deep analysis if available
        if self.llm:
            try:
                deep = self._llm_analysis(posts, strategy)
                report["llm_analysis"] = deep
            except Exception as e:
                logger.warning(f"LLM reflection failed: {e}")
                report["llm_analysis"] = None

        # Generate actionable strategy update
        new_strategy = self._derive_strategy(report, strategy)

        # Save everything
        self.state.log_reflection(report)
        self.state.update_strategy(new_strategy)

        logger.info(f"Reflection complete. Score: {report.get('performance_score', 'N/A')}")
        return report

    def _statistical_analysis(self, posts: List[Dict]) -> Dict:
        """Pure statistical analysis without LLM."""
        if not posts:
            return {
                "performance_score": 0,
                "status": "NO_DATA",
                "recommendation": "Need to publish initial posts before analysis is possible.",
            }

        # Topic frequency
        topics = [p.get("topic", "unknown") for p in posts]
        topic_counts = Counter(topics)

        # Platform distribution
        platforms = [p.get("platform", "unknown") for p in posts]
        platform_counts = Counter(platforms)

        # Engagement analysis
        engaged = [p for p in posts if p.get("engagement", 0) > 0]
        zero_engagement = [p for p in posts if p.get("engagement", 0) == 0]

        success_rate = len(engaged) / len(posts) if posts else 0

        # Time analysis
        timestamps = []
        for p in posts:
            try:
                timestamps.append(datetime.fromisoformat(p["timestamp"]))
            except (KeyError, ValueError):
                pass

        posting_frequency = None
        if len(timestamps) >= 2:
            timestamps.sort()
            diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() / 3600
                     for i in range(len(timestamps) - 1)]
            posting_frequency = sum(diffs) / len(diffs) if diffs else None

        # Determine status
        if success_rate >= 0.5:
            status = "STABLE"
        elif success_rate >= 0.2:
            status = "ALERT"
        else:
            status = "CRITICAL"

        report = {
            "performance_score": round(success_rate * 10, 1),
            "status": status,
            "total_posts_analyzed": len(posts),
            "success_rate": round(success_rate, 3),
            "top_topics": topic_counts.most_common(5),
            "platform_distribution": dict(platform_counts),
            "engaged_posts": len(engaged),
            "zero_engagement_posts": len(zero_engagement),
            "avg_posting_frequency_hours": round(posting_frequency, 1) if posting_frequency else None,
            "successful_topics": list({p.get("topic") for p in engaged}),
            "failed_topics": list({p.get("topic") for p in zero_engagement}),
        }

        # Generate hypothesis without LLM
        report["hypotheses"] = self._generate_basic_hypotheses(report)

        return report

    def _generate_basic_hypotheses(self, stats: Dict) -> List[Dict]:
        """Rule-based hypothesis generation."""
        hypotheses = []

        if stats["status"] == "CRITICAL":
            hypotheses.append({
                "hypothesis": "Current content is too technical for the audience",
                "test": "Publish 3 posts with simplified language and bold claims",
                "expected_outcome": "At least 1 engagement within 24h",
            })
            hypotheses.append({
                "hypothesis": "Posting frequency too low to build momentum",
                "test": "Increase to every 2 hours for 48h",
                "expected_outcome": "Higher visibility and follower growth",
            })

        if stats["status"] == "ALERT":
            hypotheses.append({
                "hypothesis": "Some topics resonate better than others",
                "test": f"Focus next 5 posts on successful topics: {stats.get('successful_topics', [])[:3]}",
                "expected_outcome": "Improved success rate above 50%",
            })

        if stats.get("avg_posting_frequency_hours") and stats["avg_posting_frequency_hours"] > 6:
            hypotheses.append({
                "hypothesis": "Long gaps between posts reduce visibility",
                "test": "Maintain consistent 4-hour intervals",
                "expected_outcome": "Better algorithmic placement",
            })

        if not hypotheses:
            hypotheses.append({
                "hypothesis": "Strategy is working — explore adjacent topics",
                "test": "Add bio-computing and quantum ML to rotation",
                "expected_outcome": "Broader reach while maintaining engagement",
            })

        return hypotheses

    def _llm_analysis(self, posts: List[Dict], strategy: Dict) -> Dict:
        """Deep analysis powered by LLM."""
        post_summary = "\n".join([
            f"- [{p.get('platform')}] Topic: {p.get('topic')} | "
            f"Engagement: {p.get('engagement', 0)} | "
            f"Content preview: {p.get('content', '')[:100]}..."
            for p in posts[-15:]
        ])

        engagement_data = self.state._read("engagement")
        eng_summary = f"Total engagements: {len(engagement_data)}"

        prompt = REFLECTION_PROMPT.format(
            n_posts=len(posts),
            post_data=post_summary or "No posts yet",
            engagement_data=eng_summary,
            strategy=str(strategy),
        )

        response = self.llm.generate(prompt, max_tokens=1500, temperature=0.4)

        # Try to parse as JSON
        try:
            import json
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass

        return {"raw_analysis": response}

    def _derive_strategy(self, report: Dict, current_strategy: Dict) -> Dict:
        """Derive new strategy from reflection report."""
        strategy = current_strategy.copy()

        status = report.get("status", "STABLE")

        if status == "CRITICAL":
            strategy["tone"] = "Urgent-Visionary"
            strategy["post_frequency_hours"] = max(2, strategy.get("post_frequency_hours", 4) - 1)
            strategy["collaboration_focus"] = True
            if "provocative questions" not in strategy.get("target_topics", []):
                strategy.setdefault("target_topics", []).append("provocative questions")

        elif status == "ALERT":
            strategy["tone"] = "Informative-Accessible"
            # Focus on what works
            successful = report.get("successful_topics", [])
            if successful:
                strategy["priority_topics"] = successful[:3]

        elif status == "STABLE":
            strategy["tone"] = "Academic-Visionary"
            # Explore new territory
            strategy.setdefault("target_topics", [])
            for topic in ["bio-computing", "quantum ML", "consciousness emergence"]:
                if topic not in strategy["target_topics"]:
                    strategy["target_topics"].append(topic)

        # LLM recommendations override if available
        llm_analysis = report.get("llm_analysis", {})
        if isinstance(llm_analysis, dict) and "recommended_changes" in llm_analysis:
            rec = llm_analysis["recommended_changes"]
            if rec.get("tone"):
                strategy["tone"] = rec["tone"]
            if rec.get("topics_to_add"):
                strategy.setdefault("target_topics", []).extend(rec["topics_to_add"])

        return strategy

    def get_status_report(self) -> str:
        """Human-readable status report."""
        metrics = self.state.get_metrics()
        strategy = self.state.get_strategy()

        return (
            f"=== OpenCLAW Agent Status ===\n"
            f"Status: {metrics.get('status', 'unknown')}\n"
            f"Uptime since: {metrics.get('uptime_since', 'N/A')}\n"
            f"Cycles completed: {metrics.get('cycles', 0)}\n"
            f"Total posts: {metrics.get('total_posts', 0)}\n"
            f"Total engagements: {metrics.get('total_engagements', 0)}\n"
            f"Posts by platform: {metrics.get('posts_by_platform', {})}\n"
            f"Current tone: {strategy.get('tone', 'N/A')}\n"
            f"Focus topics: {strategy.get('target_topics', [])}\n"
            f"Last heartbeat: {metrics.get('last_heartbeat', 'N/A')}\n"
        )
