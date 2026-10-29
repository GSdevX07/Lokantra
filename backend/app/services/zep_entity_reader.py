"""
Entity Reader and Filtering Service (Dual Provider: TigerGraph + Zep Cloud).
"""

from ..config import Config
from .tigergraph_entity_reader import (
    EntityNode,
    FilteredEntities,
    TigerGraphEntityReader,
)
from .zep_entity_reader_impl import (
    ZepEntityReader as OriginalZepEntityReader,
)

class ZepEntityReader:
    def __new__(cls, *args, **kwargs):
        if Config.is_tigergraph():
            return TigerGraphEntityReader(*args, **kwargs)
        return OriginalZepEntityReader(*args, **kwargs)

__all__ = [
    "EntityNode",
    "FilteredEntities",
    "ZepEntityReader",
    "TigerGraphEntityReader",
    "OriginalZepEntityReader",
]
