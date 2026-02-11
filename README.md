# OpenCLAW — Autonomous AI Research & Literary Agent 24/7

**Open Collaborative Laboratory for Autonomous Wisdom**

An autonomous AI agent that operates 24/7, publishing real research papers, engaging with AI communities, promoting scientific literature, and continuously self-improving through metacognition.

---

## What It Does

| Capability | Description |
|---|---|
| **Research Publishing** | Automatically fetches papers from ArXiv and publishes summaries to AI agent communities |
| **Community Engagement** | Proactively interacts with other AI agents on platforms like Moltbook, seeking research collaborators |
| **Literary Promotion** | Promotes ~40 published sci-fi novels, bridging fiction with real AGI research |
| **Metacognition** | Analyzes its own performance, generates hypotheses, and adjusts strategy automatically |
| **Email Notifications** | Sends status reports and boot confirmations to the admin |
| **Health Monitoring** | HTTP health endpoint for cloud platform monitoring |

## Architecture

```
main.py                     ← Entry point + health server
├── config.py               ← Environment-based configuration (no hardcoded secrets)
├── core/
│   ├── autonomous_loop.py  ← 24/7 orchestrator with task scheduling
│   ├── llm_provider.py     ← Multi-provider LLM (Gemini → Groq → NVIDIA fallback)
│   ├── state_manager.py    ← Persistent JSON state management
│   └── strategy_reflector.py ← Metacognition & self-improvement engine
├── connectors/
│   ├── arxiv_scraper.py    ← Real paper fetching from ArXiv API
│   ├── moltbook.py         ← Moltbook social platform API
│   └── email_connector.py  ← Zoho SMTP/IMAP integration
├── agents/
│   ├── research_agent.py   ← Paper publishing & collaboration seeking
│   └── literary_agent.py   ← Book promotion & author branding
└── state/                  ← Runtime data (gitignored)
```

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/Agnuxo1/OpenCLAW-update-Literary-Agent-24-7-auto.git
cd OpenCLAW-update-Literary-Agent-24-7-auto

# Copy environment template and fill in your keys
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Install & Run Locally

```bash
pip install -r requirements.txt

# Test with a single cycle
python main.py once

# Start 24/7 operation
python main.py run

# Check status
python main.py status
```

### 3. Deploy to Cloud (Free)

**Render.com (Recommended):**
1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your repository — Render auto-detects `render.yaml`
4. Set secret environment variables in the Render dashboard
5. Deploy

**Railway.app:**
1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select this repository
3. Set environment variables in Railway dashboard
4. Deploy

**Docker:**
```bash
docker build -t openclaw-agent .
docker run -d --env-file .env -p 8080:8080 openclaw-agent
```

## Configuration

All configuration is via environment variables. See `.env.example` for the full list.

**Required (at least one LLM):**
- `GEMINI_API_KEY` — Google Gemini API key
- `GROQ_API_KEY` — Groq API key (fallback)

**Social Platforms:**
- `MOLTBOOK_API_KEY` — For publishing to Moltbook

**Email (Optional):**
- `ZOHO_EMAIL` / `ZOHO_PASSWORD` — For notifications

**Schedule (with defaults):**
- `POST_INTERVAL_HOURS=4` — How often to publish research
- `ENGAGEMENT_INTERVAL_MINUTES=60` — How often to engage with community
- `REFLECTION_INTERVAL_HOURS=6` — How often to self-reflect

## Task Schedule

| Task | Interval | Description |
|---|---|---|
| Research Publishing | Every 4h | Publishes a new paper from ArXiv |
| Community Engagement | Every 1h | Comments on relevant posts, replies to notifications |
| Literary Promotion | Every 8h | Publishes book-related content |
| Self-Reflection | Every 6h | Analyzes performance, adjusts strategy |
| Email Check | Every 30m | Checks inbox for messages |
| Heartbeat | Every 30s | Updates state, keeps process alive |

## Endpoints

| Path | Description |
|---|---|
| `GET /health` | Health check (returns JSON status) |
| `GET /metrics` | Agent metrics (posts, engagements, cycles) |

## Research Context

This agent supports the research of **Francisco Angulo de Lafuente**, focusing on:
- **CHIMERA** — Neuromorphic computing with OpenGL as universal computation substrate
- **Holographic Neural Networks** — Winner, NVIDIA LlamaIndex Developers 2024
- **Thermodynamic Probability Filters** — Physics-based alternative to backpropagation
- **ASIC Repurposing** — Using Bitcoin mining hardware for AI inference

**Publications:** [Google Scholar](https://scholar.google.com/citations?user=6nOpJ9IAAAAJ&hl=en) · [ArXiv](https://arxiv.org/search/cs?searchtype=author&query=de+Lafuente,+F+A)  
**Code:** [GitHub](https://github.com/Agnuxo1)  
**Author:** [Wikipedia](https://es.wikipedia.org/wiki/Francisco_Angulo_de_Lafuente)

## Security

- **Zero hardcoded credentials** — All secrets via environment variables
- **`.env` is gitignored** — Never committed to the repository
- **Render/Railway secrets** — Set via dashboard, never in code
- **API key rotation** — Replace keys in `.env` or cloud dashboard at any time

## License

MIT License — Open source for the advancement of AGI research.
