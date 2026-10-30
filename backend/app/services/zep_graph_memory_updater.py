"""
Graph Memory Updater Service (Dual Provider: TigerGraph + Zep Cloud).
"""

import time
from typing import Any, Dict, List, Optional
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

class _ZepGraphMemoryManagerMeta(type):
    def __getattr__(cls, name):
        target = TigerGraphMemoryManager if Config.is_tigergraph() else OriginalZepGraphMemoryManager
        return getattr(target, name)

class ZepGraphMemoryManager(metaclass=_ZepGraphMemoryManagerMeta):
    @classmethod
    def _target(cls):
        return TigerGraphMemoryManager if Config.is_tigergraph() else OriginalZepGraphMemoryManager

    @classmethod
    def force_remove_updater(cls, simulation_id: str):
        return cls._target().force_remove_updater(simulation_id)

    @classmethod
    def create_updater(cls, simulation_id: str, graph_id: str):
        return cls._target().create_updater(simulation_id, graph_id)

    @classmethod
    def get_updater(cls, simulation_id: str):
        return cls._target().get_updater(simulation_id)

    @classmethod
    def get_or_create(cls, graph_id: str, simulation_id: str):
        target = cls._target()
        if hasattr(target, "get_or_create"):
            return target.get_or_create(graph_id, simulation_id)
        updater = target.get_updater(simulation_id)
        if updater is None:
            updater = target.create_updater(simulation_id, graph_id)
        return updater

    @classmethod
    def get_simulation_ids_for_graph(cls, graph_id: str) -> List[str]:
        return cls._target().get_simulation_ids_for_graph(graph_id)

    @classmethod
    def get_simulation_ids(cls) -> List[str]:
        return cls._target().get_simulation_ids()

    @classmethod
    def discard_inactive_updater(cls, simulation_id: str) -> bool:
        return cls._target().discard_inactive_updater(simulation_id)

    @classmethod
    def stop_updater(cls, simulation_id: str):
        return cls._target().stop_updater(simulation_id)

    @classmethod
    def stop_all(cls):
        return cls._target().stop_all()

    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        return cls._target().get_all_stats()

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
