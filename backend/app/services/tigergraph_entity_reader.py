"""
TigerGraph Entity Reader and Filtering Service.
Reads nodes and edges from TigerGraph and filters nodes matching predefined entity types.
Direct drop-in replacement for ZepEntityReader.
"""

from __future__ import annotations

import json
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

from ..config import Config
from ..utils.logger import get_logger
from ..utils.tigergraph_client import get_tigergraph_connection

logger = get_logger('lokantra.tigergraph_entity_reader')


@dataclass
class EntityNode:
    """Entity node data structure matching Lokantra's contract."""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    related_edges: List[Dict[str, Any]] = field(default_factory=list)
    related_nodes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes,
            "related_edges": self.related_edges,
            "related_nodes": self.related_nodes,
        }

    def get_entity_type(self) -> Optional[str]:
        """Get entity types (excluding generic Entity/Node labels)."""
        for label in self.labels:
            if label.casefold() not in {"entity", "node"}:
                return label
        return "Entity" if self.labels else None


@dataclass
class FilteredEntities:
    """Filtered entity collection matching Lokantra's contract."""
    entities: List[EntityNode]
    entity_types: Set[str]
    total_count: int
    filtered_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "entity_types": list(self.entity_types),
            "total_count": self.total_count,
            "filtered_count": self.filtered_count,
        }


class TigerGraphEntityReader:
    """
    Reads nodes and edges from TigerGraph with exact ZepEntityReader compatibility.
    """

    def __init__(self, api_key: Optional[str] = None):
        # api_key preserved for contract compatibility
        self.conn = get_tigergraph_connection()

    def get_all_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        """
        Get all Entity vertices belonging to this graph_id.
        """
        logger.info(f"Fetching all nodes for graph {graph_id} from TigerGraph...")
        try:
            # Query vertices of type Entity with filter on graph_id
            vertices = self.conn.getVertices("Entity", where=f'graph_id="{graph_id}"')
            nodes_data = []
            for v in vertices:
                attrs = v.get("attributes", {})
                raw_labels = attrs.get("labels", "[]")
                try:
                    labels = json.loads(raw_labels) if raw_labels.startswith("[") else [attrs.get("entity_type", "Entity")]
                except Exception:
                    labels = [attrs.get("entity_type", "Entity")]

                raw_attributes = attrs.get("attributes", "{}")
                try:
                    parsed_attrs = json.loads(raw_attributes) if isinstance(raw_attributes, str) else raw_attributes
                except Exception:
                    parsed_attrs = {}

                nodes_data.append({
                    "uuid": str(v.get("v_id", "")),
                    "name": attrs.get("name", ""),
                    "labels": labels or ["Entity"],
                    "summary": attrs.get("summary", ""),
                    "attributes": parsed_attrs or {},
                })
            logger.info(f"Fetched {len(nodes_data)} nodes from TigerGraph")
            return nodes_data
        except Exception as e:
            logger.error(f"Failed to fetch nodes from TigerGraph: {e}")
            return []

    def get_all_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        """
        Get all RELATIONSHIP edges belonging to this graph_id.
        """
        logger.info(f"Fetching all edges for graph {graph_id} from TigerGraph...")
        try:
            # Get edges of type RELATIONSHIP
            edges = self.conn.getEdgesByType("RELATIONSHIP")
            edges_data = []
            for e in edges:
                attrs = e.get("attributes", {})
                if attrs.get("graph_id") != graph_id:
                    continue

                raw_attributes = attrs.get("attributes", "{}")
                try:
                    parsed_attrs = json.loads(raw_attributes) if isinstance(raw_attributes, str) else raw_attributes
                except Exception:
                    parsed_attrs = {}

                edge_uuid = f"{e.get('from_id')}_{attrs.get('rel_type')}_{e.get('to_id')}"
                edges_data.append({
                    "uuid": edge_uuid,
                    "name": attrs.get("rel_type", ""),
                    "fact": attrs.get("fact", ""),
                    "source_node_uuid": str(e.get("from_id", "")),
                    "target_node_uuid": str(e.get("to_id", "")),
                    "attributes": parsed_attrs or {},
                    "valid_at": attrs.get("valid_at"),
                    "invalid_at": attrs.get("invalid_at"),
                    "expired_at": attrs.get("expired_at"),
                })
            logger.info(f"Fetched {len(edges_data)} edges from TigerGraph")
            return edges_data
        except Exception as e:
            logger.error(f"Failed to fetch edges from TigerGraph: {e}")
            return []

    def get_node_edges(
        self,
        node_uuid: str,
        *,
        graph_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get relevant bidirectional edges for the specified node.
        """
        if not graph_id:
            return []
        all_edges = self.get_all_edges(graph_id)
        return [
            edge for edge in all_edges
            if edge["source_node_uuid"] == node_uuid or edge["target_node_uuid"] == node_uuid
        ]

    def filter_defined_entities(
        self,
        graph_id: str,
        defined_entity_types: Optional[List[str]] = None,
        enrich_with_edges: bool = True
    ) -> FilteredEntities:
        """
        Filter nodes matching predefined entity types, with complete incident edge enrichment.
        """
        logger.info(f"Starting entity filtering for graph {graph_id} in TigerGraph...")
        all_nodes = self.get_all_nodes(graph_id)
        total_count = len(all_nodes)
        all_edges = self.get_all_edges(graph_id) if enrich_with_edges else []
        node_map = {n["uuid"]: n for n in all_nodes}

        filtered_entities = []
        entity_types_found = set()

        for node in all_nodes:
            labels = [
                label.strip()
                for label in node.get("labels", [])
                if isinstance(label, str) and label.strip()
            ]

            custom_labels = [
                label for label in labels
                if label.casefold() not in {"entity", "node"}
            ]

            if not custom_labels:
                if defined_entity_types:
                    continue
                entity_type = "Entity"
            else:
                entity_type = custom_labels[0]

            if defined_entity_types:
                defined_types_by_key = {
                    t.casefold(): t
                    for t in defined_entity_types
                    if isinstance(t, str) and t.strip()
                }
                matching_labels = [
                    l for l in custom_labels
                    if l.casefold() in defined_types_by_key
                ]
                if not matching_labels:
                    continue
                entity_type = defined_types_by_key[matching_labels[0].casefold()]

            entity_types_found.add(entity_type)

            entity = EntityNode(
                uuid=node["uuid"],
                name=node["name"],
                labels=labels,
                summary=node.get("summary", ""),
                attributes=node.get("attributes", {}),
            )

            if enrich_with_edges:
                related_edges = []
                related_node_ids = set()
                for edge in all_edges:
                    if edge["source_node_uuid"] == node["uuid"]:
                        related_edges.append(edge)
                        related_node_ids.add(edge["target_node_uuid"])
                    elif edge["target_node_uuid"] == node["uuid"]:
                        related_edges.append(edge)
                        related_node_ids.add(edge["source_node_uuid"])

                entity.related_edges = related_edges
                entity.related_nodes = [
                    node_map[nid] for nid in related_node_ids if nid in node_map
                ]

            filtered_entities.append(entity)

        return FilteredEntities(
            entities=filtered_entities,
            entity_types=entity_types_found,
            total_count=total_count,
            filtered_count=len(filtered_entities),
        )


# Export alias so existing code importing ZepEntityReader continues to work seamlessly
ZepEntityReader = TigerGraphEntityReader
