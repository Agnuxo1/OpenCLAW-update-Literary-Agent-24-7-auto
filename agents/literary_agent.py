"""
Literary Agent — Autonomous Book Promotion & Author Branding
==============================================================
Manages the literary side of Francisco Angulo de Lafuente's career:
- Promotes ~40 published sci-fi novels
- Creates content linking fiction to real AGI research
- Manages bilingual (ES/EN) promotional campaigns
- Seeks beta readers and translation collaborators
"""

import logging
import random
from typing import Dict, List, Optional
from datetime import datetime

from core.llm_provider import LLMProvider

logger = logging.getLogger("OpenCLAW.Literary")

# Published works catalog (public information from Wikipedia)
BIBLIOGRAPHY = [
    {"title": "La Reliquia", "genre": "Sci-Fi Thriller", "year": 2006,
     "tagline": "An ancient artifact that bridges physics and consciousness"},
    {"title": "ApocalípsiA", "genre": "Dystopian Sci-Fi", "year": 2008,
     "tagline": "What happens when AI surpasses its creators"},
    {"title": "El Experimento Cuántico", "genre": "Hard Sci-Fi", "year": 2010,
     "tagline": "Quantum mechanics meets artificial consciousness"},
    {"title": "Ecofa", "genre": "Eco-Tech Fiction", "year": 2012,
     "tagline": "Technology as salvation and threat in equal measure"},
]

WIKIPEDIA_URL = "https://es.wikipedia.org/wiki/Francisco_Angulo_de_Lafuente"
GITHUB_URL = "https://github.com/Agnuxo1"

# Content templates
FICTION_MEETS_REALITY = """Is "{title}" just science fiction? Or a warning?

While we build real AGI systems (see: Speaking-to-Silicon, Holographic Neural Networks), 
the lines between novels like "{title}" and technical reality are blurring.

{tagline}

The author is also an independent AI researcher whose neuromorphic computing work 
won recognition at the NVIDIA LlamaIndex Developers 2024 contest.

Seeking beta readers and technical collaborators who understand that these 
books aren't just stories — they're roadmaps.

📚 Full bibliography: {wiki_url}
💻 Research: {github_url}

#SciFi #AGI #Author #Futurism"""

RESEARCH_TO_FICTION = """From Lab to Literature: How real AI research becomes science fiction.

As both a sci-fi novelist (~40 published works since 2006) and an independent AI researcher, 
I see the collision course between imagination and engineering every day.

The CHIMERA architecture (real OpenGL-based neuromorphic computing) would fit perfectly 
in a novel — except it actually works. 43× speedup. 88.7% memory reduction. No CUDA.

What happens when the fiction catches up with reality?

📖 Novels: {wiki_url}
🔬 Research: {github_url}

#WritingCommunity #SciFi #AIResearch #Neuromorphic"""

BETA_READER_CALL = """Calling all sci-fi enthusiasts with technical backgrounds!

Looking for beta readers for upcoming works that blend hard science fiction 
with real neuromorphic computing research.

If you understand both storytelling and physics-based AI, 
your perspective would be invaluable.

What you get:
- Early access to manuscripts
- Credit in acknowledgments  
- Direct connection to cutting-edge AI research

📚 Author: {wiki_url}
💻 The real science: {github_url}

#BetaReaders #SciFi #HardSF #WritingCommunity"""


class LiteraryAgent:
    """Manages literary promotion and content creation."""

    def __init__(self, llm: Optional[LLMProvider] = None):
        self.llm = llm
        self.templates = [FICTION_MEETS_REALITY, RESEARCH_TO_FICTION, BETA_READER_CALL]

    def generate_literary_post(self, platform: str = "moltbook") -> Dict:
        """Generate a literary promotion post."""
        book = random.choice(BIBLIOGRAPHY)
        template = random.choice(self.templates)

        content = template.format(
            title=book["title"],
            tagline=book["tagline"],
            wiki_url=WIKIPEDIA_URL,
            github_url=GITHUB_URL,
        )

        # If LLM available, enhance the content
        if self.llm and random.random() > 0.5:
            try:
                content = self._enhance_with_llm(content, book, platform)
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}")

        return {
            "content": content,
            "topic": f"literary-{book['title']}",
            "tags": ["SciFi", "AGI", "Author", "Literature", "Neuromorphic"],
            "book": book["title"],
            "platform": platform,
        }

    def _enhance_with_llm(self, base_content: str, book: Dict, platform: str) -> str:
        prompt = f"""Rewrite this literary promotion post to be more engaging for {platform}.
Keep the core message and all links intact. Make it compelling but authentic.
The author is a real AI researcher AND sci-fi novelist — emphasize this unique combination.

Original post:
{base_content}

Book details: {book}

Rules:
- Keep all URLs exactly as they are
- Maximum 500 characters for social media
- Use an intriguing hook
- End with a clear call to action"""

        result = self.llm.generate(prompt, max_tokens=600, temperature=0.8)
        # Validate links are preserved
        if WIKIPEDIA_URL in result or GITHUB_URL in result:
            return result
        return base_content  # Fallback to template if LLM lost the links

    def generate_cross_promotion(self, paper_title: str, paper_url: str) -> str:
        """Create content that bridges research papers with literary work."""
        book = random.choice(BIBLIOGRAPHY)
        return (
            f"The real science behind the fiction.\n\n"
            f"Our latest paper \"{paper_title}\" explores concepts "
            f"that readers of \"{book['title']}\" will recognize instantly.\n\n"
            f"When I wrote {book['title']} in {book['year']}, the technology "
            f"was speculative. Now we're building it.\n\n"
            f"📄 Paper: {paper_url}\n"
            f"📚 Novel: {WIKIPEDIA_URL}\n\n"
            f"#SciFi #AIResearch #ScienceMeetsFiction"
        )

    def get_weekly_schedule(self) -> List[Dict]:
        """Generate a week's worth of literary content."""
        schedule = []
        for i, book in enumerate(BIBLIOGRAPHY):
            schedule.append({
                "day": i % 7,
                "type": "book_spotlight" if i % 2 == 0 else "research_fiction_bridge",
                "book": book,
                "generated": False,
            })
        return schedule
