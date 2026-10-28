"""
Initialize TigerGraph Cloud Schema for Lokantra.
"""

import time
import pyTigerGraph as tg

HOST = "https://tg-6e8a4a3d-1333-4e53-877b-144274eab847.tg-3452941248.i.tgcloud.io"
SECRET = "5ev8o4gnngcpd8d3r1j9ka72ebostr75"
GRAPH_NAME = "LokantraGraph"

print(f"Connecting to TigerGraph Cloud at {HOST}...")
conn = tg.TigerGraphConnection(
    host=HOST,
    gsqlSecret=SECRET,
    tgCloud=True,
)

print("Requesting API Token with Secret...")
token = conn.getToken(SECRET)
api_token = token[0] if isinstance(token, tuple) else token
conn.apiToken = api_token
print(f"Authenticated successfully! Token: {api_token[:20]}...")

print("\n--- Running GSQL Schema Definitions ---")
print("1. USE GLOBAL:")
print(conn.gsql("USE GLOBAL"))

print("2. CREATE VERTEX Entity:")
v_cmd = 'CREATE VERTEX Entity (PRIMARY_ID id STRING, graph_id STRING, name STRING, entity_type STRING, labels STRING, summary STRING, attributes STRING, created_at STRING, embedding LIST<DOUBLE>) WITH STATS="OUTDEGREE_BY_EDGETYPE"'
print(conn.gsql(v_cmd))

print("3. CREATE DIRECTED EDGE RELATIONSHIP:")
e_cmd = 'CREATE DIRECTED EDGE RELATIONSHIP (FROM Entity, TO Entity, graph_id STRING, rel_type STRING, fact STRING, attributes STRING, created_at STRING, valid_at STRING, invalid_at STRING, expired_at STRING, episodes STRING)'
print(conn.gsql(e_cmd))

print(f"4. CREATE GRAPH {GRAPH_NAME}:")
g_cmd = f"CREATE GRAPH {GRAPH_NAME} (Entity, RELATIONSHIP)"
print(conn.gsql(g_cmd))

print("\n--- Verifying Catalog ---")
print(conn.gsql("ls"))

print("\n--- Connecting to LokantraGraph ---")
graph_conn = tg.TigerGraphConnection(
    host=HOST,
    graphname=GRAPH_NAME,
    apiToken=api_token,
    tgCloud=True,
)
print("Graph Ping:", graph_conn.ping())
print("Vertex count for Entity:", graph_conn.getVertexCount("Entity"))
print("\n>>> SUCCESS: LokantraGraph is ready on TigerGraph Cloud! <<<")
