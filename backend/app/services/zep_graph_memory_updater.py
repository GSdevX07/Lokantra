"""
Graph Memory Updater Service (Dual Provider: TigerGraph + Zep Cloud).
"""

import time
from ..config import Config
from ..utils.zep import (
    ZEP_HTTP_REQUEST_TIMEOUT_SECONDS,
    ZEP_INGESTION_WAIT_TIMEOUT_SECONDS,
    call_zep_read_with_retry,
    get_zep_client,
)
from .tigergraph_memory_updater import (
    AgentActivity,
    TigerGraphMemoryUpdater,
    TigerGraphMemoryManager,
)
from .zep_memory_updater_impl import (
    AgentActivity as ZepAgentActivity,
    ZepGraphMemoryUpdater as OriginalZepGraphMemoryUpdater,
    ZepGraphMemoryManager as OriginalZepGraphMemoryManager,
)

class ZepGraphMemoryUpdater:
    def __new__(cls, *args, **kwargs):
        if Config.is_tigergraph():
            return TigerGraphMemoryUpdater(*args, **kwargs)
        return OriginalZepGraphMemoryUpdater(*args, **kwargs)

class ZepGraphMemoryManager:
    @staticmethod
    def get_simulation_ids_for_graph(graph_id: str):
        if Config.is_tigergraph():
            return TigerGraphMemoryManager.get_simulation_ids_for_graph(graph_id)
        return OriginalZepGraphMemoryManager.get_simulation_ids_for_graph(graph_id)

__all__ = [
    "AgentActivity",
    "ZepGraphMemoryUpdater",
    "ZepGraphMemoryManager",
    "TigerGraphMemoryUpdater",
    "TigerGraphMemoryManager",
    "OriginalZepGraphMemoryUpdater",
    "OriginalZepGraphMemoryManager",
    "get_zep_client",
    "call_zep_read_with_retry",
    "ZEP_INGESTION_WAIT_TIMEOUT_SECONDS",
    "ZEP_HTTP_REQUEST_TIMEOUT_SECONDS",
    "time",
]
