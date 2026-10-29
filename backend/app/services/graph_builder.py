"""
Graph Building Service (Dual Provider: TigerGraph + Zep Cloud).
"""

import time
from ..config import Config
from .tigergraph_builder import (
    GraphInfo,
    BatchSubmission,
    TigerGraphBuilderService,
)
from .zep_builder_impl import (
    GraphBuilderService as ZepGraphBuilderService,
)

class GraphBuilderService:
    def __new__(cls, *args, **kwargs):
        if Config.is_tigergraph():
            return TigerGraphBuilderService(*args, **kwargs)
        return ZepGraphBuilderService(*args, **kwargs)

__all__ = [
    "GraphInfo",
    "BatchSubmission",
    "GraphBuilderService",
    "TigerGraphBuilderService",
    "ZepGraphBuilderService",
    "time",
]
