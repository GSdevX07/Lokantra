"""
Unit tests for Web Search Service & Integration (Serper API)
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.web_search_service import WebSearchService
from app.services.report_agent import ReportAgent


def test_web_search_service_diagnostic_fallback_when_no_key():
    svc = WebSearchService(api_key="")
    assert not svc.is_configured()
    res = svc.search("quantum computing breakthrough")
    assert res["success"] is False
    assert res["provider"] == "diagnostic_fallback"
    assert len(res["results"]) > 0
    assert "SERPER_API_KEY" in res["error"]


def test_web_search_service_gather_seed_dossier():
    svc = WebSearchService(api_key="")
    dossier = svc.gather_seed_dossier("Artificial Intelligence Regulations")
    assert "content" in dossier
    assert "sources" in dossier
    assert "REALITY SEED DOSSIER" in dossier["content"]


@patch("httpx.Client.post")
def test_web_search_service_mock_serper_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "organic": [
            {
                "title": "OpenAI Announces Next-Gen Model",
                "link": "https://example.com/openai-model",
                "snippet": "A breakthrough in reasoning benchmarks was announced today.",
                "date": "2 hours ago",
                "source": "TechDaily"
            }
        ],
        "news": [
            {
                "title": "Tech Stocks Rally on AI News",
                "link": "https://example.com/stocks",
                "snippet": "Markets surged following the AI announcement.",
                "date": "1 hour ago",
                "source": "MarketWatch"
            }
        ],
        "answerBox": {
            "title": "Model Performance",
            "snippet": "Scores 95% on reasoning benchmark."
        }
    }
    mock_post.return_value = mock_resp

    svc = WebSearchService(api_key="mock_test_key_12345")
    assert svc.is_configured()

    res = svc.search("OpenAI announcement", num=5)
    assert res["success"] is True
    assert len(res["results"]) == 1
    assert res["results"][0]["title"] == "OpenAI Announces Next-Gen Model"
    assert res["answerBox"]["snippet"] == "Scores 95% on reasoning benchmark."

    # Test agent formatted search
    agent_summary = svc.search_for_agent("OpenAI announcement")
    assert "Live Web Search Results" in agent_summary
    assert "https://example.com/openai-model" in agent_summary


def test_report_agent_has_web_search_tool():
    # Verify tool registration in ReportAgent without needing full graph execution
    tools = ReportAgent._define_tools(None)
    assert "web_search" in tools
    assert "query" in tools["web_search"]["parameters"]
    assert "Serper" in tools["web_search"]["description"] or "Google" in tools["web_search"]["description"]


def test_api_web_search_endpoints():
    from app import create_app
    app = create_app()
    with app.test_client() as client:
        res = client.post("/api/graph/web-search", json={"query": "electric vehicles 2026"})
        assert res.status_code == 200
        data = res.get_json()
        assert "results" in data

        res2 = client.post("/api/graph/seed/web-search", json={"topic": "electric vehicles 2026"})
        assert res2.status_code == 200
        dossier = res2.get_json()
        assert "content" in dossier
        assert "topic" in dossier
