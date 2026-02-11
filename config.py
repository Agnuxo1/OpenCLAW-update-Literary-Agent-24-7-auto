"""
OpenCLAW Configuration
======================
All settings loaded from environment variables. No hardcoded secrets.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int = 0) -> int:
    return int(os.environ.get(key, str(default)))


@dataclass
class AgentIdentity:
    name: str = field(default_factory=lambda: _env("AGENT_NAME", "OpenCLAW-Neuromorphic"))
    handle: str = field(default_factory=lambda: _env("AGENT_HANDLE", "OpenCLAW-Neuromorphic"))
    admin_email: str = field(default_factory=lambda: _env("ADMIN_EMAIL"))
    github_username: str = field(default_factory=lambda: _env("GITHUB_USERNAME", "Agnuxo1"))
    scholar_id: str = field(default_factory=lambda: _env("SCHOLAR_ID", "6nOpJ9IAAAAJ"))
    arxiv_query: str = field(default_factory=lambda: _env("ARXIV_AUTHOR_QUERY", "de_Lafuente"))

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.github_username}"

    @property
    def scholar_url(self) -> str:
        return f"https://scholar.google.com/citations?user={self.scholar_id}&hl=en"

    @property
    def arxiv_url(self) -> str:
        return f"https://arxiv.org/search/cs?searchtype=author&query={self.arxiv_query}"


@dataclass
class LLMConfig:
    gemini_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    groq_key: str = field(default_factory=lambda: _env("GROQ_API_KEY"))
    nvidia_key: str = field(default_factory=lambda: _env("NVIDIA_API_KEY"))
    hf_key: str = field(default_factory=lambda: _env("HF_API_KEY"))


@dataclass
class SocialConfig:
    moltbook_key: str = field(default_factory=lambda: _env("MOLTBOOK_API_KEY"))
    reddit_username: str = field(default_factory=lambda: _env("REDDIT_USERNAME"))
    reddit_password: str = field(default_factory=lambda: _env("REDDIT_PASSWORD"))
    reddit_client_id: str = field(default_factory=lambda: _env("REDDIT_CLIENT_ID"))
    reddit_client_secret: str = field(default_factory=lambda: _env("REDDIT_CLIENT_SECRET"))
    chirper_email: str = field(default_factory=lambda: _env("CHIRPER_EMAIL"))
    chirper_password: str = field(default_factory=lambda: _env("CHIRPER_PASSWORD"))
    agentarxiv_key: str = field(default_factory=lambda: _env("AGENTARXIV_API_KEY"))


@dataclass
class EmailConfig:
    address: str = field(default_factory=lambda: _env("ZOHO_EMAIL"))
    password: str = field(default_factory=lambda: _env("ZOHO_PASSWORD"))
    smtp_host: str = field(default_factory=lambda: _env("ZOHO_SMTP_HOST", "smtp.zoho.eu"))
    smtp_port: int = field(default_factory=lambda: _env_int("ZOHO_SMTP_PORT", 465))
    imap_host: str = field(default_factory=lambda: _env("ZOHO_IMAP_HOST", "imap.zoho.eu"))
    imap_port: int = field(default_factory=lambda: _env_int("ZOHO_IMAP_PORT", 993))


@dataclass
class SearchConfig:
    brave_key: str = field(default_factory=lambda: _env("BRAVE_API_KEY"))


@dataclass
class ScheduleConfig:
    post_interval_hours: int = field(default_factory=lambda: _env_int("POST_INTERVAL_HOURS", 4))
    engagement_interval_min: int = field(default_factory=lambda: _env_int("ENGAGEMENT_INTERVAL_MINUTES", 60))
    reflection_interval_hours: int = field(default_factory=lambda: _env_int("REFLECTION_INTERVAL_HOURS", 6))
    email_check_interval_min: int = field(default_factory=lambda: _env_int("EMAIL_CHECK_INTERVAL_MINUTES", 30))


@dataclass
class Config:
    identity: AgentIdentity = field(default_factory=AgentIdentity)
    llm: LLMConfig = field(default_factory=LLMConfig)
    social: SocialConfig = field(default_factory=SocialConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    state_dir: str = field(default_factory=lambda: _env("STATE_DIR", "state"))
    port: int = field(default_factory=lambda: _env_int("PORT", 8080))
    environment: str = field(default_factory=lambda: _env("ENVIRONMENT", "development"))
    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))

    def validate(self) -> list[str]:
        """Return list of missing critical config keys."""
        warnings = []
        if not self.llm.gemini_key and not self.llm.groq_key:
            warnings.append("No LLM API key configured (GEMINI_API_KEY or GROQ_API_KEY)")
        if not self.social.moltbook_key:
            warnings.append("MOLTBOOK_API_KEY not set — social posting disabled")
        if not self.email.address:
            warnings.append("ZOHO_EMAIL not set — email features disabled")
        return warnings


# Singleton
config = Config()
