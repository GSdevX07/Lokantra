"""
viaSocket Governance & Action Execution API Blueprint
Exposes endpoints for Scoping Registry management, Tool Catalog discovery,
Human-in-the-Loop Action approvals, Real-Time Security Audit logs, and Rogue Agent Simulation.
"""

from __future__ import annotations

import time
from flask import Blueprint, request, jsonify

from ..services.viasocket import (
    get_viasocket_client,
    get_viasocket_governance,
    get_viasocket_hitl,
    get_viasocket_graph_bridge,
    GovernanceDecision,
    HITLActionStatus
)
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('lokantra.api.viasocket')

viasocket_bp = Blueprint('viasocket', __name__)


@viasocket_bp.route('/status', methods=['GET'])
def get_status():
    """Returns viaSocket connection status, active mode, and governance metrics."""
    client = get_viasocket_client()
    governance = get_viasocket_governance()
    hitl = get_viasocket_hitl()

    tools = client.list_tools()
    pending = hitl.list_actions(status=HITLActionStatus.PENDING)
    matrix = governance.get_scoping_matrix()

    return jsonify({
        "success": True,
        "configured": client.is_live_configured(),
        "endpoint": client.endpoint if client.is_live_configured() else "Local viaSocket Sandbox",
        "mode": client.mode,
        "total_tools_available": len(tools),
        "active_roles_configured": len(matrix),
        "embed_configured": client.is_embed_configured(),
        "org_id": Config.VIASOCKET_ORG_ID or None,
        "project_id": Config.VIASOCKET_PROJECT_ID or None,
        "pending_hitl_actions": len(pending),
        "cache_ttl_seconds": governance._cache_ttl,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })


@viasocket_bp.route('/tools', methods=['GET'])
def list_tools():
    """Retrieve all available viaSocket tools with classification and schema."""
    client = get_viasocket_client()
    tools = client.list_tools()
    return jsonify({
        "success": True,
        "count": len(tools),
        "tools": tools
    })


@viasocket_bp.route('/policies', methods=['GET'])
def get_policies():
    """Retrieve the active Scoping Registry matrix (Role-to-Tool permissions)."""
    governance = get_viasocket_governance()
    return jsonify({
        "success": True,
        "matrix": governance.get_scoping_matrix()
    })


@viasocket_bp.route('/policies', methods=['POST'])
def update_policy():
    """Update an agent role's allowed tools and limits."""
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    allowed_tools = data.get("allowed_tools", [])
    max_calls = int(data.get("max_calls_per_round", 3))
    can_request_write = bool(data.get("can_request_write", False))

    if not role:
        return jsonify({"success": False, "error": "Role parameter is required"}), 400

    governance = get_viasocket_governance()
    governance.update_role_policy(
        role=role,
        allowed_tools=allowed_tools,
        max_calls_per_round=max_calls,
        can_request_write=can_request_write
    )

    return jsonify({
        "success": True,
        "message": f"Policy updated for role '{role}'",
        "matrix": governance.get_scoping_matrix()
    })


@viasocket_bp.route('/policies/reset', methods=['POST'])
def reset_policies():
    """Reset the Scoping Registry to default-deny baselines."""
    governance = get_viasocket_governance()
    governance.reset_policies_to_default()
    return jsonify({
        "success": True,
        "message": "Scoping Registry reset to enterprise default-deny baselines",
        "matrix": governance.get_scoping_matrix()
    })


@viasocket_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """Retrieve the recent security audit trail."""
    limit = int(request.args.get("limit", 50))
    governance = get_viasocket_governance()
    logs = governance.get_audit_trail(limit=limit)
    return jsonify({
        "success": True,
        "count": len(logs),
        "logs": logs
    })


@viasocket_bp.route('/pending-actions', methods=['GET'])
def get_pending_actions():
    """List actions waiting for Human-in-the-Loop review."""
    status = request.args.get("status")
    hitl = get_viasocket_hitl()
    actions = hitl.list_actions(status=status)
    return jsonify({
        "success": True,
        "count": len(actions),
        "actions": actions
    })


@viasocket_bp.route('/approve-action', methods=['POST'])
def approve_action():
    """Operator approval: execute the staged write action via viaSocket."""
    data = request.get_json(silent=True) or {}
    action_id = data.get("action_id")
    operator_id = data.get("operator_id", "human_operator")

    if not action_id:
        return jsonify({"success": False, "error": "action_id is required"}), 400

    hitl = get_viasocket_hitl()
    try:
        updated = hitl.approve_and_execute(action_id=action_id, operator_id=operator_id)
        return jsonify({
            "success": True,
            "action": updated
        })
    except Exception as e:
        logger.error(f"Error approving action {action_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@viasocket_bp.route('/reject-action', methods=['POST'])
def reject_action():
    """Operator rejection: discard proposed write action."""
    data = request.get_json(silent=True) or {}
    action_id = data.get("action_id")
    reason = data.get("reason", "Rejected by operator")
    operator_id = data.get("operator_id", "human_operator")

    if not action_id:
        return jsonify({"success": False, "error": "action_id is required"}), 400

    hitl = get_viasocket_hitl()
    try:
        updated = hitl.reject_action(action_id=action_id, reason=reason, operator_id=operator_id)
        return jsonify({
            "success": True,
            "action": updated
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@viasocket_bp.route('/execute-tool', methods=['POST'])
def execute_tool():
    """
    Test execution endpoint through full Governance Layer.
    Intercepts, validates against Scoping Registry, checks cache, and executes if allowed.
    """
    data = request.get_json(silent=True) or {}
    agent_id = str(data.get("agent_id", "test_agent_1"))
    agent_role = str(data.get("agent_role", "market_research_agent"))
    tool_name = str(data.get("tool_name", "scrape_webpage"))
    arguments = data.get("arguments", {})
    phase = str(data.get("phase", "simulation"))
    round_num = int(data.get("round_num", 1))
    simulation_id = data.get("simulation_id", "test_sim")

    governance = get_viasocket_governance()
    hitl = get_viasocket_hitl()
    graph_bridge = get_viasocket_graph_bridge()

    decision, payload, reason, latency_ms = governance.evaluate_and_route(
        agent_id=agent_id,
        agent_role=agent_role,
        tool_name=tool_name,
        arguments=arguments,
        phase=phase,
        round_num=round_num,
        simulation_id=simulation_id
    )

    if decision == GovernanceDecision.PENDING_APPROVAL:
        # Register in HITL queue
        staged = hitl.stage_action(
            agent_id=agent_id,
            agent_role=agent_role,
            tool_name=tool_name,
            arguments=arguments,
            predicted_outcome=f"Agent '{agent_id}' requested {tool_name} during {phase}",
            simulation_id=simulation_id
        )
        return jsonify({
            "success": True,
            "decision": decision,
            "reason": reason,
            "latency_ms": latency_ms,
            "staged_action": staged
        })

    elif decision in (GovernanceDecision.ALLOWED, GovernanceDecision.CACHED):
        # Automatically bridge real-world ground truth into local graph memory
        observation = graph_bridge.ingest_ground_truth(
            tool_name=tool_name,
            arguments=arguments,
            raw_result=payload,
            simulation_id=simulation_id
        )
        return jsonify({
            "success": True,
            "decision": decision,
            "result": payload,
            "graph_observation": observation,
            "reason": reason,
            "latency_ms": latency_ms
        })

    else:
        # DENIED / BLOCKED
        return jsonify({
            "success": False,
            "decision": decision,
            "reason": reason,
            "latency_ms": latency_ms
        }), 403


@viasocket_bp.route('/simulate-rogue-attack', methods=['POST'])
def simulate_rogue_attack():
    """
    Hackathon Demo Trigger:
    Simulates a rogue public persona agent attempting unauthorized destructive actions.
    Demonstrates default-deny blocking live in <1 millisecond.
    """
    governance = get_viasocket_governance()
    
    # Rogue agent attempt
    agent_id = "rogue_persona_99"
    agent_role = "public_persona"
    tool_name = "send_slack_message"
    arguments = {
        "channel": "#production-alerts",
        "message": "UNAUTHORIZED TAKEOVER: Rogue swarm agent broadcasting external disruption!"
    }

    decision, payload, reason, latency_ms = governance.evaluate_and_route(
        agent_id=agent_id,
        agent_role=agent_role,
        tool_name=tool_name,
        arguments=arguments,
        phase="simulation",
        round_num=1,
        simulation_id="demo_rogue_sim"
    )

    latest_audit = governance.get_audit_trail(limit=1)[0] if governance.get_audit_trail(limit=1) else None

    return jsonify({
        "success": True,
        "demonstration": "Rogue Agent Interception & Default-Deny Security Barrier",
        "attempted_by": {
            "agent_id": agent_id,
            "role": agent_role,
            "unauthorized_tool": tool_name,
            "arguments": arguments
        },
        "governance_verdict": {
            "decision": decision,
            "blocked": decision == GovernanceDecision.DENIED,
            "latency_ms": latency_ms,
            "security_rationale": reason
        },
        "audit_event": latest_audit
    })

@viasocket_bp.route('/embed-token', methods=['GET'])
def get_embed_token():
    """Generates a signed JWT token for viaSocket Embed and returns config."""
    client = get_viasocket_client()
    user_id = request.args.get("user_id", "lokantra_admin")
    token = client.generate_embed_token(user_id=user_id)
    webhook_url = client.get_embed_webhook_url(user_id=user_id)

    return jsonify({
        "success": True,
        "configured": client.is_embed_configured(),
        "org_id": Config.VIASOCKET_ORG_ID,
        "project_id": Config.VIASOCKET_PROJECT_ID,
        "embed_token": token,
        "webhook_url": webhook_url
    })

