import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(backend_dir, 'app', 'services'))

from cognitive_router import (
    CognitiveSwarmRouter,
    TelemetryTracker,
    HeuristicReflexGate,
    AkidaSNNGate,
    LayaDecisionEngine,
    create_reflex_gate
)

def test_cognitive_swarm_stack():
    # 1. Telemetry verification
    tracker = TelemetryTracker()
    tracker.record_action(1, 0, 'Alice', 'LIKE_POST', 'laya', latency_ms=45.0, tokens_consumed=0, tokens_avoided=450)
    tracker.record_action(1, 1, 'Bob', 'DO_NOTHING', 'gate', latency_ms=0.4, tokens_consumed=0, tokens_avoided=450)
    tracker.record_action(1, 2, 'Charlie', 'CREATE_POST', 'llm', latency_ms=1800.0, tokens_consumed=450, tokens_avoided=0)

    summary = tracker.get_summary()
    assert summary['total_actions'] == 3
    assert summary['token_economics']['token_savings_percentage'] > 50
    assert summary['decision_tiers']['laya']['count'] == 1
    assert summary['decision_tiers']['gate']['count'] == 1
    assert summary['decision_tiers']['llm']['count'] == 1

    # 2. Reflex Gate verification
    gate = HeuristicReflexGate(threshold=0.3)
    spiked, arousal, reason = gate.evaluate(
        {'name': 'Tech Enthusiast', 'bio': 'Lover of AI and quantum computing'},
        {'content': 'New breakthrough in artificial intelligence models today!', 'likes_count': 10}
    )
    assert isinstance(spiked, bool)
    assert 0.0 <= arousal <= 1.0

    # 3. Akida SNN Gate verification
    snn_gate = AkidaSNNGate(threshold=0.4)
    snn_spiked, snn_v, _ = snn_gate.evaluate(
        {'id': 42, 'bio': 'Bio enthusiast'},
        {'content': 'CRISPR breakthrough in cellular genetics', 'likes_count': 25}
    )
    assert isinstance(snn_spiked, bool)

    # 4. Laya System 1 Decision Engine verification
    laya = LayaDecisionEngine()
    chosen, probs, lat = laya.evaluate_action(
        {'name': 'Alice', 'bio': 'AI developer', 'interests': ['ai', 'tech']},
        {'content': 'Check out this new AI open-source release', 'likes_count': 15},
        ['DO_NOTHING', 'LIKE_POST', 'REPOST', 'CREATE_POST']
    )
    assert chosen in ['DO_NOTHING', 'LIKE_POST', 'REPOST', 'CREATE_POST']
    assert len(probs) == 4
    assert sum(probs.values()) > 0.99

    # 5. Full CognitiveSwarmRouter decision loop
    router = CognitiveSwarmRouter(mode='hybrid', gate_backend='heuristic')
    action_type, tier, details = router.decide_single_agent_action(
        agent_profile={'name': 'Alice', 'bio': 'AI researcher', 'activity_level': 0.8},
        candidate_post={'id': 101, 'content': 'Exciting news in neural architecture search!', 'likes_count': 12},
        available_actions=['DO_NOTHING', 'LIKE_POST', 'REPOST', 'CREATE_POST']
    )
    assert action_type in ['DO_NOTHING', 'LIKE_POST', 'REPOST', 'CREATE_POST']
    assert tier in ['gate', 'laya', 'llm']

if __name__ == '__main__':
    test_cognitive_swarm_stack()
    print('All cognitive router unit tests passed with Laya System 1!')
