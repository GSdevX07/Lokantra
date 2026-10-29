"""
Web Search Service for Lokantra
Integrates with Serper API (https://serper.dev) for real-time Google search and news retrieval.
Empowers Graph building, reality seed ingestion, persona grounding, and ReportAgent fact verification.
"""

import os
import re
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('lokantra.web_search')

SERPER_SEARCH_URL = "https://google.serper.dev/search"
SERPER_NEWS_URL = "https://google.serper.dev/news"


class WebSearchService:
    """Unified service for web search and reality dossier extraction."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (
            api_key
            or Config.SERPER_API_KEY
            or os.environ.get('SERPER_API_KEY')
            or os.environ.get('SERVE_API_KEY')
            or os.environ.get('SERP_API_KEY')
            or ''
        ).strip()
        self.timeout = 15.0

    def is_configured(self) -> bool:
        """Check if an API key is present."""
        return bool(self.api_key and len(self.api_key) > 5)

    def search(
        self,
        query: str,
        num: int = 5,
        search_type: str = "search",
        country: str = "us",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Execute web search via Serper API.
        
        Args:
            query: Search query string
            num: Number of results to return (default: 5, max: 20)
            search_type: "search" for organic Google search, "news" for Google News
            country: Country code (e.g., 'us', 'in', 'gb')
            language: Language code (e.g., 'en')
            
        Returns:
            Dict containing query, results list, knowledgeGraph, answerBox, and status metadata.
        """
        clean_query = query.strip()
        if not clean_query:
            return {
                "success": False,
                "error": "Query string cannot be empty",
                "results": [],
                "provider": "serper"
            }

        if not self.is_configured():
            logger.warning("SERPER_API_KEY is not configured in .env. Live search cannot connect to Serper.")
            return {
                "success": False,
                "error": "SERPER_API_KEY is not configured in .env. Please configure your key from https://serper.dev.",
                "results": self._generate_diagnostic_fallback(clean_query),
                "provider": "diagnostic_fallback"
            }

        url = SERPER_NEWS_URL if search_type == "news" else SERPER_SEARCH_URL
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": clean_query,
            "num": min(max(num, 1), 20),
            "gl": country,
            "hl": language
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                
            if response.status_code == 401 or response.status_code == 403:
                err_msg = "Invalid or unauthorized SERPER_API_KEY. Please verify your key at https://serper.dev."
                logger.error(err_msg)
                return {
                    "success": False,
                    "error": err_msg,
                    "results": self._generate_diagnostic_fallback(clean_query),
                    "provider": "diagnostic_fallback"
                }

            response.raise_for_status()
            data = response.json()
            
            results = []
            kg = data.get("knowledgeGraph")
            answer_box = data.get("answerBox")
            
            # Extract organic or news results
            items = data.get("news") if search_type == "news" else data.get("organic", [])
            if not items and "organic" in data:
                items = data.get("organic", [])

            for item in items:
                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                date_str = item.get("date", "")
                source = item.get("source", "")
                if not source and link:
                    # Parse domain name as source
                    match = re.search(r"https?://(?:www\.)?([^/]+)", link)
                    source = match.group(1) if match else "Web"

                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "date": date_str,
                    "source": source
                })

            return {
                "success": True,
                "query": clean_query,
                "search_type": search_type,
                "knowledgeGraph": kg,
                "answerBox": answer_box,
                "results": results,
                "provider": "serper"
            }

        except httpx.RequestError as exc:
            err_msg = f"Network communication error with Serper API: {exc}"
            logger.error(err_msg)
            return {
                "success": False,
                "error": err_msg,
                "results": self._generate_diagnostic_fallback(clean_query),
                "provider": "diagnostic_fallback"
            }
        except Exception as exc:
            err_msg = f"Unexpected error during Serper web search: {exc}"
            logger.error(err_msg)
            return {
                "success": False,
                "error": err_msg,
                "results": [],
                "provider": "serper"
            }

    def search_news(self, query: str, num: int = 5) -> Dict[str, Any]:
        """Convenience method for searching recent news articles."""
        return self.search(query=query, num=num, search_type="news")

    def gather_seed_dossier(self, topic: str, num: int = 6, include_news: bool = True) -> Dict[str, Any]:
        """
        Gathers both organic search results and latest news to synthesize a
        structured reality briefing dossier for Knowledge Graph and OASIS simulation.
        """
        clean_topic = topic.strip()
        search_resp = self.search(clean_topic, num=num, search_type="search")
        news_resp = self.search(clean_topic, num=num, search_type="news") if include_news else {"results": []}

        combined_results: List[Dict[str, Any]] = []
        seen_links = set()

        for item in (news_resp.get("results", []) + search_resp.get("results", [])):
            link = item.get("link", "")
            if link and link in seen_links:
                continue
            if link:
                seen_links.add(link)
            combined_results.append(item)

        # Build markdown dossier
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        dossier_lines = [
            f"# REALITY SEED DOSSIER: {clean_topic.upper()}",
            f"**Generated At**: {now_str}",
            f"**Information Engine**: Serper Real-time Web Intelligence\n",
            "---"
        ]

        # Add Answer Box / Knowledge Graph if found
        answer_box = search_resp.get("answerBox")
        if answer_box:
            ans_title = answer_box.get("title", "Key Answer / Takeaway")
            ans_text = answer_box.get("answer") or answer_box.get("snippet", "")
            dossier_lines.append(f"\n### Core Fact / Executive Summary: {ans_title}")
            dossier_lines.append(f"{ans_text}\n")

        kg = search_resp.get("knowledgeGraph")
        if kg:
            kg_title = kg.get("title", "")
            kg_desc = kg.get("description", "")
            kg_type = kg.get("type", "")
            dossier_lines.append(f"\n### Entity Background: {kg_title} ({kg_type})")
            dossier_lines.append(f"{kg_desc}\n")

        # News section
        news_items = news_resp.get("results", [])
        if news_items:
            dossier_lines.append("\n## Latest News & Breaking Developments")
            for idx, item in enumerate(news_items[:5], 1):
                date_part = f" ({item.get('date')})" if item.get('date') else ""
                dossier_lines.append(
                    f"{idx}. **{item.get('title')}** - {item.get('source')}{date_part}\n"
                    f"   *Summary*: {item.get('snippet')}\n"
                    f"   *Source*: {item.get('link')}"
                )

        # Organic web context section
        web_items = search_resp.get("results", [])
        if web_items:
            dossier_lines.append("\n## Key Web Context & Analysis")
            for idx, item in enumerate(web_items[:6], 1):
                dossier_lines.append(
                    f"- **{item.get('title')}** ({item.get('source')})\n"
                    f"  {item.get('snippet')}\n"
                    f"  Ref: {item.get('link')}"
                )

        # References footer
        dossier_lines.append("\n## Verified External References")
        for idx, item in enumerate(combined_results[:10], 1):
            dossier_lines.append(f"[{idx}] {item.get('title')} - {item.get('link')}")

        dossier_content = "\n".join(dossier_lines)

        return {
            "success": search_resp.get("success", False) or bool(combined_results),
            "topic": clean_topic,
            "content": dossier_content,
            "sources": combined_results,
            "source_count": len(combined_results),
            "provider": search_resp.get("provider", "serper"),
            "error": search_resp.get("error")
        }

    def search_for_agent(self, query: str, max_results: int = 4) -> str:
        """
        Formatted response specifically designed for ReportAgent ReAct tool calls.
        Provides high-density facts, quotes, and URLs for markdown report generation.
        """
        resp = self.search(query=query, num=max_results)
        results = resp.get("results", [])

        if not results:
            if resp.get("error"):
                return f"[Web Search Warning] {resp.get('error')}"
            return f"No live search results found for query: '{query}'"

        lines = [f"=== Live Web Search Results for: '{query}' ==="]

        answer_box = resp.get("answerBox")
        if answer_box:
            lines.append(f"Direct Fact: {answer_box.get('answer') or answer_box.get('snippet')}")

        for idx, item in enumerate(results[:max_results], 1):
            title = item.get("title", "No Title")
            snippet = item.get("snippet", "No Snippet")
            source = item.get("source", "Web")
            link = item.get("link", "")
            date = f" [{item.get('date')}]" if item.get('date') else ""
            lines.append(f"\n[{idx}] {title}{date} (Source: {source})")
            lines.append(f"Summary: {snippet}")
            lines.append(f"URL: {link}")

        lines.append("\nUse these live facts, metrics, and citations to ground your analysis and compare simulation findings with real-world realities.")
        return "\n".join(lines)

    def _generate_diagnostic_fallback(self, query: str) -> List[Dict[str, Any]]:
        """Helpful fallback when API key is missing so development flow is clear."""
        return [
            {
                "title": f"Live Search Simulation for: {query}",
                "link": "https://serper.dev",
                "snippet": (
                    f"Lokantra WebSearch is ready. To connect to live Google search results, "
                    f"add your SERPER_API_KEY in .env. Search query received: '{query}'."
                ),
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "source": "Lokantra Environment Notice"
            }
        ]
