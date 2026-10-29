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

if Config.is_tigergraph():
    GraphBuilderService = TigerGraphBuilderService
else:
    GraphBuilderService = ZepGraphBuilderService

__all__ = [
    "GraphInfo",
    "BatchSubmission",
    "GraphBuilderService",
    "TigerGraphBuilderService",
    "ZepGraphBuilderService",
    "time",
]
