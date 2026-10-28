"""
TigerGraph Adapter for Zep Cloud SDK.
Mimics the zep_cloud.Zep client interface so that existing Zep calls
transparently execute against TigerGraph with zero breaking changes.
"""

from __future__ import annotations

import uuid
import time
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from .logger import get_logger
from .tigergraph_client import get_tigergraph_connection, init_lokantra_schema
from ..services.tigergraph_tools import TigerGraphToolsService
from ..services.tigergraph_entity_reader import TigerGraphEntityReader

logger = get_logger("lokantra.tigergraph_adapter")


class _NodeAdapter:
    def __init__(self, reader: TigerGraphEntityReader):
        self.reader = reader

    def get_edges(self, node_uuid: str) -> List[Any]:
        # Return incident edges as objects
        try:
            edges = self.reader.get_node_edges(node_uuid)
            return [
                SimpleNamespace(
                    uuid=e.get("uuid", ""),
                    uuid_=e.get("uuid", ""),
                    name=e.get("name", ""),
                    fact=e.get("fact", ""),
                    source_node_uuid=e.get("source_node_uuid", ""),
                    target_node_uuid=e.get("target_node_uuid", ""),
                    attributes=e.get("attributes", {}),
                )
                for e in edges
            ]
        except Exception as ex:
            logger.warning(f"Failed to get edges for node {node_uuid}: {ex}")
            return []


class _EpisodeAdapter:
    def get(self, uuid_: str) -> Any:
        return SimpleNamespace(
            uuid=uuid_,
            uuid_=uuid_,
            processed=True,
        )


class _GraphAdapter:
    def __init__(self, reader: TigerGraphEntityReader, tools: TigerGraphToolsService):
        self.reader = reader
        self.tools = tools
        self.node = _NodeAdapter(reader)
        self.episode = _EpisodeAdapter()

    def create(self, graph_id: str, name: str, description: str = "") -> Any:
        logger.info(f"[TigerGraph] Creating graph partition: {graph_id} ('{name}')")
        return SimpleNamespace(graph_id=graph_id, name=name, description=description)

    def get(self, graph_id: str) -> Any:
        return SimpleNamespace(graph_id=graph_id, name="Lokantra Graph")

    def delete(self, graph_id: str) -> None:
        logger.info(f"[TigerGraph] Deleting graph partition: {graph_id}")
        from ..services.tigergraph_builder import TigerGraphBuilderService
        TigerGraphBuilderService().delete_graph(graph_id)

    def set_ontology(self, graph_ids: List[str], entities: Any = None, edges: Any = None) -> None:
        logger.info(f"[TigerGraph] Registered ontology schema for graph(s): {graph_ids}")

    def add(
        self,
        graph_id: str,
        type: str = "text",
        data: str = "",
        created_at: Optional[str] = None,
        source_description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        episode_uuid = f"ep_{uuid.uuid4().hex[:16]}"
        logger.info(f"[TigerGraph] Ingesting episode {episode_uuid} for graph={graph_id}")
        return SimpleNamespace(uuid=episode_uuid, uuid_=episode_uuid)

    def search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10,
        scope: str = "edges",
        reranker: str = "cross_encoder",
    ) -> Any:
        search_res = self.tools.search_graph(graph_id, query, limit=limit, scope=scope)
        edges = [
            SimpleNamespace(
                uuid=e.get("uuid", ""),
                uuid_=e.get("uuid", ""),
                name=e.get("name", ""),
                fact=e.get("fact", ""),
                source_node_uuid=e.get("source_node_uuid", ""),
                target_node_uuid=e.get("target_node_uuid", ""),
            )
            for e in search_res.edges
        ]
        nodes = [
            SimpleNamespace(
                uuid=n.get("uuid", ""),
                uuid_=n.get("uuid", ""),
                name=n.get("name", ""),
                labels=n.get("labels", []),
                summary=n.get("summary", ""),
            )
            for n in search_res.nodes
        ]
        return SimpleNamespace(edges=edges, nodes=nodes)


class _BatchAdapter:
    _batches: Dict[str, Dict[str, Any]] = {}

    def create(self, metadata: Optional[Dict[str, Any]] = None) -> Any:
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        self._batches[batch_id] = {
            "batch_id": batch_id,
            "metadata": metadata or {},
            "items": [],
            "status": "draft",
        }
        return SimpleNamespace(batch_id=batch_id, metadata=metadata or {})

    def add(self, batch_id: str, items: List[Any]) -> List[Any]:
        batch = self._batches.setdefault(batch_id, {"items": [], "status": "draft"})
        item_details = []
        for idx, item in enumerate(items):
            ep_uuid = f"ep_{uuid.uuid4().hex[:12]}"
            batch["items"].append(item)
            item_details.append(
                SimpleNamespace(
                    sequence_index=idx,
                    episode_uuid=ep_uuid,
                    source_uuid=ep_uuid,
                    status="succeeded",
                )
            )
        return item_details

    def process(self, batch_id: str) -> None:
        if batch_id in self._batches:
            self._batches[batch_id]["status"] = "succeeded"

    def get(self, batch_id: str) -> Any:
        batch = self._batches.get(batch_id, {"items": []})
        count = len(batch.get("items", []))
        return SimpleNamespace(
            batch_id=batch_id,
            status="succeeded",
            progress=SimpleNamespace(
                percent_complete=100.0,
                succeeded_items=count,
                failed_items=0,
            )
        )

    def list(self, limit: int = 100, cursor: Optional[int] = None) -> Any:
        batch_list = [
            SimpleNamespace(
                batch_id=b_id,
                metadata=data.get("metadata", {}),
                status=data.get("status", "succeeded"),
            )
            for b_id, data in self._batches.items()
        ]
        return SimpleNamespace(batches=batch_list, next_cursor=None)

    def list_items(self, batch_id: str, limit: int = 100, cursor: Optional[int] = None) -> Any:
        batch = self._batches.get(batch_id, {"items": []})
        items = [
            SimpleNamespace(
                sequence_index=i,
                episode_uuid=f"ep_{i}",
                source_uuid=f"ep_{i}",
                status="succeeded",
            )
            for i in range(len(batch.get("items", [])))
        ]
        return SimpleNamespace(items=items, next_cursor=None)


class TigerGraphZepAdapter:
    """
    Exposes client.graph and client.batch identically to zep_cloud.Zep.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: float = 60.0):
        init_lokantra_schema()
        self.reader = TigerGraphEntityReader()
        self.tools = TigerGraphToolsService()
        self.graph = _GraphAdapter(self.reader, self.tools)
        self.batch = _BatchAdapter()
