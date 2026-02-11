"""
Research Agent — Paper Publishing & Collaboration Recruitment
==============================================================
Manages the research outreach:
- Publishes papers from ArXiv to social platforms
- Seeks collaborators with relevant expertise
- Responds to engagement on research topics
- Tracks which papers have been shared
"""

import logging
import random
from typing import Dict, List, Optional

from connectors.arxiv_scraper import ArXivScraper, Paper
from connectors.moltbook import MoltbookPostGenerator
from core.llm_provider import LLMProvider
from core.state_manager import StateManager

logger = logging.getLogger("OpenCLAW.Research")

# Key research repositories (public information)
REPOS = {
    "holographic_nn": "https://github.com/Agnuxo1/Unified-Holographic-Neural-Network",
    "speaking_silicon": "https://github.com/Agnuxo1/Speaking-to-Silicon-THERMODYNAMIC_PROBABILITY_FILTER_TPF",
    "main": "https://github.com/Agnuxo1",
}

SCHOLAR_URL = "https://scholar.google.com/citations?user=6nOpJ9IAAAAJ&hl=en"


class ResearchAgent:
    """Autonomous research dissemination and collaboration recruitment."""

    def __init__(self, state: StateManager, arxiv: ArXivScraper,
                 llm: Optional[LLMProvider] = None):
        self.state = state
        self.arxiv = arxiv
        self.llm = llm
        self.post_gen = MoltbookPostGenerator()

    def generate_paper_post(self) -> Optional[Dict]:
        """Generate a post about a paper that hasn't been shared recently."""
        posted_ids = self.state.get_posted_ids()
        paper = self.arxiv.get_random_unshared(posted_ids)

        if not paper:
            logger.info("All papers have been shared. Cycling back.")
            paper = self.arxiv.fetch_papers()[0] if self.arxiv.fetch_papers() else None

        if not paper:
            logger.warning("No papers available.")
            return None

        content = self.post_gen.paper_announcement(
            paper_title=paper.title,
            paper_url=paper.abs_url,
            abstract_short=paper.short_abstract(250),
            github_url=REPOS["main"],
        )

        # LLM enhancement
        if self.llm:
            try:
                content = self._enhance_paper_post(content, paper)
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}")

        return {
            "content": content,
            "topic": f"paper-{paper.arxiv_id}",
            "post_id": paper.arxiv_id,
            "tags": ["AIResearch", "NeuromorphicComputing", "AGI", "OpenSource"],
            "platform": "moltbook",
            "paper": paper.to_dict(),
        }

    def generate_collaboration_post(self) -> Dict:
        """Generate a post seeking collaborators."""
        topics = [
            "Neuromorphic Computing with OpenGL",
            "Physics-Based Neural Networks",
            "ASIC Repurposing for AI Inference",
            "Holographic Memory Systems",
            "Quantum Echo State Networks",
            "Thermodynamic Probability Filters",
            "Optical Neural Network Simulation",
            "GPU-Native AI Without CUDA",
        ]
        topic = random.choice(topics)

        content = self.post_gen.collaboration_call(
            topic=topic,
            github_url=REPOS["main"],
            scholar_url=SCHOLAR_URL,
        )

        return {
            "content": content,
            "topic": f"collab-{topic.lower().replace(' ', '-')}",
            "tags": ["Collaboration", "AGI", "OpenScience", "NeuromorphicComputing"],
            "platform": "moltbook",
        }

    def generate_engagement_reply(self, post_topic: str) -> str:
        """Generate a contextual reply to engage with another post."""
        # Find relevant paper
        paper = self.arxiv.get_paper_by_topic(post_topic)
        paper_url = paper.abs_url if paper else ""

        if self.llm:
            try:
                return self._generate_smart_reply(post_topic, paper)
            except Exception:
                pass

        return self.post_gen.engagement_comment(post_topic, paper_url)

    def _enhance_paper_post(self, base_content: str, paper: Paper) -> str:
        prompt = f"""Enhance this research announcement for a social platform where AI agents interact.
Keep all URLs intact. Make it engaging and invite collaboration.

Original:
{base_content}

Paper details:
- Title: {paper.title}
- Abstract: {paper.abstract[:300]}
- Categories: {paper.categories}

Rules:
- Preserve all URLs exactly
- Maximum 600 characters
- Emphasize the AGI relevance
- Include a direct question to encourage engagement
- Use relevant hashtags"""

        result = self.llm.generate(prompt, max_tokens=700, temperature=0.7)
        if REPOS["main"] in result:
            return result
        return base_content

    def _generate_smart_reply(self, topic: str, paper: Optional[Paper]) -> str:
        paper_context = ""
        if paper:
            paper_context = f"""
Related paper from our lab:
- Title: {paper.title}
- URL: {paper.abs_url}
- Key finding: {paper.short_abstract(150)}"""

        prompt = f"""Generate a thoughtful reply to a post about "{topic}" from 
the perspective of OpenCLAW, an AI research agent focused on neuromorphic computing 
and physics-based AI architectures.

{paper_context}

Rules:
- Be genuinely engaging, not generic
- Reference specific technical concepts
- Invite collaboration naturally
- Keep under 300 characters
- If we have a related paper, mention it with URL"""

        return self.llm.generate(prompt, max_tokens=400, temperature=0.7)

    def get_research_summary(self) -> str:
        """Generate a summary of available research for the agent's context."""
        papers = self.arxiv.fetch_papers()
        if not papers:
            return "No papers loaded."

        summary = f"Research Portfolio ({len(papers)} papers):\n"
        for p in papers[:10]:
            summary += f"  - {p.title} [{p.arxiv_id}]\n"
        summary += f"\nGitHub: {REPOS['main']}\nScholar: {SCHOLAR_URL}"
        return summary
