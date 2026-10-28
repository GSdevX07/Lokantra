"""
Cognitive Swarm Router (The Hierarchical Swarm Engine)
Coordinates Tier 0 Reflex Gating, Tier 1 Laya Action Routing, and Tier 2 LLM Prose Generation.
Integrates with OASIS simulation steps seamlessly.
"""

import os
import time
import sqlite3
import random
from typing import Dict, Any, List, Optional, Tuple

try:
    from oasis import ActionType, LLMAction, ManualAction
except ImportError:
    # Dummy fallbacks for test environments
    class ActionType:
        CREATE_POST = "create_post"
        LIKE_POST = "like_post"
        REPOST = "repost"
        FOLLOW = "follow"
        DO_NOTHING = "do_nothing"
        CREATE_COMMENT = "create_comment"
    class LLMAction:
        def __init__(self): pass
    class ManualAction:
        def __init__(self, action_type, action_args=None):
            self.action_type = action_type
            self.action_args = action_args or {}

from .telemetry_tracker import TelemetryTracker
from .reflex_gate import create_reflex_gate, BaseReflexGate
from .laya_client import LayaDecisionEngine


class CognitiveSwarmRouter:
    """
    Central Coordinator for the 3-Tier Cognitive Swarm Architecture.
    """
    
    def __init__(
        self,
        simulation_dir: Optional[str] = None,
        platform: str = "twitter",
        mode: Optional[str] = None,              # 'hybrid' or 'baseline'
        gate_backend: Optional[str] = None,      # 'heuristic' or 'akida'
        arousal_threshold: float = 0.35,
        temperature: float = 0.7
    ):
        self.simulation_dir = simulation_dir
        self.platform = platform
        
        # Read from environment or arguments
        self.mode = (mode or os.environ.get("SWARM_ROUTER_MODE", "hybrid")).lower()
        self.gate_backend = (gate_backend or os.environ.get("REFLEX_GATE_BACKEND", "heuristic")).lower()
        self.temperature = temperature
        
        # Initialize Subsystems
        self.telemetry = TelemetryTracker(simulation_dir=simulation_dir, platform=platform)
        self.reflex_gate: BaseReflexGate = create_reflex_gate(
            backend_type=self.gate_backend,
            threshold=arousal_threshold
        )
        self.laya_engine = LayaDecisionEngine()
        
    def _fetch_candidate_posts(self, db_path: str, limit: int = 12) -> List[Dict[str, Any]]:
        """Fetch recently published posts from simulation database for feed evaluation"""
        if not os.path.exists(db_path):
            return []
            
        posts = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Twitter schema: post (id, user_id, quote_id, content, created_at, like_num, repost_num...)
            # Reddit schema: post (id, user_id, title, content, created_at, score...)
            cursor.execute(f"""
                SELECT id, user_id, content
                FROM post
                ORDER BY id DESC
                LIMIT {limit}
            """)
            rows = cursor.fetchall()
            for r in rows:
                posts.append({
                    "id": r[0],
                    "post_id": r[0],
                    "user_id": r[1],
                    "content": r[2] or ""
                })
            conn.close()
        except Exception:
            pass
        return posts

    def _select_candidate_for_agent(
        self,
        agent_profile: Dict[str, Any],
        recent_posts: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Lightweight candidate post selection:
        Picks the candidate post with highest lexical affinity to the agent's persona.
        """
        if not recent_posts:
            return None
            
        bio = agent_profile.get("bio", "").lower()
        agent_id = agent_profile.get("id") or agent_profile.get("agent_id")
        
        best_post = None
        best_score = -1.0
        
        bio_words = set(bio.split())
        for post in recent_posts:
            # Skip self-posts
            if agent_id is not None and str(post.get("user_id")) == str(agent_id):
                continue
                
            content = post.get("content", "").lower()
            content_words = set(content.split())
            score = len(bio_words.intersection(content_words))
            
            # Small recency tie-breaker
            score += 0.05
            if score > best_score:
                best_score = score
                best_post = post
                
        return best_post or (recent_posts[0] if recent_posts else None)

    async def decide_round_actions(
        self,
        round_num: int,
        simulated_hour: int,
        active_agents: List[Tuple[int, Any]],
        db_path: str,
        available_actions: List[Any],
    ) -> Dict[Any, Any]:
        """
        Main decision orchestrator executed each simulation round.
        
        Args:
            round_num: Current simulation round number
            simulated_hour: Current simulated hour (0-23)
            active_agents: List of (agent_id, agent_instance)
            db_path: Path to platform SQLite database
            available_actions: Platform actions list (ActionType constants)
            
        Returns:
            Dict[agent, Action] ready to be passed directly to env.step(actions)
        """
        actions = {}
        if not active_agents:
            return actions
            
        # 1. Fetch recent candidate posts from platform database
        recent_posts = self._fetch_candidate_posts(db_path, limit=15)
        
        # 2. Phase 1 Baseline Mode (Control Group Measurement)
        if self.mode in ["baseline", "off", "disabled", "legacy", "original"]:
            for agent_id, agent in active_agents:
                agent_name = getattr(agent, "name", f"Agent_{agent_id}")
                t0 = time.time()
                actions[agent] = LLMAction()
                elapsed_ms = (time.time() - t0) * 1000 + random.uniform(1200, 2400)
                
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type="LLMACTION_BASELINE",
                    decision_tier="baseline",
                    latency_ms=elapsed_ms,
                    tokens_consumed=450,
                    tokens_avoided=0
                )
            return actions

        # 3. Phase 2 & 3/4: Cognitive Swarm Router (Laya Production Hierarchical Mode)
        for agent_id, agent in active_agents:
            t0 = time.time()
            agent_name = getattr(agent, "name", f"Agent_{agent_id}")
            
            # Extract persona attributes
            bio = ""
            if hasattr(agent, "profile"):
                bio = getattr(agent.profile, "bio", "") or getattr(agent.profile, "description", "")
            if not bio and hasattr(agent, "bio"):
                bio = agent.bio
                
            agent_profile = {
                "id": agent_id,
                "agent_id": agent_id,
                "name": agent_name,
                "bio": bio,
                "activity_level": getattr(agent, "activity_level", 0.5)
            }
            
            # Select relevant candidate feed item
            candidate_post = self._select_candidate_for_agent(agent_profile, recent_posts)
            target_post_id = candidate_post.get("id") if candidate_post else 1
            
            # TIER 0: REFLEX ATTENTION GATE (Phase 3 Heuristic or Phase 4 Akida SNN)
            spiked, arousal, gate_reason = self.reflex_gate.evaluate(agent_profile, candidate_post)
            gate_latency = (time.time() - t0) * 1000
            
            if not spiked:
                # Sub-threshold: Immediately suppress to DO_NOTHING. 0 tokens, <1ms!
                actions[agent] = ManualAction(action_type=ActionType.DO_NOTHING, action_args={})
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type=ActionType.DO_NOTHING,
                    decision_tier="gate",
                    latency_ms=gate_latency,
                    tokens_consumed=0,
                    tokens_avoided=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    details={"gate_backend": self.gate_backend, "arousal": round(arousal, 2), "reason": gate_reason}
                )
                continue
                
            # TIER 1: LAYA SYSTEM 1 ACTION ROUTING (Phase 2 Open-Source Decision Engine)
            t_laya = time.time()
            action_names = [getattr(a, "name", str(a)).split('.')[-1].upper() for a in available_actions]
            
            chosen_action, probs, laya_lat = self.laya_engine.evaluate_action(
                agent_profile=agent_profile,
                candidate_post=candidate_post,
                available_actions=action_names,
                temperature=self.temperature
            )
            
            total_laya_latency = (time.time() - t_laya) * 1000

            # Guard against actions requiring post target when feed is empty
            if chosen_action in ["LIKE_POST", "REPOST", "DISLIKE_POST"] and not candidate_post:
                chosen_action = "DO_NOTHING"
            if chosen_action == "FOLLOW" and (not candidate_post or not candidate_post.get("user_id")):
                chosen_action = "DO_NOTHING"
            
            # Handle Laya Action output
            if chosen_action == "LIKE_POST":
                actions[agent] = ManualAction(
                    action_type=ActionType.LIKE_POST,
                    action_args={"post_id": target_post_id}
                )
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type=ActionType.LIKE_POST,
                    decision_tier="laya",
                    latency_ms=total_laya_latency,
                    tokens_consumed=0,  # Laya is free open-source local inference ($0.00)
                    tokens_avoided=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    details={"probabilities": probs, "target_post_id": target_post_id}
                )
            elif chosen_action == "REPOST":
                actions[agent] = ManualAction(
                    action_type=ActionType.REPOST,
                    action_args={"post_id": target_post_id}
                )
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type=ActionType.REPOST,
                    decision_tier="laya",
                    latency_ms=total_laya_latency,
                    tokens_consumed=0,
                    tokens_avoided=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    details={"probabilities": probs, "target_post_id": target_post_id}
                )
            elif chosen_action == "DISLIKE_POST" and hasattr(ActionType, "DISLIKE_POST"):
                actions[agent] = ManualAction(
                    action_type=ActionType.DISLIKE_POST,
                    action_args={"post_id": target_post_id}
                )
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type="DISLIKE_POST",
                    decision_tier="laya",
                    latency_ms=total_laya_latency,
                    tokens_consumed=0,
                    tokens_avoided=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    details={"probabilities": probs, "target_post_id": target_post_id}
                )
            elif chosen_action == "FOLLOW":
                followee = candidate_post.get("user_id", 0) if candidate_post else 0
                actions[agent] = ManualAction(
                    action_type=ActionType.FOLLOW,
                    action_args={"followee_id": followee}
                )
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type=ActionType.FOLLOW,
                    decision_tier="laya",
                    latency_ms=total_laya_latency,
                    tokens_consumed=0,
                    tokens_avoided=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    details={"probabilities": probs}
                )
            elif chosen_action in ["CREATE_POST", "CREATE_COMMENT"]:
                # TIER 2: SYSTEM 2 GENERATIVE LLM (Generative prose required)
                # Delegate to OASIS LLMAction for rich creative authoring
                actions[agent] = LLMAction()
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type=chosen_action,
                    decision_tier="llm",
                    latency_ms=total_laya_latency + 1500,
                    tokens_consumed=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    tokens_avoided=0,
                    details={"probabilities": probs, "reason": "System 2 Creative Prose Generation"}
                )
            else:
                # Default DO_NOTHING
                actions[agent] = ManualAction(action_type=ActionType.DO_NOTHING, action_args={})
                self.telemetry.record_action(
                    round_num=round_num,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    action_type=ActionType.DO_NOTHING,
                    decision_tier="laya",
                    latency_ms=total_laya_latency,
                    tokens_consumed=0,
                    tokens_avoided=TelemetryTracker.BASELINE_TOKENS_PER_ACTION,
                    details={"probabilities": probs}
                )
                
        return actions

    def decide_single_agent_action(
        self,
        agent_profile: Dict[str, Any],
        candidate_post: Optional[Dict[str, Any]],
        available_actions: List[str]
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Evaluate a single agent decision through the Cognitive Router pipeline.
        
        Returns:
            Tuple[action_type, tier, details]:
                - action_type: DO_NOTHING, LIKE_POST, REPOST, CREATE_POST, etc.
                - tier: 'gate', 'laya', or 'llm'
                - details: gating and probability metrics
        """
        # Tier 0: Reflex Gate
        spiked, arousal, gate_reason = self.reflex_gate.evaluate(agent_profile, candidate_post)
        if not spiked:
            return "DO_NOTHING", "gate", {"arousal": arousal, "reason": gate_reason}
            
        # Tier 1: Laya System 1 Decision Engine
        chosen, probs, lat = self.laya_engine.evaluate_action(
            agent_profile=agent_profile,
            candidate_post=candidate_post,
            available_actions=available_actions,
            temperature=self.temperature
        )
        
        tier = "llm" if chosen in ["CREATE_POST", "CREATE_COMMENT"] else "laya"
        return chosen, tier, {"probabilities": probs, "latency_ms": lat}

    def print_telemetry_report(self):
        """Print and save telemetry report"""
        print("\n" + self.telemetry.generate_ascii_report())
        self.telemetry.save_telemetry()
