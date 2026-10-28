"""
Zep Entity Reader and Filtering Service.
Delegates to TigerGraphEntityReader for complete TigerGraph integration.
"""

from .tigergraph_entity_reader import (
    EntityNode,
    FilteredEntities,
    TigerGraphEntityReader as ZepEntityReader,
    TigerGraphEntityReader,
)

__all__ = [
    "EntityNode",
    "FilteredEntities",
    "ZepEntityReader",
    "TigerGraphEntityReader",
]
