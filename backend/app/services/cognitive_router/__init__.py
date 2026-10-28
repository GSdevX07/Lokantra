"""
Cognitive Swarm Router Module
Exporting the CognitiveSwarmRouter, TelemetryTracker, LayaDecisionEngine, and Reflex Gates.
"""

from .telemetry_tracker import TelemetryTracker
from .reflex_gate import (
    BaseReflexGate,
    HeuristicReflexGate,
    AkidaSNNGate,
    create_reflex_gate
)
from .laya_client import LayaDecisionEngine
from .swarm_router import CognitiveSwarmRouter

# Backwards compatibility alias
JevDecisionEngine = LayaDecisionEngine

__all__ = [
    "CognitiveSwarmRouter",
    "TelemetryTracker",
    "LayaDecisionEngine",
    "JevDecisionEngine",
    "BaseReflexGate",
    "HeuristicReflexGate",
    "AkidaSNNGate",
    "create_reflex_gate",
]
