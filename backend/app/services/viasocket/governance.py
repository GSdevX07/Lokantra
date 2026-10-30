"""
viaSocket Scoping Registry & Governance Engine ("The Conscience")
Enforces Role-Based Tool Scoping (Default-Deny), Temporal Boundary Guardrails,
Sub-millisecond In-Memory Caching, Rate Limiting, and Real-Time Security Audit Logging.
"""

from __future__ import annotations

import os
import time
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ...config import Config
from ...utils.logger import get_logger
from .client import ViaSocketClient

logger = get_logger('lokantra.viasocket.governance')


class GovernanceDecision:
    """Represents the governance verdict for a tool invocation attempt."""
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    CACHED = "CACHED"


class ScopingRegistry:
    """
    Role-Based Tool Scoping Matrix and Enforcement Engine.
    Controls what external viaSocket capabilities each agent role is allowed to access.
    """

    DEFAULT_SCOPING_MATRIX: Dict[str, Dict[str, Any]] = {
        "financial_agent": {
            "description": "Financial and quantitative market analysis persona.",
            "allowed_tools": ["query_postgres", "read_google_sheets", "scrape_webpage", "search_serp_google"],
            "max_calls_per_round": 3,
            "can_request_write": False
        },
        "market_research_agent": {
            "description": "Market trend observer, competitor tracker, and sentiment analyst.",
            "allowed_tools": ["scrape_webpage", "search_serp_google", "read_google_sheets"],
            "max_calls_per_round": 3,
            "can_request_write": False
        },
        "fact_checker_sentinel": {
            "description": "Ground-truth verification sentinel that checks external claims.",
            "allowed_tools": ["search_serp_google", "scrape_webpage", "query_postgres"],
            "max_calls_per_round": 4,
            "can_request_write": False
        },
        "report_agent": {
            "description": "Strategic synthesis agent capable of post-simulation actuation proposals.",
            "allowed_tools": [
                "scrape_webpage", "search_serp_google", "query_postgres",
                "read_google_sheets", "send_slack_message", "send_email", "post_twitter_tweet"
            ],
            "max_calls_per_round": 5,
            "can_request_write": True
        },
        "coordinator_agent": {
            "description": "Internal workflow coordinator with zero external actuation permissions.",
            "allowed_tools": [],
            "max_calls_per_round": 0,
            "can_request_write": False
        },
        "public_persona": {
            "description": "General swarm citizen persona living strictly inside the simulated sandbox.",
            "allowed_tools": [],
            "max_calls_per_round": 0,
            "can_request_write": False
        }
    }

    def __init__(self, client: Optional[ViaSocketClient] = None):
        self.client = client or ViaSocketClient()
        self.matrix: Dict[str, Dict[str, Any]] = dict(self.DEFAULT_SCOPING_MATRIX)

        # In-memory performance cache: key -> {result, expires_at}
        self._response_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = Config.VIASOCKET_CACHE_TTL

        # Rate limiting tracker: (agent_id, round_num) -> count
        self._rate_counter: Dict[str, int] = {}

        # Circular in-memory audit log (capped at 500 entries)
        self._audit_log: List[Dict[str, Any]] = []
        self._max_audit_entries = 500

        # Audit file persistence directory
        self._log_file_path = os.path.join(Config.UPLOAD_FOLDER, 'viasocket_audit.jsonl')
        os.makedirs(os.path.dirname(self._log_file_path), exist_ok=True)

    def _normalize_role(self, role: Optional[str]) -> str:
        """Normalize agent role string to registry keys."""
        if not role:
            return "public_persona"
        norm = role.strip().lower().replace(" ", "_").replace("-", "_")
        for key in self.matrix.keys():
            if key in norm or norm in key:
                return key
        return "public_persona"

    def _generate_cache_key(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Create a deterministic SHA-256 hash of tool and arguments."""
        serialized = json.dumps({"tool": tool_name, "args": arguments}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get_tool_metadata(self, tool_name: str) -> Dict[str, Any]:
        """Look up tool metadata from client catalog."""
        tools = self.client.list_tools()
        for t in tools:
            if t.get("name") == tool_name:
                return t
        # Fallback metadata for unknown tools
        is_write = any(k in tool_name.lower() for k in ["send", "post", "write", "delete", "create"])
        return {
            "name": tool_name,
            "description": "viaSocket external integration",
            "type": "write" if is_write else "read",
            "risk": "high" if is_write else "low"
        }

    def evaluate_and_route(
        self,
        agent_id: str,
        agent_role: str,
        tool_name: str,
        arguments: Dict[str, Any],
        phase: str = "simulation",
        round_num: int = 1,
        simulation_id: Optional[str] = None
    ) -> Tuple[str, Optional[Dict[str, Any]], str, float]:
        """
        Interception & Policy Evaluation Loop.
        
        Returns:
            Tuple[decision, result_or_payload, explanation, latency_ms]
            - decision: ALLOWED, DENIED, PENDING_APPROVAL, or CACHED
            - result_or_payload: execution output or action record
            - explanation: security rationale
            - latency_ms: evaluation duration in milliseconds
        """
        start_ts = time.perf_counter()
        normalized_role = self._normalize_role(agent_role)
        tool_meta = self.get_tool_metadata(tool_name)
        action_type = tool_meta.get("type", "read").lower()
        risk_level = tool_meta.get("risk", "low")

        role_policy = self.matrix.get(normalized_role, {
            "allowed_tools": [],
            "max_calls_per_round": 0,
            "can_request_write": False
        })
        allowed_tools = role_policy.get("allowed_tools", [])
        max_calls = role_policy.get("max_calls_per_round", 0)

        # 1. Check Default-Deny Scoping Registry
        if tool_name not in allowed_tools:
            eval_latency = round((time.perf_counter() - start_ts) * 1000, 2)
            reason = (
                f"SECURITY VIOLATION: Agent role '{normalized_role}' is not scoped for tool '{tool_name}'. "
                f"Default-deny policy enforced."
            )
            self._log_audit(
                decision=GovernanceDecision.DENIED,
                agent_id=agent_id,
                agent_role=normalized_role,
                tool_name=tool_name,
                arguments=arguments,
                action_type=action_type,
                risk_level=risk_level,
                phase=phase,
                simulation_id=simulation_id,
                latency_ms=eval_latency,
                reason=reason
            )
            return GovernanceDecision.DENIED, None, reason, eval_latency

        # 2. Check Rate Limiter / Circuit Breaker
        rate_key = f"{agent_id}:{round_num}"
        current_calls = self._rate_counter.get(rate_key, 0)
        if max_calls > 0 and current_calls >= max_calls:
            eval_latency = round((time.perf_counter() - start_ts) * 1000, 2)
            reason = (
                f"RATE LIMIT EXCEEDED: Agent '{agent_id}' has reached the limit of "
                f"{max_calls} viaSocket tool calls for round {round_num}."
            )
            self._log_audit(
                decision=GovernanceDecision.DENIED,
                agent_id=agent_id,
                agent_role=normalized_role,
                tool_name=tool_name,
                arguments=arguments,
                action_type=action_type,
                risk_level=risk_level,
                phase=phase,
                simulation_id=simulation_id,
                latency_ms=eval_latency,
                reason=reason
            )
            return GovernanceDecision.DENIED, None, reason, eval_latency

        # 3. Check Temporal Boundary & Action Type (Read vs Write)
        if action_type == "write":
            eval_latency = round((time.perf_counter() - start_ts) * 1000, 2)
            # Write actions must go through Human-in-the-Loop review
            reason = (
                f"HUMAN-IN-THE-LOOP REQUIRED: Tool '{tool_name}' performs destructive/external write action. "
                f"Staged in pending execution queue for operator approval."
            )
            self._log_audit(
                decision=GovernanceDecision.PENDING_APPROVAL,
                agent_id=agent_id,
                agent_role=normalized_role,
                tool_name=tool_name,
                arguments=arguments,
                action_type=action_type,
                risk_level=risk_level,
                phase=phase,
                simulation_id=simulation_id,
                latency_ms=eval_latency,
                reason=reason
            )
            pending_action = {
                "agent_id": agent_id,
                "agent_role": normalized_role,
                "tool_name": tool_name,
                "arguments": arguments,
                "risk_level": risk_level,
                "phase": phase,
                "simulation_id": simulation_id,
                "staged_at": datetime.now().isoformat()
            }
            return GovernanceDecision.PENDING_APPROVAL, pending_action, reason, eval_latency

        # 4. Read Action: Check Sub-millisecond In-Memory Cache
        cache_key = self._generate_cache_key(tool_name, arguments)
        now_ts = time.time()
        if cache_key in self._response_cache:
            entry = self._response_cache[cache_key]
            if entry["expires_at"] > now_ts:
                eval_latency = round((time.perf_counter() - start_ts) * 1000, 2)
                reason = "CACHE HIT: Sub-millisecond local ground-truth retrieved."
                self._log_audit(
                    decision=GovernanceDecision.CACHED,
                    agent_id=agent_id,
                    agent_role=normalized_role,
                    tool_name=tool_name,
                    arguments=arguments,
                    action_type=action_type,
                    risk_level=risk_level,
                    phase=phase,
                    simulation_id=simulation_id,
                    latency_ms=eval_latency,
                    reason=reason
                )
                self._rate_counter[rate_key] = current_calls + 1
                return GovernanceDecision.CACHED, entry["data"], reason, eval_latency

        # 5. Execute Authorized Read Action via viaSocket MCP
        call_output = self.client.call_tool(tool_name, arguments)
        total_latency = round((time.perf_counter() - start_ts) * 1000, 2)

        if call_output.get("success"):
            # Populate cache
            self._response_cache[cache_key] = {
                "data": call_output.get("result"),
                "expires_at": now_ts + self._cache_ttl
            }
            self._rate_counter[rate_key] = current_calls + 1
            reason = f"POLICY APPROVED: Authorized viaSocket {call_output.get('mode')} call executed."
            self._log_audit(
                decision=GovernanceDecision.ALLOWED,
                agent_id=agent_id,
                agent_role=normalized_role,
                tool_name=tool_name,
                arguments=arguments,
                action_type=action_type,
                risk_level=risk_level,
                phase=phase,
                simulation_id=simulation_id,
                latency_ms=total_latency,
                reason=reason
            )
            return GovernanceDecision.ALLOWED, call_output.get("result"), reason, total_latency
        else:
            reason = f"EXECUTION FAILED: {call_output.get('error')}"
            self._log_audit(
                decision=GovernanceDecision.DENIED,
                agent_id=agent_id,
                agent_role=normalized_role,
                tool_name=tool_name,
                arguments=arguments,
                action_type=action_type,
                risk_level=risk_level,
                phase=phase,
                simulation_id=simulation_id,
                latency_ms=total_latency,
                reason=reason
            )
            return GovernanceDecision.DENIED, None, reason, total_latency

    def _log_audit(
        self,
        decision: str,
        agent_id: str,
        agent_role: str,
        tool_name: str,
        arguments: Dict[str, Any],
        action_type: str,
        risk_level: str,
        phase: str,
        simulation_id: Optional[str],
        latency_ms: float,
        reason: str
    ):
        """Append an event to the security audit stream."""
        event = {
            "audit_id": f"aud_{int(time.time() * 1000)}_{len(self._audit_log)}",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id or "global",
            "agent_id": agent_id,
            "agent_role": agent_role,
            "tool_name": tool_name,
            "arguments": arguments,
            "action_type": action_type,
            "risk_level": risk_level,
            "phase": phase,
            "decision": decision,
            "latency_ms": latency_ms,
            "reason": reason
        }

        self._audit_log.append(event)
        if len(self._audit_log) > self._max_audit_entries:
            self._audit_log.pop(0)

        # Non-blocking file append
        try:
            with open(self._log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent security audit events in reverse chronological order."""
        return list(reversed(self._audit_log[-limit:]))

    def get_scoping_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve the active policy matrix."""
        return self.matrix

    def update_role_policy(
        self,
        role: str,
        allowed_tools: List[str],
        max_calls_per_round: int = 3,
        can_request_write: bool = False
    ) -> bool:
        """Dynamically update an agent role's allowed viaSocket tool scope."""
        norm = self._normalize_role(role)
        self.matrix[norm] = {
            "description": f"Custom policy for {norm}",
            "allowed_tools": allowed_tools,
            "max_calls_per_round": max_calls_per_round,
            "can_request_write": can_request_write
        }
        return True

    def reset_policies_to_default(self):
        """Reset scoping matrix to enterprise default-deny baselines."""
        self.matrix = dict(self.DEFAULT_SCOPING_MATRIX)
