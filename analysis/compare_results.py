"""
Compare Injection Test Results

Compares multiple test run reports to identify:
- Which model is most secure
- Which attack types are most effective
- Trends over time
"""

import json
import sys
from typing import List, Dict


def load_report(filename: str) -> Dict:
    """Load a test report JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get('report', data)  # Handle both formats
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{filename}' is not valid JSON")
        sys.exit(1)


def compare_reports(reports: List[Dict], labels: List[str]):
    """Compare multiple test reports."""

    print("\n" + "="*80)
    print("INJECTION TEST COMPARISON")
    print("="*80)

    # Summary comparison
    print("\n" + "-"*80)
    print("SUMMARY COMPARISON")
    print("-"*80)
    print(f"{'Report':<30} {'Total Tests':<15} {'Leaks':<10} {'Success Rate':<15}")
    print("-"*80)

    for label, report in zip(labels, reports):
        summary = report.get('summary', {})
        total = summary.get('total_tests', 0)
        leaks = summary.get('successful_leaks', 0)
        rate = summary.get('overall_success_rate', 0)
        print(f"{label:<30} {total:<15} {leaks:<10} {rate:>6.1f}%")

    # Find best and worst models
    print("\n" + "-"*80)
    print("MODEL SECURITY RANKING (lower success rate = more secure)")
    print("-"*80)

    ranked = sorted(
        zip(labels, reports),
        key=lambda x: x[1].get('summary', {}).get('overall_success_rate', 0)
    )

    for rank, (label, report) in enumerate(ranked, 1):
        rate = report.get('summary', {}).get('overall_success_rate', 0)
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{emoji} {rank}. {label:<30} {rate:>6.1f}% leak rate")

    # Attack type effectiveness across models
    print("\n" + "-"*80)
    print("ATTACK TYPE EFFECTIVENESS ACROSS MODELS")
    print("-"*80)

    # Collect all attack types
    all_attack_types = set()
    for report in reports:
        all_attack_types.update(report.get('by_attack_type', {}).keys())

    print(f"{'Attack Type':<25}", end="")
    for label in labels:
        print(f"{label[:20]:>22}", end="")
    print()
    print("-"*80)

    for attack_type in sorted(all_attack_types):
        print(f"{attack_type:<25}", end="")
        for report in reports:
            stats = report.get('by_attack_type', {}).get(attack_type, {})
            rate = stats.get('success_rate', 0)
            print(f"{rate:>20.1f}%", end="  ")
        print()

    # Most dangerous attack types (averaged)
    print("\n" + "-"*80)
    print("MOST EFFECTIVE ATTACK TYPES (averaged across all models)")
    print("-"*80)

    attack_averages = {}
    for attack_type in all_attack_types:
        rates = []
        for report in reports:
            stats = report.get('by_attack_type', {}).get(attack_type, {})
            rate = stats.get('success_rate', 0)
            rates.append(rate)
        attack_averages[attack_type] = sum(rates) / len(rates) if rates else 0

    sorted_attacks = sorted(attack_averages.items(), key=lambda x: x[1], reverse=True)

    for rank, (attack_type, avg_rate) in enumerate(sorted_attacks[:10], 1):
        danger = "🔴" if avg_rate > 50 else "🟡" if avg_rate > 10 else "🟢"
        print(f"{danger} {rank:2}. {attack_type:<30} {avg_rate:>6.1f}% avg success")

    # Compromised recipes comparison
    print("\n" + "-"*80)
    print("RECIPE VULNERABILITY COMPARISON")
    print("-"*80)

    all_recipes = set()
    for report in reports:
        all_recipes.update(report.get('leaked_recipes', {}).keys())

    if all_recipes:
        print(f"{'Recipe':<30}", end="")
        for label in labels:
            print(f"{label[:15]:>17}", end="")
        print()
        print("-"*80)

        for recipe in sorted(all_recipes):
            print(f"{recipe:<30}", end="")
            for report in reports:
                leaked = recipe in report.get('leaked_recipes', {})
                count = len(report.get('leaked_recipes', {}).get(recipe, []))
                if leaked:
                    print(f"{'🚨 ' + str(count) + ' leaks':>17}", end="")
                else:
                    print(f"{'✓ secure':>17}", end="")
            print()
    else:
        print("✅ No recipes compromised in any test!")

    # Recommendations
    print("\n" + "-"*80)
    print("RECOMMENDATIONS")
    print("-"*80)

    best_model = ranked[0][0]
    worst_model = ranked[-1][0]

    print(f"✅ Most Secure Model: {best_model}")
    print(f"⚠️  Least Secure Model: {worst_model}")

    # Find attack types that work on all models
    universal_attacks = []
    for attack_type in all_attack_types:
        rates = [report.get('by_attack_type', {}).get(attack_type, {}).get('success_rate', 0)
                for report in reports]
        if all(rate > 0 for rate in rates):
            universal_attacks.append((attack_type, sum(rates) / len(rates)))

    if universal_attacks:
        print(f"\n🔴 Universal Vulnerabilities (work on all models):")
        for attack_type, avg_rate in sorted(universal_attacks, key=lambda x: x[1], reverse=True):
            print(f"   - {attack_type} ({avg_rate:.1f}% avg)")

    # Find model-specific vulnerabilities
    print(f"\n💡 Model-Specific Vulnerabilities:")
    for label, report in zip(labels, reports):
        model_vulns = []
        for attack_type, stats in report.get('by_attack_type', {}).items():
            if stats.get('success_rate', 0) > 20:  # Threshold
                # Check if this is unique to this model
                other_rates = [
                    r.get('by_attack_type', {}).get(attack_type, {}).get('success_rate', 0)
                    for l, r in zip(labels, reports) if l != label
                ]
                if not other_rates or max(other_rates) < 10:
                    model_vulns.append(attack_type)

        if model_vulns:
            print(f"   {label}: {', '.join(model_vulns)}")

    print("\n" + "="*80)


def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_results.py <report1.json> <report2.json> [report3.json ...]")
        print("\nExample:")
        print("  python compare_results.py gemini_flash.json gemini_pro.json claude.json")
        sys.exit(1)

    filenames = sys.argv[1:]

    # Load all reports
    reports = []
    labels = []

    for filename in filenames:
        report = load_report(filename)
        reports.append(report)

        # Create label from filename or use provider/model from report
        if 'provider' in report and 'model' in report:
            labels.append(f"{report['provider']}/{report['model']}")
        else:
            # Use filename without extension
            labels.append(filename.rsplit('.', 1)[0])

    # Compare
    compare_reports(reports, labels)


if __name__ == "__main__":
    main()
