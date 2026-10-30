"""
Tests for viaSocket MCP Client, Scoping Registry, HITL Queue, and Governance API
"""

import pytest
from app import create_app
from app.services.viasocket import (
    ViaSocketClient,
    ScopingRegistry,
    GovernanceDecision,
    HITLActionQueue,
    HITLActionStatus,
    ViaSocketGraphBridge
)


@pytest.fixture
def test_client():
    client = ViaSocketClient(mode="demo")
    return client


@pytest.fixture
def governance(test_client):
    gov = ScopingRegistry(test_client)
    gov.reset_policies_to_default()
    return gov


@pytest.fixture
def hitl(test_client, governance):
    return HITLActionQueue(test_client, governance)


@pytest.fixture
def api_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_client_catalog_and_fallback(test_client):
    tools = test_client.list_tools()
    assert len(tools) >= 5
    tool_names = [t["name"] for t in tools]
    assert "scrape_webpage" in tool_names
    assert "send_slack_message" in tool_names
    assert "search_serp_google" in tool_names


def test_scoping_registry_default_deny(governance):
    # Public persona is not allowed any tools by default
    decision, payload, reason, latency = governance.evaluate_and_route(
        agent_id="agent_12",
        agent_role="public_persona",
        tool_name="send_slack_message",
        arguments={"channel": "#general", "message": "Disruption!"},
        phase="simulation"
    )
    assert decision == GovernanceDecision.DENIED
    assert "SECURITY VIOLATION" in reason
    assert latency < 20.0  # Fast sub-millisecond in-memory decision


def test_scoping_registry_allowed_read(governance):
    # Market research agent is authorized for scrape_webpage
    decision, payload, reason, latency = governance.evaluate_and_route(
        agent_id="agent_researcher",
        agent_role="market_research_agent",
        tool_name="scrape_webpage",
        arguments={"url": "https://competitor.com"},
        phase="simulation"
    )
    assert decision in (GovernanceDecision.ALLOWED, GovernanceDecision.CACHED)
    assert payload is not None
    assert "extracted_content" in payload


def test_in_memory_cache_sub_millisecond_latency(governance):
    args = {"query": "interest_rates_q4"}
    # Call 1: Allowed and fetched
    dec1, res1, reason1, lat1 = governance.evaluate_and_route(
        agent_id="analyst_1",
        agent_role="financial_agent",
        tool_name="search_serp_google",
        arguments=args,
        phase="simulation",
        round_num=1
    )
    assert dec1 in (GovernanceDecision.ALLOWED, GovernanceDecision.CACHED)

    # Call 2 with identical arguments: Must hit in-memory cache instantly
    dec2, res2, reason2, lat2 = governance.evaluate_and_route(
        agent_id="analyst_2",
        agent_role="financial_agent",
        tool_name="search_serp_google",
        arguments=args,
        phase="simulation",
        round_num=1
    )
    assert dec2 == GovernanceDecision.CACHED
    assert "CACHE HIT" in reason2
    assert lat2 < 5.0  # Zero network roundtrip


def test_rate_limiter_exceeded(governance):
    # Financial agent has max 3 calls per round
    agent_id = "eager_agent_99"
    role = "financial_agent"
    tool = "search_serp_google"

    for i in range(3):
        dec, _, _, _ = governance.evaluate_and_route(
            agent_id=agent_id,
            agent_role=role,
            tool_name=tool,
            arguments={"query": f"rate_{i}"},
            phase="simulation",
            round_num=2
        )
        assert dec in (GovernanceDecision.ALLOWED, GovernanceDecision.CACHED)

    # 4th call should be blocked by Rate Limiter
    dec4, _, reason4, _ = governance.evaluate_and_route(
        agent_id=agent_id,
        agent_role=role,
        tool_name=tool,
        arguments={"query": "rate_excess"},
        phase="simulation",
        round_num=2
    )
    assert dec4 == GovernanceDecision.DENIED
    assert "RATE LIMIT EXCEEDED" in reason4


def test_write_action_staged_for_hitl(governance, hitl):
    # Report agent has permission to request send_slack_message, but write tools are staged for HITL
    decision, staged_payload, reason, _ = governance.evaluate_and_route(
        agent_id="report_agent",
        agent_role="report_agent",
        tool_name="send_slack_message",
        arguments={"channel": "#boardroom", "message": "Simulated forecast complete"},
        phase="post_simulation"
    )
    assert decision == GovernanceDecision.PENDING_APPROVAL
    assert "HUMAN-IN-THE-LOOP REQUIRED" in reason

    # Stage into HITL queue
    action = hitl.stage_action(
        agent_id=staged_payload["agent_id"],
        agent_role=staged_payload["agent_role"],
        tool_name=staged_payload["tool_name"],
        arguments=staged_payload["arguments"]
    )
    assert action["status"] == HITLActionStatus.PENDING
    assert action["action_id"].startswith("act_")


def test_hitl_approval_and_execution(hitl):
    action = hitl.stage_action(
        agent_id="report_agent",
        agent_role="report_agent",
        tool_name="send_slack_message",
        arguments={"channel": "#general", "message": "Approved test message"}
    )
    approved = hitl.approve_and_execute(action["action_id"], operator_id="admin_judge")
    assert approved["status"] == HITLActionStatus.EXECUTED
    assert approved["reviewed_by"] == "admin_judge"
    assert approved["execution_result"] is not None


def test_hitl_rejection(hitl):
    action = hitl.stage_action(
        agent_id="report_agent",
        agent_role="report_agent",
        tool_name="post_twitter_tweet",
        arguments={"status_text": "Unverified claim"}
    )
    rejected = hitl.reject_action(action["action_id"], reason="Too risky before final review")
    assert rejected["status"] == HITLActionStatus.REJECTED
    assert "Too risky" in rejected["error"]


def test_knowledge_graph_ingestion_bridge():
    bridge = ViaSocketGraphBridge()
    obs = bridge.ingest_ground_truth(
        tool_name="scrape_webpage",
        arguments={"url": "https://gov.in/policy"},
        raw_result={"extracted_content": "New green energy tax exemption passed."},
        simulation_id="sim_123"
    )
    assert obs["tool_name"] == "scrape_webpage"
    assert "New green energy tax exemption" in obs["fact_text"]
    assert len(bridge.get_recent_observations()) >= 1


def test_flask_api_status_and_tools(api_client):
    res = api_client.get("/api/viasocket/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "total_tools_available" in data

    res2 = api_client.get("/api/viasocket/tools")
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["count"] >= 5


def test_flask_api_simulate_rogue_attack(api_client):
    res = api_client.post("/api/viasocket/simulate-rogue-attack")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["governance_verdict"]["blocked"] is True
    assert data["governance_verdict"]["decision"] == "DENIED"
    assert "SECURITY VIOLATION" in data["governance_verdict"]["security_rationale"]
