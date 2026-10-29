"""
TigerGraph Graph Building Service.
Replaces Zep GraphBuilderService.
Constructs standalone knowledge graphs in TigerGraph from unstructured documents and dynamic ontologies.
"""

from __future__ import annotations

import uuid
import time
import json
import hashlib
import re
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

    _batches: Dict[str, Dict[str, Any]] = {}
    _ontologies: Dict[str, Dict[str, Any]] = {}
    _graphs: Dict[str, Dict[str, Any]] = {}

    def __init__(self, api_key: Optional[str] = None):
        # Ensure schema exists on boot
        init_lokantra_schema()
        self.conn = get_tigergraph_connection()
        self.task_manager = TaskManager()
        self.llm = LLMClient()

    @staticmethod
    def validate_batch_chunks(chunks: List[str], *, batch_size: int = 350) -> None:
        """Validate text chunks before graph processing."""
        if not chunks:
            raise ValueError("At least one text chunk is required")
        if not 1 <= batch_size <= 350:
            raise ValueError("batch_size must be between 1 and 350")
        if len(chunks) > 50_000:
            raise ValueError("A batch cannot contain more than 50,000 items")
        oversized = [index for index, chunk in enumerate(chunks) if len(chunk) > 10_000]
        if oversized:
            raise ValueError(
                f"Batch item exceeds 10,000 characters at chunk {oversized[0]}"
            )

    @staticmethod
    def build_operation_id(graph_id: str, chunks: List[str]) -> str:
        """Build deterministic operation hash."""
        payload_hash = hashlib.sha256("\0".join(chunks).encode("utf-8")).hexdigest()
        return hashlib.sha256(
            f"{graph_id}:{payload_hash}".encode("utf-8")
        ).hexdigest()

    def create_graph(
        self,
        name: str,
        *,
        graph_id: str | None = None,
        graph_id_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Create a graph partition with a caller-durable ID."""
        graph_id = graph_id or f"lokantra_{uuid.uuid4().hex[:16]}"
        if graph_id_callback:
            graph_id_callback(graph_id)
        self._graphs[graph_id] = {"name": name, "created_at": time.time()}
        return graph_id

    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]):
        """Set and store graph ontology."""
        self._ontologies[graph_id] = ontology
        self._current_ontology = ontology

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
            try:
                self.client.graph.set_ontology(
                    graph_ids=[graph_id],
                    entities=entity_types,
                    edges=edge_definitions if edge_definitions else None,
                )
            except Exception:
                pass

    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 350,
        progress_callback: Optional[Callable] = None,
        batch_created_callback: Optional[Callable[[str | None, str], None]] = None,
    ) -> BatchSubmission:
        """Process chunks and upsert extracted entities and relations into TigerGraph."""
        if not graph_id:
            raise ValueError("graph_id is required")
        self.validate_batch_chunks(chunks, batch_size=batch_size)

        total_chunks = len(chunks)
        operation_id = self.build_operation_id(graph_id, chunks)
        batch_id = f"batch_{uuid.uuid4().hex[:16]}"

        if batch_created_callback:
            batch_created_callback(batch_id, operation_id)

        ontology = self._ontologies.get(graph_id, getattr(self, "_current_ontology", {}))
        all_vertices: Dict[str, Dict[str, Any]] = {}
        all_edges: List[Dict[str, Any]] = []

        for idx, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(
                    f"Extracting knowledge ({idx + 1}/{total_chunks})...",
                    (idx + 1) / total_chunks
                )

            extracted = self._extract_from_chunk(chunk, ontology)

            for ent in extracted.get("entities", []):
                name = ent.get("name", "").strip()
                if not name:
                    continue
                v_id = f"{graph_id}_{name.lower().replace(' ', '_')}"
                entity_type = ent.get("type", "Entity")
                summary = ent.get("summary", "")

                if v_id in all_vertices:
                    if summary and summary not in all_vertices[v_id]["summary"]:
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

            for rel in extracted.get("relationships", []):
                source = rel.get("source", "").strip()
                target = rel.get("target", "").strip()
                rel_type = rel.get("type", "RELATED_TO").strip()
                fact = rel.get("fact", "").strip()
                if not source or not target:
                    continue

                src_id = f"{graph_id}_{source.lower().replace(' ', '_')}"
                tgt_id = f"{graph_id}_{target.lower().replace(' ', '_')}"

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

        episode_uuids = [f"ep_{uuid.uuid4().hex[:12]}" for _ in chunks]
        submission = BatchSubmission(
            batch_id=batch_id,
            operation_id=operation_id,
            episode_uuids=episode_uuids,
            item_count=total_chunks,
        )
        self._batches[batch_id] = {
            "batch_id": batch_id,
            "operation_id": operation_id,
            "status": "succeeded",
            "item_count": total_chunks,
            "episode_uuids": episode_uuids,
        }
        return submission

    def _wait_for_batch(
        self,
        submission: BatchSubmission,
        progress_callback: Optional[Callable] = None,
        timeout: int | None = None,
    ) -> List[str]:
        """Wait for batch completion and report progress."""
        if progress_callback:
            progress_callback("Completed TigerGraph graph indexing", 1.0)
        return submission.episode_uuids

    def get_batch_summary(self, batch_id: str) -> Any:
        """Get summary of batch ingestion for restart/reconciliation."""
        class BatchProgress:
            percent_complete = 100
            succeeded_items = 1
            failed_items = 0

        class BatchSummaryResult:
            def __init__(self, status="succeeded", count=1):
                self.status = status
                self.progress = BatchProgress()
                self.progress.succeeded_items = count

        if batch_id in self._batches:
            b = self._batches[batch_id]
            return BatchSummaryResult(status=b.get("status", "succeeded"), count=b.get("item_count", 1))

        return BatchSummaryResult(status="succeeded")

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
            self.validate_batch_chunks(chunks)
            graph_id = self.create_graph(name=graph_name)
            self.set_ontology(graph_id, ontology)

            self.task_manager.update_task(
                task_id,
                progress=15,
                message=f"Initialized TigerGraph partition for graph {graph_id}."
            )

            def progress_cb(msg, ratio):
                prog = 15 + int(ratio * 70)
                self.task_manager.update_task(task_id, progress=prog, message=msg)

            submission = self.add_text_batches(graph_id, chunks, progress_callback=progress_cb)
            self._wait_for_batch(submission)

            self.task_manager.update_task(
                task_id,
                progress=90,
                message="Finalizing TigerGraph statistics..."
            )

            graph_info = self._get_graph_info(graph_id)

            self.task_manager.complete_task(task_id, {
                "graph_id": graph_id,
                "graph_info": graph_info.to_dict(),
                "chunks_processed": len(chunks),
            })
            logger.info(f"Successfully built TigerGraph graph {graph_id} with {graph_info.node_count} nodes, {graph_info.edge_count} edges.")

        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Graph build task failed: {error_msg}")
            self.task_manager.fail_task(task_id, error_msg)

    def _extract_from_chunk(self, chunk: str, ontology: Dict[str, Any]) -> Dict[str, Any]:
        """Call LLM to extract entities and relations conforming to ontology."""
        entity_types = [e.get("name") for e in ontology.get("entity_types", [])] if ontology else []
        edge_types = [e.get("name") for e in ontology.get("edge_types", [])] if ontology else []

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
            data = self.llm.chat_json([{"role": "user", "content": prompt}], temperature=0.1)
            if isinstance(data, dict):
                entities = data.get("entities", [])
                relationships = data.get("relationships", [])
                return {
                    "entities": entities if isinstance(entities, list) else [],
                    "relationships": relationships if isinstance(relationships, list) else []
                }
            return {"entities": [], "relationships": []}
        except Exception as e:
            logger.warning(f"LLM extraction chat_json fallback on chunk: {e}")
            try:
                resp = self.llm.chat([{"role": "user", "content": prompt}])
                cleaned = re.sub(r'<think>[\s\S]*?</think>', '', resp).strip()
                cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'\n?```\s*$', '', cleaned)
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict):
                    return {
                        "entities": parsed.get("entities", []) if isinstance(parsed.get("entities"), list) else [],
                        "relationships": parsed.get("relationships", []) if isinstance(parsed.get("relationships"), list) else []
                    }
            except Exception as e2:
                logger.warning(f"Secondary LLM fallback failed: {e2}")
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
