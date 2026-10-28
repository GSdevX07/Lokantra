"""
TigerGraph Graph Building Service.
Replaces Zep GraphBuilderService.
Constructs standalone knowledge graphs in TigerGraph from unstructured documents and dynamic ontologies.
"""

from __future__ import annotations

import uuid
import time
import json
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from ..config import Config
from ..models.task import TaskManager, TaskStatus
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient
from ..utils.embedding import EmbeddingService
from ..utils.tigergraph_client import get_tigergraph_connection, init_lokantra_schema
from .text_processor import TextProcessor

logger = get_logger("lokantra.tigergraph_builder")


@dataclass
class GraphInfo:
    """Graph summary information."""
    graph_id: str
    node_count: int
    edge_count: int
    entity_types: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": self.entity_types,
        }


@dataclass(frozen=True)
class BatchSubmission:
    """Batch submission metadata matching Lokantra's contract."""
    batch_id: str
    operation_id: str
    episode_uuids: List[str]
    item_count: int


class TigerGraphBuilderService:
    """
    Constructs knowledge graphs in TigerGraph with automated LLM text extraction.
    """

    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]):
        """Set graph ontology (for schema validation and contract compatibility)."""
        import warnings
        from typing import Optional
        from pydantic import Field
        try:
            from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel
            from zep_cloud import EntityEdgeSourceTarget
        except ImportError:
            EntityModel = object
            EntityText = str
            EdgeModel = object
            class EntityEdgeSourceTarget:
                def __init__(self, source, target):
                    self.source = source
                    self.target = target

        from ..utils.ontology import (
            MAX_ONTOLOGY_TYPES,
            RESERVED_ONTOLOGY_ATTRIBUTE_NAMES,
            normalize_ontology_attributes,
            normalize_ontology_source_targets,
        )

        warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')

        def safe_attr_name(attr_name: str) -> str:
            if attr_name.lower() in RESERVED_ONTOLOGY_ATTRIBUTE_NAMES:
                return f"entity_{attr_name}"
            return attr_name

        entity_types = {}
        for entity_def in ontology.get("entity_types", [])[:MAX_ONTOLOGY_TYPES]:
            name = entity_def["name"]
            description = entity_def.get("description", f"A {name} entity.")
            attrs = {"__doc__": description}
            annotations = {}
            for normalized in normalize_ontology_attributes(entity_def.get("attributes", [])):
                attr_name = safe_attr_name(normalized["name"])
                attr_desc = normalized["description"]
                attrs[attr_name] = Field(description=attr_desc, default=None)
                annotations[attr_name] = Optional[EntityText]
            attrs["__annotations__"] = annotations
            entity_class = type(name, (EntityModel,), attrs)
            entity_class.__doc__ = description
            entity_types[name] = entity_class

        edge_definitions = {}
        for edge_def in ontology.get("edge_types", [])[:MAX_ONTOLOGY_TYPES]:
            name = edge_def["name"]
            description = edge_def.get("description", f"A {name} relationship.")
            attrs = {"__doc__": description}
            annotations = {}
            for normalized in normalize_ontology_attributes(edge_def.get("attributes", [])):
                attr_name = safe_attr_name(normalized["name"])
                attr_desc = normalized["description"]
                attrs[attr_name] = Field(description=attr_desc, default=None)
                annotations[attr_name] = Optional[str]
            attrs["__annotations__"] = annotations
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            edge_class = type(class_name, (EdgeModel,), attrs)
            edge_class.__doc__ = description

            source_targets = []
            for st in normalize_ontology_source_targets(edge_def.get("source_targets", [])):
                source_targets.append(
                    EntityEdgeSourceTarget(
                        source=st.get("source", "Entity"),
                        target=st.get("target", "Entity")
                    )
                )
            if source_targets:
                edge_definitions[name] = (edge_class, source_targets)

        if hasattr(self, "client") and hasattr(self.client, "graph"):
            self.client.graph.set_ontology(
                graph_ids=[graph_id],
                entities=entity_types,
                edges=edge_definitions if edge_definitions else None,
            )

    def __init__(self, api_key: Optional[str] = None):
        # Ensure schema exists on boot
        init_lokantra_schema()
        self.conn = get_tigergraph_connection()
        self.task_manager = TaskManager()
        self.llm = LLMClient()

    def build_graph_async(
        self,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str = "Lokantra Graph",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 350
    ) -> str:
        """
        Build knowledge graph asynchronously in TigerGraph.
        """
        task_id = self.task_manager.create_task(
            task_type="graph_build",
            metadata={
                "graph_name": graph_name,
                "chunk_size": chunk_size,
                "text_length": len(text),
            }
        )

        thread = threading.Thread(
            target=self._build_graph_worker,
            args=(task_id, text, ontology, graph_name, chunk_size, chunk_overlap)
        )
        thread.daemon = True
        thread.start()
        return task_id

    def _build_graph_worker(
        self,
        task_id: str,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
    ):
        try:
            self.task_manager.update_task(
                task_id,
                status=TaskStatus.PROCESSING,
                progress=5,
                message="Starting graph extraction in TigerGraph..."
            )

            chunks = TextProcessor.split_text(text, chunk_size, chunk_overlap)
            graph_id = f"lokantra_{uuid.uuid4().hex[:16]}"

            self.task_manager.update_task(
                task_id,
                progress=15,
                message=f"Initialized TigerGraph partition for graph {graph_id}."
            )

            total_chunks = len(chunks)
            all_vertices: Dict[str, Dict[str, Any]] = {}
            all_edges: List[Dict[str, Any]] = []

            # Extract entities and relationships from chunks using LLM
            for idx, chunk in enumerate(chunks):
                progress = 20 + int((idx / total_chunks) * 50)
                self.task_manager.update_task(
                    task_id,
                    progress=progress,
                    message=f"Extracting knowledge from chunk {idx + 1}/{total_chunks}..."
                )

                extracted = self._extract_from_chunk(chunk, ontology)

                # Collect entities
                for ent in extracted.get("entities", []):
                    name = ent.get("name", "").strip()
                    if not name:
                        continue
                    v_id = f"{graph_id}_{name.lower().replace(' ', '_')}"
                    entity_type = ent.get("type", "Entity")
                    summary = ent.get("summary", "")

                    if v_id in all_vertices:
                        # Merge summaries and attributes
                        if summary:
                            all_vertices[v_id]["summary"] += f" {summary}"
                    else:
                        all_vertices[v_id] = {
                            "graph_id": graph_id,
                            "name": name,
                            "entity_type": entity_type,
                            "labels": json.dumps(["Entity", entity_type]),
                            "summary": summary,
                            "attributes": json.dumps(ent.get("attributes", {})),
                            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "embedding": EmbeddingService.get_embedding(f"{name} {summary}"),
                        }

                # Collect edges
                for rel in extracted.get("relationships", []):
                    source = rel.get("source", "").strip()
                    target = rel.get("target", "").strip()
                    rel_type = rel.get("type", "RELATED_TO").strip()
                    fact = rel.get("fact", "").strip()
                    if not source or not target:
                        continue

                    src_id = f"{graph_id}_{source.lower().replace(' ', '_')}"
                    tgt_id = f"{graph_id}_{target.lower().replace(' ', '_')}"

                    # Ensure source and target exist
                    if src_id not in all_vertices:
                        all_vertices[src_id] = {
                            "graph_id": graph_id,
                            "name": source,
                            "entity_type": "Entity",
                            "labels": json.dumps(["Entity"]),
                            "summary": "",
                            "attributes": json.dumps({}),
                            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "embedding": EmbeddingService.get_embedding(source),
                        }
                    if tgt_id not in all_vertices:
                        all_vertices[tgt_id] = {
                            "graph_id": graph_id,
                            "name": target,
                            "entity_type": "Entity",
                            "labels": json.dumps(["Entity"]),
                            "summary": "",
                            "attributes": json.dumps({}),
                            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "embedding": EmbeddingService.get_embedding(target),
                        }

                    all_edges.append({
                        "from_id": src_id,
                        "to_id": tgt_id,
                        "graph_id": graph_id,
                        "rel_type": rel_type,
                        "fact": fact or f"{source} {rel_type} {target}",
                        "attributes": json.dumps(rel.get("attributes", {})),
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "valid_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "invalid_at": "",
                        "expired_at": "",
                        "episodes": f"chunk_{idx}",
                    })

            # Upsert into TigerGraph
            self.task_manager.update_task(
                task_id,
                progress=75,
                message=f"Writing {len(all_vertices)} vertices and {len(all_edges)} edges to TigerGraph..."
            )

            if all_vertices:
                vertices_payload = [(v_id, data) for v_id, data in all_vertices.items()]
                self.conn.upsertVertices("Entity", vertices_payload)

            if all_edges:
                edges_payload = [
                    (
                        e["from_id"],
                        e["to_id"],
                        {
                            "graph_id": e["graph_id"],
                            "rel_type": e["rel_type"],
                            "fact": e["fact"],
                            "attributes": e["attributes"],
                            "created_at": e["created_at"],
                            "valid_at": e["valid_at"],
                            "invalid_at": e["invalid_at"],
                            "expired_at": e["expired_at"],
                            "episodes": e["episodes"],
                        }
                    )
                    for e in all_edges
                ]
                self.conn.upsertEdges("Entity", "RELATIONSHIP", "Entity", edges_payload)

            self.task_manager.update_task(
                task_id,
                progress=90,
                message="Finalizing TigerGraph statistics..."
            )

            graph_info = self._get_graph_info(graph_id)

            self.task_manager.complete_task(task_id, {
                "graph_id": graph_id,
                "graph_info": graph_info.to_dict(),
                "chunks_processed": total_chunks,
            })
            logger.info(f"Successfully built TigerGraph graph {graph_id} with {graph_info.node_count} nodes, {graph_info.edge_count} edges.")

        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Graph build task failed: {error_msg}")
            self.task_manager.fail_task(task_id, error_msg)

    def _extract_from_chunk(self, chunk: str, ontology: Dict[str, Any]) -> Dict[str, Any]:
        """Call LLM to extract entities and relations conforming to ontology."""
        entity_types = [e.get("name") for e in ontology.get("entity_types", [])]
        edge_types = [e.get("name") for e in ontology.get("edge_types", [])]

        prompt = f"""You are a Knowledge Graph Extraction Engine.
Extract entities and relationships from the provided text according to this schema.

Permitted Entity Types: {', '.join(entity_types) if entity_types else 'Any'}
Permitted Relationship Types: {', '.join(edge_types) if edge_types else 'Any'}

Text:
\"\"\"{chunk}\"\"\"

Output STRICT JSON ONLY matching:
{{
  "entities": [
    {{"name": "Entity Name", "type": "EntityType", "summary": "Short 1-sentence bio", "attributes": {{}}}}
  ],
  "relationships": [
    {{"source": "Entity Name", "target": "Target Entity Name", "type": "RELATIONSHIP_TYPE", "fact": "Clear natural language fact describing the connection"}}
  ]
}}"""
        try:
            resp = self.llm.chat([{"role": "user", "content": prompt}], json_mode=True)
            return json.loads(resp)
        except Exception as e:
            logger.warning(f"LLM extraction fallback on chunk: {e}")
            return {"entities": [], "relationships": []}

    def _get_graph_info(self, graph_id: str) -> GraphInfo:
        from .tigergraph_entity_reader import TigerGraphEntityReader
        reader = TigerGraphEntityReader()
        nodes = reader.get_all_nodes(graph_id)
        edges = reader.get_all_edges(graph_id)
        entity_types = set()
        for n in nodes:
            for l in n.get("labels", []):
                if l not in ["Entity", "Node"]:
                    entity_types.add(l)
        return GraphInfo(
            graph_id=graph_id,
            node_count=len(nodes),
            edge_count=len(edges),
            entity_types=list(entity_types)
        )

    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        from .tigergraph_entity_reader import TigerGraphEntityReader
        reader = TigerGraphEntityReader()
        nodes = reader.get_all_nodes(graph_id)
        edges = reader.get_all_edges(graph_id)
        return {
            "graph_id": graph_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

    def delete_graph(self, graph_id: str):
        """Delete all entities and edges for this graph_id from TigerGraph."""
        try:
            self.conn.delVertices("Entity", where=f'graph_id="{graph_id}"')
            logger.info(f"Deleted TigerGraph data for graph_id={graph_id}")
        except Exception as e:
            logger.warning(f"Failed to delete partition for graph {graph_id}: {e}")


# Export alias so existing code seamlessly calls TigerGraphBuilderService
GraphBuilderService = TigerGraphBuilderService
