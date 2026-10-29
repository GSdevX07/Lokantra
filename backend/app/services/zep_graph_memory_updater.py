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

if Config.is_tigergraph():
    ZepGraphMemoryUpdater = TigerGraphMemoryUpdater
    ZepGraphMemoryManager = TigerGraphMemoryManager
else:
    ZepGraphMemoryUpdater = OriginalZepGraphMemoryUpdater
    ZepGraphMemoryManager = OriginalZepGraphMemoryManager

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
