"""
TigerGraph Client Connection and Schema Manager for Lokantra.
Manages connections via pyTigerGraph, schema initialization, and health checks.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional
import pyTigerGraph as tg

from ..config import Config
from .logger import get_logger

logger = get_logger("lokantra.tigergraph")

# Global cached connection
_tg_conn: Optional[tg.TigerGraphConnection] = None


def get_tigergraph_connection(
    graph_name: Optional[str] = None,
    force_new: bool = False
) -> tg.TigerGraphConnection:
    """
    Get or create a cached pyTigerGraph connection.
    """
    global _tg_conn
    target_graph = graph_name or Config.TIGERGRAPH_GRAPH_NAME

    if _tg_conn is not None and not force_new:
        if _tg_conn.graphname == target_graph:
            return _tg_conn

    host = Config.TIGERGRAPH_HOST
    restpp_port = Config.TIGERGRAPH_REST_PORT
    gs_port = Config.TIGERGRAPH_GS_PORT
    username = Config.TIGERGRAPH_USERNAME
    password = Config.TIGERGRAPH_PASSWORD
    is_cloud = "tgcloud.io" in host.lower() or host.lower().startswith("https://")

    logger.info(f"Connecting to TigerGraph at {host} (is_cloud={is_cloud}, graph={target_graph})...")

    if is_cloud:
        conn = tg.TigerGraphConnection(
            host=host,
            graphname=target_graph,
            gsqlSecret=Config.TIGERGRAPH_SECRET or "",
            tgCloud=True,
        )
    else:
        conn = tg.TigerGraphConnection(
            host=host,
            restppPort=restpp_port,
            gsPort=gs_port,
            username=username,
            password=password,
            graphname=target_graph,
        )

    # If secret or token exists, configure it
    if Config.TIGERGRAPH_API_TOKEN:
        conn.apiToken = Config.TIGERGRAPH_API_TOKEN
    elif Config.TIGERGRAPH_SECRET:
        try:
            token_res = conn.getToken(Config.TIGERGRAPH_SECRET)
            conn.apiToken = token_res[0] if isinstance(token_res, tuple) else token_res
            logger.info("TigerGraph API token successfully generated and cached.")
        except Exception as e:
            logger.warning(f"Failed to generate TigerGraph token from secret: {e}")

    _tg_conn = conn
    return conn


def init_lokantra_schema(conn: Optional[tg.TigerGraphConnection] = None) -> bool:
    """
    Ensure the LokantraGraph schema exists in TigerGraph.
    Installs:
    - Entity vertex type
    - RELATIONSHIP directed edge type
    - LokantraGraph graph definition
    """
    target_graph = Config.TIGERGRAPH_GRAPH_NAME
    host = Config.TIGERGRAPH_HOST
    is_cloud = "tgcloud.io" in host.lower() or host.lower().startswith("https://")
    
    # Connect without specific graph first to inspect schema
    if is_cloud:
        base_conn = tg.TigerGraphConnection(
            host=host,
            gsqlSecret=Config.TIGERGRAPH_SECRET or "",
            tgCloud=True,
        )
        if Config.TIGERGRAPH_SECRET:
            try:
                token_res = base_conn.getToken(Config.TIGERGRAPH_SECRET)
                base_conn.apiToken = token_res[0] if isinstance(token_res, tuple) else token_res
            except Exception:
                pass
    else:
        base_conn = tg.TigerGraphConnection(
            host=host,
            restppPort=Config.TIGERGRAPH_REST_PORT,
            gsPort=Config.TIGERGRAPH_GS_PORT,
            username=Config.TIGERGRAPH_USERNAME,
            password=Config.TIGERGRAPH_PASSWORD,
        )

    try:
        graphs_resp = base_conn.gsql("ls")
        if target_graph.lower() in graphs_resp.lower():
            logger.info(f"TigerGraph graph '{target_graph}' already exists.")
            return True

        logger.info(f"Creating TigerGraph schema and graph '{target_graph}'...")

        schema_commands = f"""
        USE GLOBAL
        CREATE VERTEX Entity(
            PRIMARY_ID id STRING,
            graph_id STRING,
            name STRING,
            entity_type STRING,
            labels STRING,
            summary STRING,
            attributes STRING,
            created_at STRING,
            embedding LIST<DOUBLE>
        ) WITH STATS="OUTDEGREE_BY_EDGETYPE";

        CREATE DIRECTED EDGE RELATIONSHIP(
            FROM Entity,
            TO Entity,
            graph_id STRING,
            rel_type STRING,
            fact STRING,
            attributes STRING,
            created_at STRING,
            valid_at STRING,
            invalid_at STRING,
            expired_at STRING,
            episodes STRING
        );

        CREATE GRAPH {target_graph}(Entity, RELATIONSHIP);
        """

        res = base_conn.gsql(schema_commands)
        logger.info(f"TigerGraph schema creation result: {res}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize TigerGraph schema: {e}")
        return False


def ping_tigergraph() -> bool:
    """Check whether TigerGraph server is alive and reachable."""
    try:
        conn = get_tigergraph_connection()
        res = conn.ping()
        return bool(res and "pong" in str(res).lower())
    except Exception:
        return False
