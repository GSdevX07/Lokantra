"""
Human-in-the-Loop (HITL) Execution Engine
Manages staged write/destructive actions, operator approvals, and safe execution dispatch.
"""

from __future__ import annotations

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...utils.logger import get_logger
from .client import ViaSocketClient
from .governance import ScopingRegistry, GovernanceDecision

logger = get_logger('lokantra.viasocket.hitl')


class HITLActionStatus:
    PENDING = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class HITLActionQueue:
    """
    Queue and review manager for destructive or external side-effect actions.
    Ensures no autonomous agent can execute write actions without human validation.
    """

    def __init__(self, client: Optional[ViaSocketClient] = None, governance: Optional[ScopingRegistry] = None):
        self.client = client or ViaSocketClient()
        self.governance = governance or ScopingRegistry(self.client)
        self._actions: Dict[str, Dict[str, Any]] = {}

    def stage_action(
        self,
        agent_id: str,
        agent_role: str,
        tool_name: str,
        arguments: Dict[str, Any],
        predicted_outcome: Optional[str] = None,
        risk_level: Optional[str] = None,
        simulation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Stage an action into the queue waiting for human approval."""
        action_id = f"act_{int(time.time() * 1000)}_{len(self._actions)}"
        tool_meta = self.governance.get_tool_metadata(tool_name)
        inferred_risk = risk_level or tool_meta.get("risk", "high")

        action_record = {
            "action_id": action_id,
            "created_at": datetime.now().isoformat(),
            "simulation_id": simulation_id or "global",
            "agent_id": agent_id,
            "agent_role": agent_role,
            "tool_name": tool_name,
            "arguments": arguments,
            "risk_level": inferred_risk,
            "predicted_outcome": predicted_outcome or f"Autonomous execution of {tool_name} with staged arguments.",
            "status": HITLActionStatus.PENDING,
            "reviewed_at": None,
            "reviewed_by": None,
            "execution_result": None,
            "error": None
        }

        self._actions[action_id] = action_record
        logger.info(f"Staged action {action_id} [{tool_name}] from {agent_role} for HITL review")
        return action_record

    def list_actions(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List staged actions ordered by newest first."""
        items = list(self._actions.values())
        if status:
            items = [x for x in items if x["status"] == status]
        items.sort(key=lambda x: x["created_at"], reverse=True)
        return items[:limit]

    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        return self._actions.get(action_id)

    def approve_and_execute(self, action_id: str, operator_id: str = "human_operator") -> Dict[str, Any]:
        """Human approval callback: dispatches tool call directly to viaSocket."""
        action = self._actions.get(action_id)
        if not action:
            raise ValueError(f"Action '{action_id}' not found")

        if action["status"] != HITLActionStatus.PENDING:
            return action

        start_ts = time.perf_counter()
        logger.info(f"Operator '{operator_id}' approved action {action_id} ({action['tool_name']})")

        # Execute via viaSocket client
        exec_res = self.client.call_tool(action["tool_name"], action["arguments"])
        elapsed_ms = round((time.perf_counter() - start_ts) * 1000, 2)

        action["reviewed_at"] = datetime.now().isoformat()
        action["reviewed_by"] = operator_id

        if exec_res.get("success"):
            action["status"] = HITLActionStatus.EXECUTED
            action["execution_result"] = exec_res.get("result")
            reason = f"OPERATOR APPROVED: Executed via viaSocket in {elapsed_ms}ms"
        else:
            action["status"] = HITLActionStatus.FAILED
            action["error"] = exec_res.get("error")
            reason = f"OPERATOR APPROVED BUT FAILED: {exec_res.get('error')}"

        # Audit the manual execution
        self.governance._log_audit(
            decision=GovernanceDecision.ALLOWED if exec_res.get("success") else GovernanceDecision.DENIED,
            agent_id=action["agent_id"],
            agent_role=action["agent_role"],
            tool_name=action["tool_name"],
            arguments=action["arguments"],
            action_type="write",
            risk_level=action["risk_level"],
            phase="operator_approval",
            simulation_id=action.get("simulation_id"),
            latency_ms=elapsed_ms,
            reason=reason
        )

        return action

    def reject_action(self, action_id: str, reason: str = "Rejected by operator", operator_id: str = "human_operator") -> Dict[str, Any]:
        """Operator rejects a proposed action."""
        action = self._actions.get(action_id)
        if not action:
            raise ValueError(f"Action '{action_id}' not found")

        action["status"] = HITLActionStatus.REJECTED
        action["reviewed_at"] = datetime.now().isoformat()
        action["reviewed_by"] = operator_id
        action["error"] = reason

        self.governance._log_audit(
            decision=GovernanceDecision.DENIED,
            agent_id=action["agent_id"],
            agent_role=action["agent_role"],
            tool_name=action["tool_name"],
            arguments=action["arguments"],
            action_type="write",
            risk_level=action["risk_level"],
            phase="operator_approval",
            simulation_id=action.get("simulation_id"),
            latency_ms=0.1,
            reason=f"OPERATOR REJECTED: {reason}"
        )

        return action
