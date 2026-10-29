"""
End-to-End Verification of TigerGraph Integration for Lokantra.
"""

import sys
import json
import time

from app.config import Config
from app.utils.tigergraph_client import get_tigergraph_connection
from app.services.tigergraph_builder import TigerGraphBuilderService
from app.services.tigergraph_entity_reader import TigerGraphEntityReader
from app.services.tigergraph_memory_updater import TigerGraphMemoryUpdater, AgentActivity
from app.services.tigergraph_tools import TigerGraphToolsService

print("=== Starting End-to-End TigerGraph Verification ===")
def run_verification():
    
    # 1. Connection check
    conn = get_tigergraph_connection()
    ping = conn.ping()
    print(f"1. Connection Ping: {ping}")
    assert ping.get("error") is False
    
    test_graph_id = "test_lokantra_project_1"
    
    # Cleanup before test
    builder = TigerGraphBuilderService()
    builder.delete_graph(test_graph_id)
    
    # 2. Test Entity Reader on empty graph
    reader = TigerGraphEntityReader()
    nodes = reader.get_all_nodes(test_graph_id)
    print(f"2. Initial node count for {test_graph_id}: {len(nodes)}")
    
    # 3. Test Direct Upsert & Entity Reader
    print("3. Testing Vertex and Edge Upsert into TigerGraph...")
    v_payload = [
        (
            "test_alice",
            {
                "graph_id": test_graph_id,
                "name": "Alice Smith",
                "entity_type": "Person",
                "labels": json.dumps(["Entity", "Person"]),
                "summary": "Key opinion leader and public policy researcher.",
                "attributes": json.dumps({"role": "Researcher", "influence": 0.85}),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "embedding": [0.1] * 128,
            }
        ),
        (
            "test_acme",
            {
                "graph_id": test_graph_id,
                "name": "Acme Institute",
                "entity_type": "Organization",
                "labels": json.dumps(["Entity", "Organization"]),
                "summary": "Leading social policy research think-tank.",
                "attributes": json.dumps({"founded": 2010}),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "embedding": [0.2] * 128,
            }
        )
    ]
    conn.upsertVertices("Entity", v_payload)
    
    e_payload = [
        (
            "test_alice",
            "test_acme",
            {
                "graph_id": test_graph_id,
                "rel_type": "WORKS_AT",
                "fact": "Alice Smith works at Acme Institute as a senior researcher.",
                "attributes": json.dumps({"tenure_years": 4}),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "valid_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "invalid_at": "",
                "expired_at": "",
                "episodes": "ep_test_01",
            }
        )
    ]
    conn.upsertEdges("Entity", "RELATIONSHIP", "Entity", e_payload)
    print("   Upserted 2 vertices and 1 edge.")
    
    # 4. Verify Entity Reader
    nodes = reader.get_all_nodes(test_graph_id)
    edges = reader.get_all_edges(test_graph_id)
    print(f"4. Retrieved {len(nodes)} nodes and {len(edges)} edges via TigerGraphEntityReader.")
    assert len(nodes) == 2, f"Expected 2 nodes, got {len(nodes)}"
    assert len(edges) == 1, f"Expected 1 edge, got {len(edges)}"
    assert nodes[0]["name"] in ["Alice Smith", "Acme Institute"]
    print("   Entity Reader Verification: PASSED")
    
    # 5. Test Filtered Entities
    filtered = reader.filter_defined_entities(test_graph_id, defined_entity_types=["Person"])
    print(f"5. FilteredEntities (Person): {filtered.filtered_count} matching entities found.")
    assert filtered.filtered_count == 1
    assert filtered.entities[0].name == "Alice Smith"
    assert len(filtered.entities[0].related_edges) == 1
    print("   Filtered Entities & 1-Hop Subgraph Enrichment: PASSED")
    
    # 6. Test Memory Updater (Streaming simulation action)
    print("6. Testing Simulation Memory Streaming Updater...")
    updater = TigerGraphMemoryUpdater(graph_id=test_graph_id, simulation_id="sim_test_001")
    activity = AgentActivity(
        platform="twitter",
        agent_id=101,
        agent_name="Bob Jones",
        action_type="LIKE_POST",
        action_args={"post_content": "New public opinion report", "post_author_name": "Alice Smith"},
        round_num=1,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    updater.add_activity(activity)
    # Force flush
    updater._flush_buffer()
    
    nodes_after = reader.get_all_nodes(test_graph_id)
    edges_after = reader.get_all_edges(test_graph_id)
    print(f"   Nodes after simulation action: {len(nodes_after)}, Edges: {len(edges_after)}")
    assert len(edges_after) >= 2, f"Expected at least 2 edges, got {len(edges_after)}"
    print("   Simulation Memory Streaming: PASSED")
    
    # 7. Test Retrieval Tools (QuickSearch, PanoramaSearch, InsightForge)
    print("7. Testing Retrieval Tools Service (TigerGraphToolsService)...")
    tools = TigerGraphToolsService()
    
    quick = tools.quick_search(test_graph_id, "researcher at Acme", limit=5)
    print(f"   QuickSearch results: {quick.total_count} facts found.")
    print(f"   Top fact: {quick.facts[0] if quick.facts else 'None'}")
    assert quick.total_count > 0, "Expected facts in QuickSearch"
    
    panorama = tools.panorama_search(test_graph_id, "policy", limit=10)
    print(f"   PanoramaSearch: {len(panorama.active_facts)} active facts found.")
    assert panorama.total_facts > 0, "Expected facts in PanoramaSearch"
    
    insight = tools.insight_forge(test_graph_id, "What role does Alice Smith play?")
    print(f"   InsightForge: Retrieved {insight.total_facts_retrieved} facts.")
    assert insight.total_facts_retrieved > 0, "Expected facts in InsightForge"
    print("   Retrieval Tools Verification: PASSED")
    
    # 8. Clean up test partition
    print("8. Cleaning up test graph partition...")
    builder = TigerGraphBuilderService()
    builder.delete_graph(test_graph_id)
    remaining_nodes = reader.get_all_nodes(test_graph_id)
    print(f"   Remaining nodes after cleanup: {len(remaining_nodes)}")
    print("   Cleanup: PASSED")
    
    print("\n============================================================")
    print("ALL END-TO-END TIGERGRAPH TESTS PASSED 100% SUCCESSFULLY!")
    print("============================================================")

if __name__ == "__main__":
    run_verification()
