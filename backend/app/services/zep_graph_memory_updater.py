"""
Zep Graph Memory Updater Service
Dynamically updates Agent activities from simulation into Zep graph
"""

import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from queue import Queue, Empty

from ..config import Config
from ..utils.logger import get_logger
from ..utils.locale import get_locale, set_locale
from ..utils.zep import (
    ZEP_INGESTION_WAIT_TIMEOUT_SECONDS,
    call_zep_read_with_retry,
    get_zep_client,
)

logger = get_logger('lokantra.zep_graph_memory_updater')


@dataclass
class AgentActivity:
    """Agent Activity Record"""
    platform: str           # twitter / reddit
    agent_id: int
    agent_name: str
    action_type: str        # CREATE_POST, LIKE_POST, etc.
    action_args: Dict[str, Any]
    round_num: int
    timestamp: str
    
    def to_episode_text(self) -> str:
        """
        Convert activity to text description for Zep
        
        Uses natural language format so Zep can extract entities and relations
        Avoids simulation-specific prefixes that could mislead graph updates
        """
        # Generate descriptions based on action types
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
        
        # Keep the event time in the source text as well as episode metadata so
        # temporal extraction does not collapse a multi-action batch.
        return (
            f"[{self.timestamp}] [{self.platform} round {self.round_num}] "
            f"{self.agent_name}: {description}"
        )
    
    def _describe_create_post(self) -> str:
        content = self.action_args.get("content", "")
        if content:
            return f"posted: \"{content}\""
        return "posted a message"
    
    def _describe_like_post(self) -> str:
        """Like post - contains post content and author info"""
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if post_content and post_author:
            return f"liked {post_author}'s post: \"{post_content}\""
        elif post_content:
            return f"liked a post: \"{post_content}\""
        elif post_author:
            return f"liked a post by {post_author}"
        return "liked a post"
    
    def _describe_dislike_post(self) -> str:
        """Dislike post - contains post content and author info"""
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if post_content and post_author:
            return f"disliked {post_author}'s post: \"{post_content}\""
        elif post_content:
            return f"disliked a post: \"{post_content}\""
        elif post_author:
            return f"disliked a post by {post_author}"
        return "disliked a post"
    
    def _describe_repost(self) -> str:
        """Repost post - contains original content and author info"""
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        
        if original_content and original_author:
            return f"reposted {original_author}'s post: \"{original_content}\""
        elif original_content:
            return f"reposted a post: \"{original_content}\""
        elif original_author:
            return f"reposted a post by {original_author}"
        return "reposted a post"
    
    def _describe_quote_post(self) -> str:
        """Quote post - contains original content, author info, and quote commentary"""
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        quote_content = self.action_args.get("quote_content", "") or self.action_args.get("content", "")
        
        base = ""
        if original_content and original_author:
            base = f"quoted {original_author}'s post \"{original_content}\""
        elif original_content:
            base = f"quoted a post \"{original_content}\""
        elif original_author:
            base = f"quoted a post by {original_author}"
        else:
            base = "quoted a post"
        
        if quote_content:
            base += f", commenting: \"{quote_content}\""
        return base
    
    def _describe_follow(self) -> str:
        """Follow user - contains followed user name"""
        target_user_name = self.action_args.get("target_user_name", "")
        
        if target_user_name:
            return f"followed user \"{target_user_name}\""
        return "followed a user"
    
    def _describe_create_comment(self) -> str:
        """Create comment - contains comment content and post info"""
        content = self.action_args.get("content", "")
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if content:
            if post_content and post_author:
                return f"commented on {post_author}'s post \"{post_content}\": \"{content}\""
            elif post_content:
                return f"commented on post \"{post_content}\": \"{content}\""
            elif post_author:
                return f"commented on {post_author}'s post: \"{content}\""
            return f"commented: \"{content}\""
        return "posted a comment"
    
    def _describe_like_comment(self) -> str:
        """Like comment - contains comment content and author info"""
        comment_content = self.action_args.get("comment_content", "")
        comment_author = self.action_args.get("comment_author_name", "")
        
        if comment_content and comment_author:
            return f"liked {comment_author}'s comment: \"{comment_content}\""
        elif comment_content:
            return f"liked a comment: \"{comment_content}\""
        elif comment_author:
            return f"liked a comment by {comment_author}"
        return "liked a comment"
    
    def _describe_dislike_comment(self) -> str:
        """Dislike comment - contains comment content and author info"""
        comment_content = self.action_args.get("comment_content", "")
        comment_author = self.action_args.get("comment_author_name", "")
        
        if comment_content and comment_author:
            return f"disliked {comment_author}'s comment: \"{comment_content}\""
        elif comment_content:
            return f"disliked a comment: \"{comment_content}\""
        elif comment_author:
            return f"disliked a comment by {comment_author}"
        return "disliked a comment"
    
    def _describe_search(self) -> str:
        """Search posts - contains search query"""
        query = self.action_args.get("query", "") or self.action_args.get("keyword", "")
        return f"searched for \"{query}\"" if query else "performed a search"
    
    def _describe_search_user(self) -> str:
        """Search users - contains search query"""
        query = self.action_args.get("query", "") or self.action_args.get("username", "")
        return f"searched for user \"{query}\"" if query else "searched for user"
    
    def _describe_mute(self) -> str:
        """Mute user - contains muted user name"""
        target_user_name = self.action_args.get("target_user_name", "")
        
        if target_user_name:
            return f"muted user \"{target_user_name}\""
        return "muted a user"
    
    def _describe_generic(self) -> str:
        # Generate generic description for unknown action types
        return f"performed {self.action_type} action"


class _DrainDeadlineExceeded(TimeoutError):
    def __init__(self, processed_count: int):
        super().__init__("Zep updater drain deadline elapsed")
        self.processed_count = processed_count


class ZepGraphMemoryUpdater:
    """
    Zep Graph Memory Updater
    
    Monitors simulation action logs and updates new agent activities into Zep in real time.
    Groups by platform, sending batches after accumulating BATCH_SIZE activities.
    
    All meaningful actions are updated to Zep with full context in action_args:
    - Liked / disliked post text
    - Reposted / quoted post text
    - Followed / muted usernames
    - Liked / disliked comment text
    """
    
    # Batch send size (activities accumulated per platform before sending)
    BATCH_SIZE = 5
    
    # Platform name mapping (for console display)
    PLATFORM_DISPLAY_NAMES = {
        'twitter': 'World 1',
        'reddit': 'World 2',
    }
    
    # Send interval (seconds) to prevent flooding requests
    SEND_INTERVAL = 0.5
    
    # Zep recommends keeping an episode below 10,000 characters. Leave room
    # for future source formatting changes.
    MAX_EPISODE_CHARS = 9_500
    
    def __init__(
        self,
        graph_id: str,
        api_key: Optional[str] = None,
        simulation_id: Optional[str] = None,
    ):
        """
        Initialize updater
        
        Args:
            graph_id: Zep graph ID
            api_key: Zep API Key (optional, read from config by default)
        """
        self.graph_id = graph_id
        self.simulation_id = simulation_id or "unknown"
        self.api_key = api_key or Config.ZEP_API_KEY
        
        if not self.api_key:
            raise ValueError("ZEP_API_KEY is not configured")
        
        self.client = get_zep_client(self.api_key)
        
        # Activity queue
        self._activity_queue: Queue = Queue()
        
        # Activity buffers grouped by platform (batched when reaching BATCH_SIZE)
        self._platform_buffers: Dict[str, List[AgentActivity]] = {
            'twitter': [],
            'reddit': [],
        }
        self._buffer_lock = threading.Lock()
        self._acceptance_lock = threading.Lock()
        
        # Control flags
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # Statistics
        self._total_activities = 0  # Total activities added to queue
        self._total_sent = 0        # Total batches sent to Zep
        self._total_items_sent = 0  # Total activities sent to Zep
        self._failed_count = 0      # Failed batches count
        self._skipped_count = 0     # Skipped activities count (DO_NOTHING)
        self._failed_batches: List[Dict[str, Any]] = []
        self._pending_episode_uuids: List[str] = []
        
        logger.info(f"ZepGraphMemoryUpdater initialized: graph_id={graph_id}, batch_size={self.BATCH_SIZE}")
    
    def _get_platform_display_name(self, platform: str) -> str:
        """Get display name for platform"""
        return self.PLATFORM_DISPLAY_NAMES.get(platform.lower(), platform)
    
    def start(self):
        """Start background worker thread"""
        if self._running:
            return

        # Capture locale before spawning background thread
        current_locale = get_locale()

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            args=(current_locale,),
            daemon=True,
            name=f"ZepMemoryUpdater-{self.graph_id[:8]}"
        )
        self._worker_thread.start()
        logger.info(f"ZepGraphMemoryUpdater started: graph_id={self.graph_id}")
    
    def stop(self):
        """Drain the worker, flush tail events, and wait for Cloud ingestion."""
        deadline = time.time() + ZEP_INGESTION_WAIT_TIMEOUT_SECONDS
        # Serialize the accepting->closed transition with add_activity's
        # check+enqueue operation. This closes the small race where a producer
        # could enqueue after both the worker and final flush had exited.
        with self._acceptance_lock:
            self._running = False

        if self._worker_thread and self._worker_thread.is_alive():
            join_timeout = max(0.0, deadline - time.time())
            self._worker_thread.join(timeout=join_timeout)
            if self._worker_thread.is_alive():
                raise TimeoutError(
                    f"Zep updater worker did not stop within {join_timeout:.0f}s"
                )

        # The worker has drained the queue. Only now is it safe to flush
        # buffers; doing this before join loses an item already dequeued by the
        # worker but not yet buffered.
        self._flush_remaining(deadline=deadline)

        if self._failed_batches:
            raise RuntimeError(
                f"{len(self._failed_batches)} Zep activity batch(es) failed; "
                "simulation graph ingestion is incomplete"
            )

        self._wait_for_pending_episodes(deadline=deadline)
        
        logger.info(f"ZepGraphMemoryUpdater stopped: graph_id={self.graph_id}, "
                   f"total_activities={self._total_activities}, "
                   f"batches_sent={self._total_sent}, "
                   f"items_sent={self._total_items_sent}, "
                   f"failed={self._failed_count}, "
                   f"skipped={self._skipped_count}")
    
    def add_activity(self, activity: AgentActivity):
        """
        Add an agent activity to the queue
        
        All meaningful behaviors are queued, including:
        - CREATE_POST (post)
        - CREATE_COMMENT (comment)
        - QUOTE_POST (quote post)
        - SEARCH_POSTS (search posts)
        - SEARCH_USER (search user)
        - LIKE_POST/DISLIKE_POST (like/dislike post)
        - REPOST (repost)
        - FOLLOW (follow)
        - MUTE (mute)
        - LIKE_COMMENT/DISLIKE_COMMENT (like/dislike comment)
        
        action_args includes complete context (post text, username, etc.).
        
        Args:
            activity: Agent activity record
        """
        # Skip DO_NOTHING type activities
        if activity.action_type == "DO_NOTHING":
            self._skipped_count += 1
            return

        with self._acceptance_lock:
            if not self._running:
                raise RuntimeError("Zep graph updater is not running")
            self._activity_queue.put(activity)
            self._total_activities += 1
        logger.debug(f"Added activity to Zep queue: {activity.agent_name} - {activity.action_type}")
    
    def add_activity_from_dict(self, data: Dict[str, Any], platform: str):
        """
        Add activity from dictionary data
        
        Args:
            data: Dict parsed from actions.jsonl
            platform: Platform name (twitter/reddit)
        """
        # Skip event-type entries
        if "event_type" in data:
            return
        if data.get("success") is False:
            self._skipped_count += 1
            return
        
        activity = AgentActivity(
            platform=platform,
            agent_id=data.get("agent_id", 0),
            agent_name=data.get("agent_name", ""),
            action_type=data.get("action_type", ""),
            action_args=data.get("action_args", {}),
            round_num=data.get("round", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )
        
        self.add_activity(activity)
    
    def _worker_loop(self, locale: str = 'zh'):
        """Background worker loop - batches and sends activities to Zep by platform"""
        set_locale(locale)
        while self._running or not self._activity_queue.empty():
            try:
                # Try to get activity from queue (timeout 1s)
                try:
                    activity = self._activity_queue.get(timeout=1)
                    
                    # Add activity to platform buffer
                    platform = activity.platform.lower()
                    batch = None
                    with self._buffer_lock:
                        if platform not in self._platform_buffers:
                            self._platform_buffers[platform] = []
                        self._platform_buffers[platform].append(activity)
                        
                        # Check if platform reached batch size
                        if len(self._platform_buffers[platform]) >= self.BATCH_SIZE:
                            batch = self._platform_buffers[platform][:self.BATCH_SIZE]
                            self._platform_buffers[platform] = self._platform_buffers[platform][self.BATCH_SIZE:]

                    # Never hold the buffer lock across network I/O or sleep.
                    if batch:
                        self._send_batch_activities(batch, platform)
                        time.sleep(self.SEND_INTERVAL)

                except Empty:
                    # Periodically check and clean up finished episodes while worker is idling
                    if self._pending_episode_uuids:
                        try:
                            pending_set = set(self._pending_episode_uuids)
                            self._poll_pending_batch(pending_set)
                            self._pending_episode_uuids = [u for u in self._pending_episode_uuids if u in pending_set]
                        except Exception:
                            pass
                    
            except Exception as e:
                logger.error(f"Worker loop exception: {e}")
                time.sleep(1)
    
    def _build_episode_payloads(
        self,
        activities: List[AgentActivity],
    ) -> List[tuple[List[AgentActivity], str]]:
        payloads: List[tuple[List[AgentActivity], str]] = []
        current_activities: List[AgentActivity] = []
        current_lines: List[str] = []
        current_length = 0

        for activity in activities:
            text = activity.to_episode_text()
            if len(text) > self.MAX_EPISODE_CHARS:
                marker = "... [truncated by Lokantra]"
                text = text[: self.MAX_EPISODE_CHARS - len(marker)] + marker
            projected_length = current_length + (1 if current_lines else 0) + len(text)
            if current_lines and projected_length > self.MAX_EPISODE_CHARS:
                payloads.append((current_activities, "\n".join(current_lines)))
                current_activities = []
                current_lines = []
                current_length = 0
            current_activities.append(activity)
            current_lines.append(text)
            current_length += (1 if len(current_lines) > 1 else 0) + len(text)

        if current_lines:
            payloads.append((current_activities, "\n".join(current_lines)))
        return payloads

    def _send_batch_activities(
        self,
        activities: List[AgentActivity],
        platform: str,
        *,
        deadline: float | None = None,
    ) -> int:
        """
        Batch send activities to Zep graph (merged into single text)
        
        Args:
            activities: Agent activity list
            platform: Platform name
        """
        if not activities:
            return 0

        processed_count = 0
        for payload_activities, combined_text in self._build_episode_payloads(activities):
            if deadline is not None and time.time() >= deadline:
                raise _DrainDeadlineExceeded(processed_count)
            try:
                episode = self.client.graph.add(
                    graph_id=self.graph_id,
                    type="text",
                    data=combined_text,
                    created_at=self._to_rfc3339(payload_activities[-1].timestamp),
                    source_description="Lokantra simulation activity batch",
                    metadata={
                        "source": "lokantra_simulation",
                        "simulation_id": self.simulation_id,
                        "platform": platform,
                        "activity_count": len(payload_activities),
                        "first_round": min(a.round_num for a in payload_activities),
                        "last_round": max(a.round_num for a in payload_activities),
                        "agent_ids": ",".join(
                            str(value)
                            for value in sorted({a.agent_id for a in payload_activities})
                        ),
                        "action_types": ",".join(
                            value
                            for value in sorted({a.action_type for a in payload_activities})
                            if value
                        ) or "unknown",
                    },
                )

                episode_uuid = (
                    getattr(episode, "uuid_", None)
                    or getattr(episode, "uuid", None)
                )
                if not episode_uuid:
                    raise RuntimeError("Zep graph.add returned no episode UUID")
                self._pending_episode_uuids.append(str(episode_uuid))
                self._total_sent += 1
                self._total_items_sent += len(payload_activities)
                display_name = self._get_platform_display_name(platform)
                logger.info(f"Successfully batch sent {len(payload_activities)} {display_name} activities to graph {self.graph_id}")
                logger.debug(f"Batch content preview: {combined_text[:200]}...")

            except Exception as e:
                # graph.add has no idempotency key. Replaying an ambiguous
                # response can duplicate extracted facts, so fail closed and
                # surface the incomplete batch to SimulationRunner.
                logger.error(f"Batch send to Zep failed, non-idempotent write not retried: {e}")
                self._failed_count += 1
                self._failed_batches.append({
                    "platform": platform,
                    "activities": payload_activities,
                    "error": str(e),
                })
            finally:
                # Successes have a confirmed episode UUID; failures are kept
                # durably in _failed_batches and must never be replayed. Either
                # way this payload is accounted for before moving on.
                processed_count += len(payload_activities)
        return processed_count

    @staticmethod
    def _to_rfc3339(value: str) -> str:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.astimezone()
            return parsed.isoformat()
        except (AttributeError, TypeError, ValueError):
            return datetime.now().astimezone().isoformat()

    def _flush_remaining(self, *, deadline: float | None = None):
        """Send remaining activities in queue and buffer"""
        # Process remaining queue activities into buffer
        while not self._activity_queue.empty():
            try:
                activity = self._activity_queue.get_nowait()
                platform = activity.platform.lower()
                with self._buffer_lock:
                    if platform not in self._platform_buffers:
                        self._platform_buffers[platform] = []
                    self._platform_buffers[platform].append(activity)
            except Empty:
                break
        
        for platform in list(self._platform_buffers):
            with self._buffer_lock:
                buffer = list(self._platform_buffers.get(platform, []))
            if not buffer:
                continue
            display_name = self._get_platform_display_name(platform)
            logger.info(f"Sending {len(buffer)} remaining activities for {display_name}")
            if deadline is not None and time.time() >= deadline:
                raise TimeoutError(
                    "Zep updater drain deadline elapsed before flushing all activities"
                )
            try:
                processed_count = self._send_batch_activities(
                    buffer,
                    platform,
                    deadline=deadline,
                )
            except _DrainDeadlineExceeded as error:
                with self._buffer_lock:
                    del self._platform_buffers[platform][:error.processed_count]
                raise TimeoutError(str(error)) from error
            else:
                with self._buffer_lock:
                    del self._platform_buffers[platform][:processed_count]

    def _poll_pending_batch(self, pending: set) -> None:
        """Poll pending episodes using efficient batch status retrieval where possible."""
        try:
            res = self.client.graph.episode.get_by_graph_id(
                graph_id=self.graph_id,
                lastn=min(100, max(len(pending) * 2, 20)),
            )
            episodes = getattr(res, "episodes", []) or []
            if episodes:
                uuid_map = {}
                for ep in episodes:
                    ep_id = getattr(ep, "uuid_", getattr(ep, "uuid", None))
                    if ep_id:
                        uuid_map[str(ep_id)] = getattr(ep, "processed", False)
                for episode_uuid in list(pending):
                    if uuid_map.get(str(episode_uuid)) is True:
                        pending.remove(episode_uuid)
                return
        except Exception as e:
            logger.debug(f"Batch episode status check fallback: {e}")

        for episode_uuid in list(pending):
            episode = call_zep_read_with_retry(
                lambda: self.client.graph.episode.get(uuid_=episode_uuid),
                operation_name=f"poll simulation episode {episode_uuid}",
            )
            if getattr(episode, "processed", False):
                pending.remove(episode_uuid)

    def _wait_for_pending_episodes(self, *, deadline: float | None = None) -> None:
        pending = set(self._pending_episode_uuids)
        if not pending:
            return

        if deadline is None:
            deadline = time.time() + ZEP_INGESTION_WAIT_TIMEOUT_SECONDS
        while pending:
            if time.time() >= deadline:
                raise TimeoutError(
                    f"Zep simulation ingestion timed out with {len(pending)} "
                    "episode(s) pending"
                )
            self._poll_pending_batch(pending)
            if pending:
                time.sleep(3)
        self._pending_episode_uuids = []
    
    def is_active(self) -> bool:
        """Check if updater is actively processing or worker is alive"""
        worker_alive = bool(self._worker_thread and self._worker_thread.is_alive())
        return self._running or worker_alive or not self._activity_queue.empty()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        with self._buffer_lock:
            buffer_sizes = {p: len(b) for p, b in self._platform_buffers.items()}
        
        return {
            "graph_id": self.graph_id,
            "batch_size": self.BATCH_SIZE,
            "total_activities": self._total_activities,  # Total activities added to queue
            "batches_sent": self._total_sent,            # Batches successfully sent
            "items_sent": self._total_items_sent,        # Items successfully sent
            "failed_count": self._failed_count,          # Failed batches
            "pending_episode_count": len(self._pending_episode_uuids),
            "skipped_count": self._skipped_count,        # Filtered activities count (DO_NOTHING)
            "queue_size": self._activity_queue.qsize(),
            "buffer_sizes": buffer_sizes,                # Buffer sizes per platform
            "running": self._running,
        }


class ZepGraphMemoryManager:
    """
    Manages Zep Graph Memory Updaters for multiple simulations
    
    Each simulation can have its own updater instance
    """
    
    _updaters: Dict[str, ZepGraphMemoryUpdater] = {}
    _lock = threading.Lock()

    @classmethod
    def force_remove_updater(cls, simulation_id: str) -> Optional["ZepGraphMemoryUpdater"]:
        """Forcefully remove updater from registry (e.g. after worker stopped or during recovery)"""
        with cls._lock:
            updater = cls._updaters.pop(simulation_id, None)
            if updater:
                logger.info(f"Force removed graph memory updater: simulation_id={simulation_id}")
            return updater
    
    @classmethod
    def create_updater(cls, simulation_id: str, graph_id: str) -> ZepGraphMemoryUpdater:
        """
        Create graph memory updater for simulation
        
        Args:
            simulation_id: Simulation ID
            graph_id: Zep graph ID
            
        Returns:
            ZepGraphMemoryUpdater instance
        """
        with cls._lock:
            # If already exists, stop the previous one
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
            
            updater = ZepGraphMemoryUpdater(
                graph_id,
                simulation_id=simulation_id,
            )
            updater.start()
            cls._updaters[simulation_id] = updater
            cls._stop_all_done = False
            
            logger.info(f"Created graph memory updater: simulation_id={simulation_id}, graph_id={graph_id}")
            return updater
    
    @classmethod
    def get_updater(cls, simulation_id: str) -> Optional[ZepGraphMemoryUpdater]:
        """Get updater for simulation"""
        with cls._lock:
            return cls._updaters.get(simulation_id)

    @classmethod
    def get_simulation_ids_for_graph(cls, graph_id: str) -> List[str]:
        """Return simulations whose updater still owns or drains this graph."""

        with cls._lock:
            return sorted(
                simulation_id
                for simulation_id, updater in cls._updaters.items()
                if updater.graph_id == graph_id
            )

    @classmethod
    def get_simulation_ids(cls) -> List[str]:
        """Return every simulation with a retained updater."""

        with cls._lock:
            return sorted(cls._updaters)

    @classmethod
    def discard_inactive_updater(cls, simulation_id: str) -> bool:
        """Discard a failed, fully stopped updater during graph destruction."""

        with cls._lock:
            updater = cls._updaters.get(simulation_id)
            if updater is None:
                return False
            worker_alive = bool(
                updater._worker_thread and updater._worker_thread.is_alive()
            )
            if updater._running or worker_alive:
                raise RuntimeError(
                    f"Zep updater for {simulation_id} is still active"
                )
            cls._updaters.pop(simulation_id, None)
        logger.warning(
            "Discarded incomplete Zep updater during explicit graph deletion: "
            "simulation_id=%s, graph_id=%s",
            simulation_id,
            updater.graph_id,
        )
        return True
    
    @classmethod
    def stop_updater(cls, simulation_id: str):
        """Stop and remove updater for simulation"""
        with cls._lock:
            updater = cls._updaters.get(simulation_id)
        if updater is None:
            return

        # Do not hold the manager lock through up to several minutes of Cloud
        # polling. Crucially, only remove the updater after a successful drain;
        # on failure it remains visible to report/deletion barriers and can be
        # stopped again.
        updater.stop()
        with cls._lock:
            if cls._updaters.get(simulation_id) is updater:
                cls._updaters.pop(simulation_id, None)
        logger.info(f"Stopped graph memory updater: simulation_id={simulation_id}")
    
    # Flag to prevent duplicate stop_all calls
    _stop_all_done = False
    
    @classmethod
    def stop_all(cls):
        """Stop all updaters"""
        # Prevent duplicate calls
        if cls._stop_all_done:
            return

        with cls._lock:
            simulation_ids = list(cls._updaters)

        errors = []
        for simulation_id in simulation_ids:
            try:
                cls.stop_updater(simulation_id)
            except Exception as error:
                # Keep a failed updater registered so the caller can retry and
                # lifecycle/report guards still see the incomplete ingestion.
                logger.error(
                    "Failed to stop updater: simulation_id=%s, error=%s",
                    simulation_id,
                    error,
                )
                errors.append((simulation_id, error))

        with cls._lock:
            cls._stop_all_done = not cls._updaters

        if errors:
            details = "; ".join(
                f"{simulation_id}: {error}"
                for simulation_id, error in errors
            )
            raise RuntimeError(f"Some graph memory updaters did not stop cleanly: {details}")
        logger.info("All graph memory updaters stopped")
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all updaters"""
        return {
            sim_id: updater.get_stats() 
            for sim_id, updater in cls._updaters.items()
        }
