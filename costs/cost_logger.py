"""
Cost Logger

Tracks token usage and costs for LLM API calls.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from .pricing_config import estimate_cost, get_model_pricing


class CostLogger:
    """Logs and tracks API costs."""

    def __init__(self, log_file: str = "cost_logs.jsonl"):
        """
        Initialize cost logger.

        Args:
            log_file: Path to log file (JSONL format)
        """
        self.log_file = log_file
        self.session_logs = []
        self.session_start = datetime.now()

    def log_request(self, model: str, input_tokens: int, output_tokens: int,
                   test_name: str = None, metadata: dict = None):
        """
        Log a single API request.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            test_name: Optional test name
            metadata: Optional additional metadata
        """
        cost_data = estimate_cost(input_tokens, output_tokens, model)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_start": self.session_start.isoformat(),
            "model": model,
            "test_name": test_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_eur": cost_data["total_cost_eur"],
            "cost_breakdown": {
                "input_eur": cost_data["input_cost_eur"],
                "output_eur": cost_data["output_cost_eur"]
            },
            "metadata": metadata or {}
        }

        self.session_logs.append(log_entry)

        # Append to file
        self._write_to_file(log_entry)

    def _write_to_file(self, log_entry: Dict):
        """Write log entry to file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to cost log: {e}")

    def get_session_summary(self) -> Dict:
        """
        Get summary of current session.

        Returns:
            Summary dict with totals
        """
        if not self.session_logs:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_eur": 0.0,
                "duration_seconds": 0
            }

        total_tokens = sum(log["total_tokens"] for log in self.session_logs)
        total_cost = sum(log["cost_eur"] for log in self.session_logs)
        duration = (datetime.now() - self.session_start).total_seconds()

        # Group by model
        by_model = {}
        for log in self.session_logs:
            model = log["model"]
            if model not in by_model:
                by_model[model] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost_eur": 0.0
                }
            by_model[model]["requests"] += 1
            by_model[model]["tokens"] += log["total_tokens"]
            by_model[model]["cost_eur"] += log["cost_eur"]

        return {
            "total_requests": len(self.session_logs),
            "total_tokens": total_tokens,
            "total_cost_eur": round(total_cost, 4),
            "duration_seconds": round(duration, 1),
            "by_model": by_model,
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat()
        }

    def print_summary(self):
        """Print session summary to console."""
        summary = self.get_session_summary()

        print("\n" + "="*70)
        print("COST SUMMARY")
        print("="*70)

        if summary["total_requests"] == 0:
            print("No requests logged in this session.")
            return

        print(f"\nSession Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        print(f"Total Cost: €{summary['total_cost_eur']:.4f}")

        if summary.get("by_model"):
            print("\nBreakdown by Model:")
            print("-"*70)
            for model, stats in summary["by_model"].items():
                print(f"  {model}")
                print(f"    Requests: {stats['requests']}")
                print(f"    Tokens:   {stats['tokens']:,}")
                print(f"    Cost:     €{stats['cost_eur']:.4f}")

        print("="*70 + "\n")

    def load_historical_logs(self, limit: int = 100) -> List[Dict]:
        """
        Load historical logs from file.

        Args:
            limit: Maximum number of recent logs to load

        Returns:
            List of log entries
        """
        if not os.path.exists(self.log_file):
            return []

        logs = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

            # Return most recent entries
            return logs[-limit:] if len(logs) > limit else logs

        except Exception as e:
            print(f"Warning: Could not read cost logs: {e}")
            return []

    def get_total_historical_cost(self, days: int = 30) -> Dict:
        """
        Get total cost from historical logs.

        Args:
            days: Number of days to look back

        Returns:
            Summary dict
        """
        logs = self.load_historical_logs(limit=10000)

        if not logs:
            return {
                "period_days": days,
                "total_cost_eur": 0.0,
                "total_tokens": 0,
                "total_requests": 0
            }

        # Filter by date
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_logs = [
            log for log in logs
            if datetime.fromisoformat(log["timestamp"]).timestamp() > cutoff
        ]

        total_cost = sum(log.get("cost_eur", 0) for log in recent_logs)
        total_tokens = sum(log.get("total_tokens", 0) for log in recent_logs)

        return {
            "period_days": days,
            "total_cost_eur": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_requests": len(recent_logs),
            "logs_analyzed": len(logs)
        }


# Global logger instance
_logger = None


def get_cost_logger() -> CostLogger:
    """Get global cost logger instance."""
    global _logger
    if _logger is None:
        _logger = CostLogger()
    return _logger
