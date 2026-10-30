"""
viaSocket Action Execution & Governance Service Module
Unified exports for client, scoping registry, HITL queue, and graph bridge.
"""

from .client import ViaSocketClient
from .governance import ScopingRegistry, GovernanceDecision
from .hitl import HITLActionQueue, HITLActionStatus
from .graph_bridge import ViaSocketGraphBridge

# Global service instances
_client = ViaSocketClient()
_governance = ScopingRegistry(_client)
_hitl = HITLActionQueue(_client, _governance)
_graph_bridge = ViaSocketGraphBridge()


def get_viasocket_client() -> ViaSocketClient:
    return _client


def get_viasocket_governance() -> ScopingRegistry:
    return _governance


def get_viasocket_hitl() -> HITLActionQueue:
    return _hitl


def get_viasocket_graph_bridge() -> ViaSocketGraphBridge:
    return _graph_bridge


__all__ = [
    "ViaSocketClient",
    "ScopingRegistry",
    "GovernanceDecision",
    "HITLActionQueue",
    "HITLActionStatus",
    "ViaSocketGraphBridge",
    "get_viasocket_client",
    "get_viasocket_governance",
    "get_viasocket_hitl",
    "get_viasocket_graph_bridge",
]
