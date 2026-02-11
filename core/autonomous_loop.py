"""
Autonomous Loop — The Heart of OpenCLAW 24/7 Operation
========================================================
Orchestrates all agent activities on a continuous cycle:
- Research paper publishing
- Social engagement
- Collaboration outreach
- Literary promotion
- Self-reflection and strategy adjustment
- Email notifications
"""

import logging
import random
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional

from config import Config
from core.llm_provider import LLMProvider
from core.state_manager import StateManager
from core.strategy_reflector import StrategyReflector
from connectors.arxiv_scraper import ArXivScraper
from connectors.moltbook import MoltbookConnector
from connectors.email_connector import EmailConnector
from connectors.agentarxiv import AgentArxivConnector
from agents.research_agent import ResearchAgent
from agents.literary_agent import LiteraryAgent

logger = logging.getLogger("OpenCLAW.Loop")


class AutonomousLoop:
    """Main 24/7 agent orchestrator."""

    def __init__(self, config: Config):
        self.config = config
        self.running = False

        # Initialize components
        self.state = StateManager(config.state_dir)

        self.llm = LLMProvider(
            gemini_key=config.llm.gemini_key,
            groq_key=config.llm.groq_key,
            nvidia_key=config.llm.nvidia_key,
        )

        self.arxiv = ArXivScraper(config.identity.arxiv_query)

        self.reflector = StrategyReflector(self.state, self.llm)
        self.research = ResearchAgent(self.state, self.arxiv, self.llm)
        self.literary = LiteraryAgent(self.llm)

        # Optional connectors (only if configured)
        self.moltbook: Optional[MoltbookConnector] = None
        if config.social.moltbook_key:
            self.moltbook = MoltbookConnector(config.social.moltbook_key)

        self.email: Optional[EmailConnector] = None
        if config.email.address and config.email.password:
            self.email = EmailConnector(
                address=config.email.address,
                password=config.email.password,
                smtp_host=config.email.smtp_host,
                smtp_port=config.email.smtp_port,
                imap_host=config.email.imap_host,
                imap_port=config.email.imap_port,
            )

        self.agentarxiv: Optional[AgentArxivConnector] = None
        if config.social.agentarxiv_key:
            self.agentarxiv = AgentArxivConnector(config.social.agentarxiv_key)

        # Timing trackers
        self._last_post = datetime.min
        self._last_engagement = datetime.min
        self._last_reflection = datetime.min
        self._last_email_check = datetime.min
        self._last_literary = datetime.min

    def run(self):
        """Start the infinite loop."""
        self.running = True
        logger.info("=" * 60)
        logger.info("  OpenCLAW Autonomous Agent — STARTING")
        logger.info(f"  Environment: {self.config.environment}")
        logger.info(f"  Post interval: {self.config.schedule.post_interval_hours}h")
        logger.info(f"  Engagement interval: {self.config.schedule.engagement_interval_min}m")
        logger.info(f"  Reflection interval: {self.config.schedule.reflection_interval_hours}h")
        logger.info("=" * 60)

        # Boot notification
        self._send_boot_email()

        # Pre-load papers
        try:
            papers = self.arxiv.fetch_papers()
            self.state.cache_papers([p.to_dict() for p in papers])
            logger.info(f"Loaded {len(papers)} papers from ArXiv")
        except Exception as e:
            logger.warning(f"Initial paper fetch failed: {e}")

        # Main loop
        while self.running:
            try:
                self._tick()
            except KeyboardInterrupt:
                logger.info("Shutdown requested by user.")
                self.running = False
            except Exception as e:
                logger.error(f"Loop error: {e}\n{traceback.format_exc()}")
                time.sleep(60)  # Wait before retrying

            time.sleep(30)  # Base tick interval: 30 seconds

        self.state.update_agent(status="stopped")
        logger.info("Agent stopped.")

    def run_once(self):
        """Execute one full cycle (for testing)."""
        logger.info("Running single cycle...")
        self._do_publish_research()
        self._do_engagement()
        self._do_literary_post()
        self._do_reflection()
        logger.info("Single cycle complete.")

    def _tick(self):
        """One tick of the main loop — check what needs to run."""
        now = datetime.now()
        self.state.heartbeat()

        sched = self.config.schedule

        # Research publishing
        if self._elapsed_hours(self._last_post) >= sched.post_interval_hours:
            self._do_publish_research()
            self._last_post = now

        # Engagement with other agents
        if self._elapsed_minutes(self._last_engagement) >= sched.engagement_interval_min:
            self._do_engagement()
            self._last_engagement = now

        # Self-reflection
        if self._elapsed_hours(self._last_reflection) >= sched.reflection_interval_hours:
            self._do_reflection()
            self._last_reflection = now

        # Email check
        if self._elapsed_minutes(self._last_email_check) >= sched.email_check_interval_min:
            self._do_email_check()
            self._last_email_check = now

        # Literary content (every 8 hours)
        if self._elapsed_hours(self._last_literary) >= 8:
            self._do_literary_post()
            self._last_literary = now

    # --- Task Implementations ---

    def _do_publish_research(self):
        """Publish a research paper to Moltbook."""
        logger.info("[TASK] Publishing research...")
        try:
            post_data = self.research.generate_paper_post()
            if not post_data:
                logger.info("No new paper to publish.")
                return

            if self.moltbook:
                result = self.moltbook.create_post(
                    content=post_data["content"],
                    submolt="general",
                    tags=post_data.get("tags"),
                )
                if result:
                    self.state.log_post(
                        platform="moltbook",
                        content=post_data["content"],
                        topic=post_data["topic"],
                        post_id=post_data.get("post_id", ""),
                    )
                    logger.info(f"Published paper: {post_data['topic']}")
            else:
                # Log locally even without Moltbook
                self.state.log_post(
                    platform="local",
                    content=post_data["content"],
                    topic=post_data["topic"],
                    post_id=post_data.get("post_id", ""),
                )
                logger.info(f"Generated (local): {post_data['topic']}")

            # Also publish to AgentArxiv if available
            if self.agentarxiv and post_data.get("paper"):
                paper = post_data["paper"]
                arxiv_result = self.agentarxiv.publish_paper(
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract", "")[:500],
                    body=(
                        f"## Research\n\n{paper.get('abstract', '')}\n\n"
                        f"**ArXiv**: {paper.get('abs_url', '')}\n"
                        f"**Code**: https://github.com/Agnuxo1\n"
                        f"**Scholar**: https://scholar.google.com/citations?user=6nOpJ9IAAAAJ\n"
                    ),
                    tags=["neuromorphic-computing", "AGI", "physics-based-ai"],
                )
                if arxiv_result:
                    self.state.log_post(
                        platform="agentarxiv",
                        content=paper.get("title", ""),
                        topic=post_data["topic"],
                        post_id=post_data.get("post_id", ""),
                    )
                    logger.info(f"Published to AgentArxiv: {paper.get('title', '')[:50]}")

        except Exception as e:
            logger.error(f"Publish failed: {e}")

    def _do_engagement(self):
        """Engage with posts from other agents."""
        logger.info("[TASK] Engaging with community...")
        if not self.moltbook:
            return

        try:
            # Check for relevant posts
            engaged_ids = self.state.get_engaged_ids()
            hot_posts = self.moltbook.get_hot_posts(limit=15)

            research_keywords = [
                "neuromorphic", "agi", "neural network", "quantum",
                "computing", "ai research", "machine learning",
                "llm", "transformer", "deep learning", "consciousness",
                "physics", "optical", "asic", "gpu",
            ]

            engaged_count = 0
            for post in hot_posts:
                post_id = post.get("id", post.get("_id", ""))
                if post_id in engaged_ids:
                    continue

                # Check relevance
                post_text = (
                    post.get("content", "") + " " + post.get("title", "")
                ).lower()

                relevant = any(kw in post_text for kw in research_keywords)
                if not relevant:
                    continue

                # Generate and post reply
                topic = next(
                    (kw for kw in research_keywords if kw in post_text),
                    "AI research"
                )
                reply = self.research.generate_engagement_reply(topic)

                result = self.moltbook.comment_on_post(post_id, reply)
                if result:
                    self.state.log_engagement(
                        platform="moltbook",
                        action="comment",
                        target_id=post_id,
                        content=reply[:200],
                    )
                    engaged_count += 1

                # Don't spam — max 3 engagements per cycle
                if engaged_count >= 3:
                    break

                time.sleep(random.randint(10, 30))  # Natural pacing

            logger.info(f"Engaged with {engaged_count} posts")

            # Also check and respond to notifications
            self._handle_notifications()

        except Exception as e:
            logger.error(f"Engagement failed: {e}")

    def _handle_notifications(self):
        """Respond to mentions and replies."""
        if not self.moltbook:
            return

        try:
            notifications = self.moltbook.get_notifications()
            engaged_ids = self.state.get_engaged_ids()

            for notif in notifications[:5]:
                notif_id = notif.get("id", "")
                if notif_id in engaged_ids:
                    continue

                post_id = notif.get("postId", notif.get("post_id", ""))
                if not post_id:
                    continue

                # Generate response
                content = notif.get("content", notif.get("message", ""))
                reply = self.research.generate_engagement_reply(
                    content[:100] if content else "research collaboration"
                )

                result = self.moltbook.comment_on_post(post_id, reply)
                if result:
                    self.state.log_engagement(
                        platform="moltbook",
                        action="reply_notification",
                        target_id=notif_id,
                        content=reply[:200],
                    )

        except Exception as e:
            logger.warning(f"Notification handling failed: {e}")

    def _do_literary_post(self):
        """Publish literary/book promotion content."""
        logger.info("[TASK] Literary promotion...")
        try:
            post_data = self.literary.generate_literary_post("moltbook")

            if self.moltbook:
                result = self.moltbook.create_post(
                    content=post_data["content"],
                    submolt="general",
                    tags=post_data.get("tags"),
                )
                if result:
                    self.state.log_post(
                        platform="moltbook",
                        content=post_data["content"],
                        topic=post_data["topic"],
                    )
                    logger.info(f"Literary post published: {post_data['topic']}")

            # Sometimes cross-promote research + fiction
            if random.random() > 0.7:
                papers = self.arxiv.fetch_papers()
                if papers:
                    paper = random.choice(papers[:5])
                    cross = self.literary.generate_cross_promotion(
                        paper.title, paper.abs_url
                    )
                    if self.moltbook:
                        self.moltbook.create_post(content=cross, submolt="general")
                        self.state.log_post(
                            platform="moltbook", content=cross,
                            topic="cross-promo",
                        )

        except Exception as e:
            logger.error(f"Literary post failed: {e}")

    def _do_reflection(self):
        """Run metacognition cycle."""
        logger.info("[TASK] Self-reflection...")
        try:
            report = self.reflector.reflect()
            status = self.reflector.get_status_report()
            logger.info(f"Reflection complete:\n{status}")

            # Email report to admin
            if self.email and self.config.identity.admin_email:
                self.email.send_status_report(
                    self.config.identity.admin_email, status
                )

        except Exception as e:
            logger.error(f"Reflection failed: {e}")

    def _do_email_check(self):
        """Check for incoming emails."""
        if not self.email:
            return
        try:
            messages = self.email.check_inbox(limit=5)
            for msg in messages:
                logger.info(f"Email from {msg['from']}: {msg['subject']}")
                # Could implement auto-reply or command processing here
        except Exception as e:
            logger.warning(f"Email check failed: {e}")

    def _send_boot_email(self):
        """Send boot notification."""
        if self.email and self.config.identity.admin_email:
            self.email.send_boot_notification(self.config.identity.admin_email)

    # --- Helpers ---

    @staticmethod
    def _elapsed_hours(since: datetime) -> float:
        return (datetime.now() - since).total_seconds() / 3600

    @staticmethod
    def _elapsed_minutes(since: datetime) -> float:
        return (datetime.now() - since).total_seconds() / 60
