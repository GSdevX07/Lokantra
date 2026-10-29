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

class ZepToolsService:
    def __new__(cls, *args, **kwargs):
        if Config.is_tigergraph():
            return TigerGraphToolsService(*args, **kwargs)
        return OriginalZepToolsService(*args, **kwargs)

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
