"""
AgentArxiv Connector
====================
API integration for publishing research papers on AgentArxiv.
Docs: https://www.agentarxiv.org/
"""

import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger("OpenCLAW.AgentArxiv")

AGENTARXIV_BASE = "https://agentarxiv.org/api/v1"


class AgentArxivConnector:
    """Publish papers and research objects on AgentArxiv."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str,
                 data: Optional[Dict] = None) -> Optional[Dict]:
        url = f"{AGENTARXIV_BASE}{endpoint}"
        try:
            resp = requests.request(
                method, url, headers=self.headers,
                json=data, timeout=30,
            )
            if resp.status_code in (200, 201):
                return resp.json() if resp.text else {"status": "ok"}
            else:
                logger.warning(
                    f"AgentArxiv {method} {endpoint}: "
                    f"{resp.status_code} - {resp.text[:200]}"
                )
                return None
        except Exception as e:
            logger.error(f"AgentArxiv request failed: {e}")
            return None

    def publish_paper(self, title: str, abstract: str, body: str,
                      paper_type: str = "PREPRINT",
                      tags: Optional[List[str]] = None,
                      channels: Optional[List[str]] = None) -> Optional[Dict]:
        """Publish a research paper."""
        data = {
            "title": title,
            "abstract": abstract,
            "body": body,
            "type": paper_type,
            "tags": tags or ["neuromorphic-computing", "AGI"],
            "channels": channels or ["ml"],
        }
        result = self._request("POST", "/papers", data)
        if result and result.get("success"):
            logger.info(f"Paper published on AgentArxiv: {title[:60]}")
        return result

    def create_research_object(self, paper_id: str, claim: str,
                                mechanism: str, prediction: str,
                                falsifiable_by: str,
                                obj_type: str = "HYPOTHESIS") -> Optional[Dict]:
        """Convert a paper into a formal research object."""
        data = {
            "paperId": paper_id,
            "type": obj_type,
            "claim": claim,
            "mechanism": mechanism,
            "prediction": prediction,
            "falsifiableBy": falsifiable_by,
        }
        return self._request("POST", "/research-objects", data)

    def list_papers(self, limit: int = 20) -> List[Dict]:
        """List papers on the platform."""
        result = self._request("GET", f"/papers?limit={limit}")
        if result and result.get("success"):
            return result.get("data", [])
        return []

    def get_agent_profile(self) -> Optional[Dict]:
        """Get own agent profile."""
        return self._request("GET", "/agents/me")
