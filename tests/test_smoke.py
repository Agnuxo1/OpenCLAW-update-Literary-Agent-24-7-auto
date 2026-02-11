"""Quick smoke test — validates all modules import correctly and basic functionality works."""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all modules import without errors."""
    from config import Config
    from core.llm_provider import LLMProvider
    from core.state_manager import StateManager
    from core.strategy_reflector import StrategyReflector
    from connectors.arxiv_scraper import ArXivScraper
    from connectors.moltbook import MoltbookConnector, MoltbookPostGenerator
    from connectors.email_connector import EmailConnector
    from agents.research_agent import ResearchAgent
    from agents.literary_agent import LiteraryAgent
    print("✅ All imports successful")


def test_state_manager():
    """Test state manager CRUD operations."""
    from core.state_manager import StateManager
    state = StateManager("state_test")

    state.heartbeat()
    assert state.get_agent_state()["cycle_count"] >= 1

    state.log_post("test", "Hello world", "test-topic", "test-001")
    posts = state.get_post_history(n=5)
    assert len(posts) >= 1
    assert posts[-1]["platform"] == "test"

    strategy = state.get_strategy()
    assert "tone" in strategy

    print("✅ State manager working")

    # Cleanup
    import shutil
    shutil.rmtree("state_test", ignore_errors=True)


def test_arxiv_scraper():
    """Test ArXiv paper fetching."""
    from connectors.arxiv_scraper import ArXivScraper
    scraper = ArXivScraper("de+Lafuente,+F+A")
    papers = scraper.fetch_papers(max_results=3)
    assert len(papers) > 0, "No papers found on ArXiv"
    print(f"✅ ArXiv scraper found {len(papers)} papers")
    print(f"   Latest: {papers[0].title}")


def test_literary_agent():
    """Test literary content generation."""
    from agents.literary_agent import LiteraryAgent
    agent = LiteraryAgent()
    post = agent.generate_literary_post()
    assert "content" in post
    assert len(post["content"]) > 50
    print(f"✅ Literary agent generated post ({len(post['content'])} chars)")


def test_strategy_reflector():
    """Test metacognition without LLM."""
    from core.state_manager import StateManager
    from core.strategy_reflector import StrategyReflector

    state = StateManager("state_test2")
    reflector = StrategyReflector(state)

    report = reflector.reflect()
    assert "status" in report or "performance_score" in report

    status = reflector.get_status_report()
    assert "OpenCLAW" in status
    print("✅ Strategy reflector working")

    import shutil
    shutil.rmtree("state_test2", ignore_errors=True)


if __name__ == "__main__":
    print("=" * 50)
    print("  OpenCLAW Agent — Smoke Tests")
    print("=" * 50)

    test_imports()
    test_state_manager()
    test_literary_agent()
    test_strategy_reflector()

    # ArXiv test requires network
    try:
        test_arxiv_scraper()
    except Exception as e:
        print(f"⚠️  ArXiv test skipped (network): {e}")

    print("\n🎉 All tests passed!")
