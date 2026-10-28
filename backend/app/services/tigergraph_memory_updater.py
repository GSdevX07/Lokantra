"""
TigerGraph Memory Updater Service.
Dynamically updates Agent activities from OASIS simulation into TigerGraph.
Provides exact drop-in parity for ZepGraphMemoryUpdater.
"""

from __future__ import annotations

import json
import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from queue import Queue, Empty

from ..config import Config
from ..utils.logger import get_logger
from ..utils.embedding import EmbeddingService
from ..utils.tigergraph_client import get_tigergraph_connection

logger = get_logger('lokantra.tigergraph_memory_updater')


@dataclass
class AgentActivity:
    """Agent Activity Record matching simulation runner contract."""
    platform: str           # twitter / reddit
    agent_id: int
    agent_name: str
    action_type: str        # CREATE_POST, LIKE_POST, etc.
    action_args: Dict[str, Any]
    round_num: int
    timestamp: str

    def to_episode_text(self) -> str:
        """Convert activity to natural language description."""
        action_descriptions = {
            "CREATE_POST": self._describe_create_post,
            "LIKE_POST": self._describe_like_post,
            "DISLIKE_POST": self._describe_dislike_post,
            "REPOST": self._describe_repost,
            "QUOTE_POST": self._describe_quote_post,
            "FOLLOW": self._describe_follow,
            "CREATE_COMMENT": self._describe_create_comment,
            "LIKE_COMMENT": self._describe_like_comment,
            "DISLIKE_COMMENT": self._describe_dislike_comment,
            "SEARCH_POSTS": self._describe_search,
            "SEARCH_USER": self._describe_search_user,
            "MUTE": self._describe_mute,
        }
        describe_func = action_descriptions.get(self.action_type, self._describe_generic)
        description = describe_func()
        return (
            f"[{self.timestamp}] [{self.platform} round {self.round_num}] "
            f"{self.agent_name}: {description}"
        )

    def _describe_create_post(self) -> str:
        content = self.action_args.get("content", "")
        return f"posted: \"{content}\"" if content else "posted a message"

    def _describe_like_post(self) -> str:
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        if post_content and post_author:
            return f"liked {post_author}'s post: \"{post_content}\""
        return f"liked a post by {post_author}" if post_author else "liked a post"

    def _describe_dislike_post(self) -> str:
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        if post_content and post_author:
            return f"disliked {post_author}'s post: \"{post_content}\""
        return f"disliked a post by {post_author}" if post_author else "disliked a post"

    def _describe_repost(self) -> str:
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        if original_content and original_author:
            return f"reposted {original_author}'s post: \"{original_content}\""
        return f"reposted a post by {original_author}" if original_author else "reposted a post"

    def _describe_quote_post(self) -> str:
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        quote_content = self.action_args.get("quote_content", "") or self.action_args.get("content", "")
        base = f"quoted {original_author}'s post" if original_author else "quoted a post"
        if quote_content:
            base += f", commenting: \"{quote_content}\""
        return base

    def _describe_follow(self) -> str:
        target = self.action_args.get("target_user_name", "")
        return f"followed user \"{target}\"" if target else "followed a user"

    def _describe_create_comment(self) -> str:
        content = self.action_args.get("content", "")
        post_author = self.action_args.get("post_author_name", "")
        return f"commented on {post_author}'s post: \"{content}\"" if post_author else f"commented: \"{content}\""

    def _describe_like_comment(self) -> str:
        comment_author = self.action_args.get("comment_author_name", "")
        return f"liked {comment_author}'s comment" if comment_author else "liked a comment"

    def _describe_dislike_comment(self) -> str:
        comment_author = self.action_args.get("comment_author_name", "")
        return f"disliked {comment_author}'s comment" if comment_author else "disliked a comment"

    def _describe_search(self) -> str:
        query = self.action_args.get("query", "")
        return f"searched for \"{query}\"" if query else "searched posts"

    def _describe_search_user(self) -> str:
        query = self.action_args.get("query", "")
        return f"searched for user \"{query}\"" if query else "searched users"

    def _describe_mute(self) -> str:
        target = self.action_args.get("target_user_name", "")
        return f"muted user \"{target}\"" if target else "muted a user"

    def _describe_generic(self) -> str:
        return f"performed action {self.action_type}"


class TigerGraphMemoryUpdater:
    """
    Asynchronous buffer and updater that streams agent actions into TigerGraph.
    """

    BATCH_SIZE = 10
    FLUSH_INTERVAL = 3.0

    def __init__(
        self,
        graph_id: str,
        api_key: Optional[str] = None,
        simulation_id: Optional[str] = None,
    ):
        self.graph_id = graph_id
        self.simulation_id = simulation_id or "unknown"
        self.conn = get_tigergraph_connection()

        self._activity_queue: Queue = Queue()
        self._buffer: List[AgentActivity] = []
        self._buffer_lock = threading.Lock()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None

        self._total_activities = 0
        self._total_sent = 0
        self._failed_count = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name=f"TGMemoryUpdater-{self.graph_id[:8]}"
        )
        self._worker_thread.start()
        logger.info(f"TigerGraphMemoryUpdater started: graph_id={self.graph_id}")

    def stop(self):
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=15.0)
        self._flush_buffer()
        logger.info(f"TigerGraphMemoryUpdater stopped for graph={self.graph_id}")

    def add_activity(self, activity: AgentActivity):
        if activity.action_type == "DO_NOTHING":
            return
        self._total_activities += 1
        self._activity_queue.put(activity)

    def _worker_loop(self):
        last_flush = time.time()
        while self._running:
            try:
                try:
                    activity = self._activity_queue.get(timeout=1.0)
                    with self._buffer_lock:
                        self._buffer.append(activity)
                except Empty:
                    pass

                now = time.time()
                with self._buffer_lock:
                    should_flush = len(self._buffer) >= self.BATCH_SIZE or (
                        self._buffer and now - last_flush >= self.FLUSH_INTERVAL
                    )

                if should_flush:
                    self._flush_buffer()
                    last_flush = now
            except Exception as e:
                logger.error(f"Error in TigerGraphMemoryUpdater worker: {e}")
                time.sleep(1.0)

    def _flush_buffer(self):
        while not self._activity_queue.empty():
            try:
                self._buffer.append(self._activity_queue.get_nowait())
            except Empty:
                break
        with self._buffer_lock:
            if not self._buffer:
                return
            batch = list(self._buffer)
            self._buffer.clear()

        self._ingest_batch(batch)

    def _ingest_batch(self, batch: List[AgentActivity]):
        """
        Upsert entities and relationships into TigerGraph with temporal properties.
        """
        try:
            vertices_payload = []
            edges_payload = []

            for act in batch:
                actor_id = f"agent_{act.agent_id}"
                actor_name = act.agent_name
                timestamp = act.timestamp or datetime.now().isoformat()

                # Upsert Actor Vertex
                actor_embedding = EmbeddingService.get_embedding(actor_name)
                vertices_payload.append((
                    actor_id,
                    {
                        "graph_id": self.graph_id,
                        "name": actor_name,
                        "entity_type": "Agent",
                        "labels": json.dumps(["Entity", "Agent"]),
                        "summary": f"Agent {actor_name} on {act.platform}",
                        "attributes": json.dumps({"platform": act.platform, "agent_id": act.agent_id}),
                        "created_at": timestamp,
                        "embedding": actor_embedding,
                    }
                ))

                # Determine target of the action
                target_author = act.action_args.get("post_author_name") or act.action_args.get("target_user_name")
                target_id = f"target_{target_author}" if target_author else actor_id
                target_name = target_author or actor_name

                if target_id != actor_id:
                    target_embedding = EmbeddingService.get_embedding(target_name)
                    vertices_payload.append((
                        target_id,
                        {
                            "graph_id": self.graph_id,
                            "name": target_name,
                            "entity_type": "Entity",
                            "labels": json.dumps(["Entity", "User"]),
                            "summary": f"User {target_name} on {act.platform}",
                            "attributes": json.dumps({"platform": act.platform}),
                            "created_at": timestamp,
                            "embedding": target_embedding,
                        }
                    ))

                # Relationship edge
                fact_text = act.to_episode_text()
                edge_attributes = {
                    "graph_id": self.graph_id,
                    "rel_type": act.action_type,
                    "fact": fact_text,
                    "attributes": json.dumps(act.action_args),
                    "created_at": timestamp,
                    "valid_at": timestamp,
                    "invalid_at": "",
                    "expired_at": "",
                    "episodes": f"sim_{self.simulation_id}_r{act.round_num}",
                }

                edges_payload.append((
                    actor_id,
                    target_id,
                    edge_attributes
                ))

            # Upsert into TigerGraph
            if vertices_payload:
                self.conn.upsertVertices("Entity", vertices_payload)
            if edges_payload:
                self.conn.upsertEdges("Entity", "RELATIONSHIP", "Entity", edges_payload)

            self._total_sent += len(batch)
            logger.info(f"Ingested {len(batch)} simulation activities into TigerGraph graph={self.graph_id}")
        except Exception as e:
            self._failed_count += len(batch)
            logger.error(f"Failed to upsert activities into TigerGraph: {e}")


class TigerGraphMemoryManager:
    """Manages active updaters per simulation and graph."""
    _updaters: Dict[str, TigerGraphMemoryUpdater] = {}
    _lock = threading.Lock()

    @classmethod
    def get_or_create(cls, graph_id: str, simulation_id: str) -> TigerGraphMemoryUpdater:
        with cls._lock:
            key = f"{graph_id}:{simulation_id}"
            if key not in cls._updaters:
                updater = TigerGraphMemoryUpdater(graph_id=graph_id, simulation_id=simulation_id)
                updater.start()
                cls._updaters[key] = updater
            return cls._updaters[key]

    @classmethod
    def discard(cls, simulation_id: str):
        with cls._lock:
            for key, updater in list(cls._updaters.items()):
                if key.endswith(f":{simulation_id}"):
                    updater.stop()
                    del cls._updaters[key]

    @classmethod
    def get_simulation_ids_for_graph(cls, graph_id: str) -> List[str]:
        with cls._lock:
            prefix = f"{graph_id}:"
            return [k[len(prefix):] for k in cls._updaters if k.startswith(prefix)]

    @classmethod
    def discard_inactive_updater(cls, simulation_id: str):
        cls.discard(simulation_id)


# Export aliases for seamless backwards-compatibility
ZepGraphMemoryUpdater = TigerGraphMemoryUpdater
ZepGraphMemoryManager = TigerGraphMemoryManager
