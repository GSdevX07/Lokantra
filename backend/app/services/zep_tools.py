"""
Retrieval Tools Service (Dual Provider: TigerGraph + Zep Cloud).
"""

from ..config import Config
from .tigergraph_tools import (
    SearchResult,
    NodeInfo,
    EdgeInfo,
    InsightForgeResult,
    PanoramaResult,
    AgentInterview,
    InterviewResult,
    TigerGraphToolsService,
)
from .zep_tools_impl import (
    ZepToolsService as OriginalZepToolsService,
)

if Config.is_tigergraph():
    ZepToolsService = TigerGraphToolsService
else:
    ZepToolsService = OriginalZepToolsService

__all__ = [
    "SearchResult",
    "NodeInfo",
    "EdgeInfo",
    "InsightForgeResult",
    "PanoramaResult",
    "AgentInterview",
    "InterviewResult",
    "ZepToolsService",
    "TigerGraphToolsService",
    "OriginalZepToolsService",
]
