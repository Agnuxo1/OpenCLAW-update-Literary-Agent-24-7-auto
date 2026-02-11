"""
ArXiv Research Scraper
======================
Fetches real papers by Francisco A. de Lafuente from ArXiv API.
Provides paper data for social posting and collaboration outreach.
"""

import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("OpenCLAW.ArXiv")

ARXIV_API = "https://export.arxiv.org/api/query"


@dataclass
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    authors: List[str]
    published: str
    updated: str
    categories: List[str]
    pdf_url: str
    abs_url: str

    def short_abstract(self, max_len: int = 280) -> str:
        if len(self.abstract) <= max_len:
            return self.abstract
        return self.abstract[:max_len - 3].rsplit(" ", 1)[0] + "..."

    def to_dict(self) -> Dict:
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "published": self.published,
            "updated": self.updated,
            "categories": self.categories,
            "pdf_url": self.pdf_url,
            "abs_url": self.abs_url,
        }


class ArXivScraper:
    """Fetches papers from ArXiv for a given author."""

    NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}

    def __init__(self, author_query: str = "de+Lafuente,+F+A"):
        self.author_query = author_query
        self._cache: List[Paper] = []
        self._cache_time: Optional[datetime] = None
        self._cache_ttl_hours = 6

    def fetch_papers(self, max_results: int = 25) -> List[Paper]:
        """Fetch papers, using cache if fresh enough."""
        if self._cache and self._cache_time:
            age = (datetime.now() - self._cache_time).total_seconds() / 3600
            if age < self._cache_ttl_hours:
                logger.info(f"Using cached papers ({len(self._cache)} papers, {age:.1f}h old)")
                return self._cache

        try:
            papers = self._fetch_from_api(max_results)
            self._cache = papers
            self._cache_time = datetime.now()
            logger.info(f"Fetched {len(papers)} papers from ArXiv")
            return papers
        except Exception as e:
            logger.error(f"ArXiv fetch failed: {e}")
            return self._cache  # Return stale cache if available

    def _fetch_from_api(self, max_results: int) -> List[Paper]:
        params = {
            "search_query": f"au:{self.author_query}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }

        resp = requests.get(ARXIV_API, params=params, timeout=30)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        papers = []

        for entry in root.findall("atom:entry", self.NAMESPACE):
            try:
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)
            except Exception as e:
                logger.warning(f"Failed to parse entry: {e}")

        return papers

    def _parse_entry(self, entry) -> Optional[Paper]:
        ns = self.NAMESPACE

        title_el = entry.find("atom:title", ns)
        abstract_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        updated_el = entry.find("atom:updated", ns)

        if title_el is None or abstract_el is None:
            return None

        # Extract arxiv ID from entry id
        entry_id = entry.find("atom:id", ns)
        arxiv_id = entry_id.text.split("/abs/")[-1] if entry_id is not None else ""

        # Authors
        authors = []
        for author_el in entry.findall("atom:author", ns):
            name_el = author_el.find("atom:name", ns)
            if name_el is not None:
                authors.append(name_el.text)

        # Categories
        categories = []
        for cat_el in entry.findall("atom:category", ns):
            term = cat_el.get("term", "")
            if term:
                categories.append(term)

        # Links
        pdf_url = ""
        abs_url = ""
        for link_el in entry.findall("atom:link", ns):
            if link_el.get("title") == "pdf":
                pdf_url = link_el.get("href", "")
            elif link_el.get("type") == "text/html":
                abs_url = link_el.get("href", "")

        if not abs_url and arxiv_id:
            abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        if not pdf_url and arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

        return Paper(
            arxiv_id=arxiv_id,
            title=title_el.text.strip().replace("\n", " "),
            abstract=abstract_el.text.strip().replace("\n", " "),
            authors=authors,
            published=published_el.text if published_el is not None else "",
            updated=updated_el.text if updated_el is not None else "",
            categories=categories,
            pdf_url=pdf_url,
            abs_url=abs_url,
        )

    def get_paper_by_topic(self, topic: str) -> Optional[Paper]:
        """Find most relevant paper for a given topic."""
        papers = self.fetch_papers()
        topic_lower = topic.lower()
        for paper in papers:
            if (topic_lower in paper.title.lower() or
                    topic_lower in paper.abstract.lower()):
                return paper
        return papers[0] if papers else None

    def get_random_unshared(self, shared_ids: set) -> Optional[Paper]:
        """Get a paper that hasn't been shared yet."""
        papers = self.fetch_papers()
        for paper in papers:
            if paper.arxiv_id not in shared_ids:
                return paper
        # If all shared, cycle back
        return papers[0] if papers else None
