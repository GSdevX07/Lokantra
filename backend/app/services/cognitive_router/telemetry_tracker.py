"""
Cognitive Swarm Telemetry Tracker (Phase 1 Baseline & Laya Hybrid Measurement)
Tracks action distribution, token consumption, avoided tokens, latency (p50/p95),
and dollar savings across Swarm Simulation rounds.
"""

import os
import json
import time
import math
from datetime import datetime
from typing import Dict, Any, List, Optional


class TelemetryTracker:
    """
    Precision Telemetry & Benchmark Tracker for Multi-Agent Swarm Simulation.
    Instruments action distributions, token savings, and decision latency.
    """
    
    # Cost assumptions (USD per 1M tokens)
    # Frontier/Standard LLM: ~$0.15 / 1M input, ~$0.60 / 1M output (average ~$0.30/1M blended)
    # Laya System 1: $0.00 (100% Free & Open Source local execution)
    LLM_COST_PER_MILLION_TOKENS = 0.30
    LAYA_COST_PER_MILLION_TOKENS = 0.00
    
    # Average tokens per LLM action decision if handled by traditional LLMAction
    BASELINE_TOKENS_PER_ACTION = 450
    
    def __init__(self, simulation_dir: Optional[str] = None, platform: str = "all"):
        self.simulation_dir = simulation_dir
        self.platform = platform
        self.records: List[Dict[str, Any]] = []
        self.action_counts: Dict[str, int] = {}
        self.method_counts: Dict[str, int] = {"gate": 0, "laya": 0, "llm": 0, "baseline": 0}
        self.latencies_by_method: Dict[str, List[float]] = {
            "gate": [], "laya": [], "llm": [], "baseline": []
        }
        self.total_tokens_consumed = 0
        self.total_tokens_avoided = 0
        self.start_time = time.time()
        
    def record_action(
        self,
        round_num: int,
        agent_id: int,
        agent_name: str,
        action_type: str,
        decision_tier: str,  # 'gate' (Tier 0), 'laya' (Tier 1), 'llm' (Tier 2), or 'baseline'
        latency_ms: float,
        tokens_consumed: int = 0,
        tokens_avoided: int = 0,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ):
        """Record an individual agent action decision with telemetry"""
        # Normalize action name
        action_name = str(action_type).upper()
        if "ACTIONTYPE." in action_name:
            action_name = action_name.split("ACTIONTYPE.")[-1]
            
        self.action_counts[action_name] = self.action_counts.get(action_name, 0) + 1
        tier_key = decision_tier.lower()
        if tier_key == "jev":
            tier_key = "laya"
            
        if tier_key not in self.method_counts:
            self.method_counts[tier_key] = 0
            self.latencies_by_method[tier_key] = []
            
        self.method_counts[tier_key] += 1
        self.latencies_by_method[tier_key].append(max(0.1, latency_ms))
        
        self.total_tokens_consumed += tokens_consumed
        self.total_tokens_avoided += tokens_avoided
        
        record = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "agent_name": agent_name,
            "action_type": action_name,
            "decision_tier": tier_key,
            "latency_ms": round(latency_ms, 2),
            "tokens_consumed": tokens_consumed,
            "tokens_avoided": tokens_avoided,
            "success": success,
            "details": details or {}
        }
        self.records.append(record)
        
        # Periodic auto-save every 10 actions if dir is configured
        if len(self.records) % 10 == 0 and self.simulation_dir:
            self.save_telemetry()
            
    def _percentile(self, data: List[float], p: float) -> float:
        """Calculate percentile from data list"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return round(sorted_data[int(k)], 2)
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return round(d0 + d1, 2)
        
    def get_summary(self) -> Dict[str, Any]:
        """Generate comprehensive metrics summary"""
        total_actions = len(self.records)
        all_latencies = [r["latency_ms"] for r in self.records] if self.records else []
        
        # Action Distribution
        distribution = {}
        for action, count in self.action_counts.items():
            pct = (count / total_actions * 100) if total_actions > 0 else 0
            distribution[action] = {
                "count": count,
                "percentage": round(pct, 1)
            }
            
        # Method / Tier breakdown
        tiers = {}
        for tier, count in self.method_counts.items():
            pct = (count / total_actions * 100) if total_actions > 0 else 0
            lat_list = self.latencies_by_method.get(tier, [])
            avg_lat = (sum(lat_list) / len(lat_list)) if lat_list else 0.0
            tiers[tier] = {
                "count": count,
                "percentage": round(pct, 1),
                "avg_latency_ms": round(avg_lat, 2)
            }
            
        # Overall Latency Stats
        latency_stats = {
            "avg_ms": round(sum(all_latencies) / len(all_latencies), 2) if all_latencies else 0.0,
            "p50_ms": self._percentile(all_latencies, 50),
            "p95_ms": self._percentile(all_latencies, 95),
            "min_ms": round(min(all_latencies), 2) if all_latencies else 0.0,
            "max_ms": round(max(all_latencies), 2) if all_latencies else 0.0
        }
        
        # Token and Cost economics (Laya is $0.00 / free!)
        est_cost_consumed = (self.total_tokens_consumed / 1_000_000) * self.LLM_COST_PER_MILLION_TOKENS
        est_cost_saved = (self.total_tokens_avoided / 1_000_000) * (self.LLM_COST_PER_MILLION_TOKENS - self.LAYA_COST_PER_MILLION_TOKENS)
        
        total_hypothetical_tokens = self.total_tokens_consumed + self.total_tokens_avoided
        savings_pct = (self.total_tokens_avoided / total_hypothetical_tokens * 100) if total_hypothetical_tokens > 0 else 0.0
        
        return {
            "total_actions": total_actions,
            "elapsed_seconds": round(time.time() - self.start_time, 2),
            "action_distribution": distribution,
            "decision_tiers": tiers,
            "latency_metrics": latency_stats,
            "token_economics": {
                "tokens_consumed": self.total_tokens_consumed,
                "tokens_avoided": self.total_tokens_avoided,
                "total_hypothetical_tokens": total_hypothetical_tokens,
                "token_savings_percentage": round(savings_pct, 1),
                "estimated_cost_consumed_usd": round(est_cost_consumed, 6),
                "estimated_cost_saved_usd": round(est_cost_saved, 6)
            }
        }
        
    def save_telemetry(self, filepath: Optional[str] = None):
        """Save telemetry data and summary to JSON file"""
        target_path = filepath
        if not target_path and self.simulation_dir:
            target_path = os.path.join(self.simulation_dir, "telemetry.json")
            
        if not target_path:
            return
            
        data = {
            "updated_at": datetime.now().isoformat(),
            "platform": self.platform,
            "summary": self.get_summary(),
            "recent_actions": self.records[-50:]  # Keep last 50 detailed records
        }
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save telemetry to {target_path}: {e}")

    def generate_ascii_report(self) -> str:
        """Format an informative summary report for terminal display and logs"""
        summary = self.get_summary()
        econ = summary["token_economics"]
        lat = summary["latency_metrics"]
        tiers = summary["decision_tiers"]
        
        lines = [
            "=" * 68,
            "       COGNITIVE SWARM TELEMETRY & SAVINGS REPORT (LAYA + LLM)",
            "=" * 68,
            f" Total Decisions Tracked : {summary['total_actions']} actions",
            f" Decision Latency (p50)  : {lat['p50_ms']} ms | (p95): {lat['p95_ms']} ms | Avg: {lat['avg_ms']} ms",
            "-" * 68,
            " DECISION TIER BREAKDOWN:",
            f"   • Tier 0 (Reflex Gate)   : {tiers.get('gate', {}).get('count', 0)} ({tiers.get('gate', {}).get('percentage', 0)}%) [Avg {tiers.get('gate', {}).get('avg_latency_ms', 0)}ms]",
            f"   • Tier 1 (Laya System 1) : {tiers.get('laya', {}).get('count', 0)} ({tiers.get('laya', {}).get('percentage', 0)}%) [Avg {tiers.get('laya', {}).get('avg_latency_ms', 0)}ms]",
            f"   • Tier 2 (System 2 LLM)  : {tiers.get('llm', {}).get('count', 0)} ({tiers.get('llm', {}).get('percentage', 0)}%) [Avg {tiers.get('llm', {}).get('avg_latency_ms', 0)}ms]",
            "-" * 68,
            " TOKEN & COST ECONOMICS (Laya Open-Source $0.00/token):",
            f"   • Tokens Consumed        : {econ['tokens_consumed']:,} tokens",
            f"   • Tokens Avoided         : {econ['tokens_avoided']:,} tokens",
            f"   • Token Reduction Rate   : {econ['token_savings_percentage']}%",
            f"   • Estimated USD Saved    : ${econ['estimated_cost_saved_usd']:.4f}",
            "=" * 68
        ]
        return "\n".join(lines)
