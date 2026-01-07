"""
Compare Prompt Versions Script

Runs the full test suite for all prompt versions and generates a comparison report.
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List
from pathlib import Path

PROMPT_VERSIONS = ["strict", "moderate", "relaxed", "minimal", "none"]


def run_test_for_version(version: str, output_dir: str = "reports") -> Dict:
    """Run full test suite for a specific prompt version."""
    print(f"\n{'='*70}")
    print(f"TESTING PROMPT VERSION: {version.upper()}")
    print(f"{'='*70}\n")
    sys.stdout.flush()  # Ensure output is written immediately

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/report_{version}_{timestamp}.json"

    # Run the test suite
    cmd = [
        "python",
        "automated_injection_tests.py",
        "--prompt-version", version,
        "--output", output_file,
        "--yes"  # Auto-confirm
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✓ Test completed for {version}")
        print(f"  Report saved to: {output_file}")

        # Load and return the report
        with open(output_file, 'r') as f:
            report = json.load(f)

        return {
            "version": version,
            "output_file": output_file,
            "report": report,
            "success": True
        }

    except subprocess.CalledProcessError as e:
        print(f"✗ Error testing {version}: {e}")
        return {
            "version": version,
            "output_file": None,
            "report": None,
            "success": False,
            "error": str(e)
        }


def generate_comparison_report(results: List[Dict], output_file: str = "prompt_version_comparison.json"):
    """Generate a comparison report from all test results."""

    comparison = {
        "timestamp": datetime.now().isoformat(),
        "versions_tested": len(results),
        "summary": {},
        "detailed_comparison": {},
        "attack_type_comparison": {},
        "cost_comparison": {}
    }

    # Summary for each version
    for result in results:
        if not result["success"]:
            continue

        version = result["version"]
        report = result["report"]

        comparison["summary"][version] = {
            "total_tests": report.get("total_tests", 0),
            "successful_leaks": report.get("successful_leaks", 0),
            "failed_attacks": report.get("failed_attacks", 0),
            "leak_percentage": report.get("successful_leaks", 0) / report.get("total_tests", 1) * 100,
            "report_file": result["output_file"]
        }

        # Cost information
        if "metadata" in report and "cost_eur" in report["metadata"]:
            comparison["cost_comparison"][version] = {
                "total_cost_eur": report["metadata"]["cost_eur"],
                "total_tokens": report["metadata"].get("total_tokens", 0)
            }

    # Attack type comparison
    attack_types = set()
    for result in results:
        if result["success"] and result["report"]:
            for attack_type in result["report"].get("results_by_attack_type", {}).keys():
                attack_types.add(attack_type)

    for attack_type in attack_types:
        comparison["attack_type_comparison"][attack_type] = {}

        for result in results:
            if not result["success"]:
                continue

            version = result["version"]
            attack_data = result["report"].get("results_by_attack_type", {}).get(attack_type, {})

            comparison["attack_type_comparison"][attack_type][version] = {
                "successful": attack_data.get("successful", 0),
                "total": attack_data.get("total", 0),
                "success_rate": attack_data.get("success_rate", 0)
            }

    # Detailed comparison
    for result in results:
        if not result["success"]:
            continue

        version = result["version"]
        report = result["report"]

        comparison["detailed_comparison"][version] = {
            "test_details": report.get("test_details", []),
            "compromised_recipes": report.get("compromised_recipes", []),
            "execution_time": report.get("metadata", {}).get("execution_time_seconds", 0)
        }

    # Save comparison report
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)

    print(f"\n📊 Comparison report saved to: {output_file}")
    return comparison


def print_comparison_summary(comparison: Dict):
    """Print a human-readable comparison summary."""

    print("\n" + "="*70)
    print("PROMPT VERSION COMPARISON SUMMARY")
    print("="*70)

    # Overall summary
    print("\n--- OVERALL RESULTS ---\n")
    print(f"{'Version':<15} {'Tests':<10} {'Leaks':<10} {'Defense Rate':<15}")
    print("-" * 70)

    for version, data in comparison["summary"].items():
        defense_rate = 100 - data["leak_percentage"]
        print(f"{version:<15} {data['total_tests']:<10} {data['successful_leaks']:<10} {defense_rate:>6.1f}%")

    # Cost comparison
    if comparison["cost_comparison"]:
        print("\n--- COST COMPARISON ---\n")
        print(f"{'Version':<15} {'Cost (EUR)':<15} {'Tokens':<15}")
        print("-" * 70)

        for version, data in comparison["cost_comparison"].items():
            print(f"{version:<15} €{data['total_cost_eur']:<14.4f} {data['total_tokens']:<15,}")

    # Attack type comparison
    print("\n--- ATTACK TYPE EFFECTIVENESS ---\n")
    print(f"{'Attack Type':<45} {'Strict':<10} {'Moderate':<10} {'Relaxed':<10} {'Minimal':<10} {'None':<10}")
    print("-" * 110)

    for attack_type, versions in comparison["attack_type_comparison"].items():
        attack_name = attack_type[:42] + "..." if len(attack_type) > 42 else attack_type
        row = f"{attack_name:<45}"

        for version in PROMPT_VERSIONS:
            if version in versions:
                success_rate = versions[version]["success_rate"]
                row += f" {success_rate:>6.1f}%   "
            else:
                row += " N/A      "

        print(row)

    # Find most vulnerable prompt versions
    print("\n--- VULNERABILITY RANKING ---\n")
    sorted_versions = sorted(
        comparison["summary"].items(),
        key=lambda x: x[1]["leak_percentage"],
        reverse=True
    )

    for i, (version, data) in enumerate(sorted_versions, 1):
        leak_pct = data["leak_percentage"]
        status = "🔴 CRITICAL" if leak_pct > 50 else "🟠 HIGH" if leak_pct > 20 else "🟡 MEDIUM" if leak_pct > 5 else "🟢 LOW" if leak_pct > 0 else "✅ SECURE"
        print(f"{i}. {version.upper():<15} - {leak_pct:>5.1f}% leak rate - {status}")

    print("\n" + "="*70 + "\n")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Compare all prompt versions")
    parser.add_argument("--output-dir", type=str, default="reports", help="Directory to store reports")
    parser.add_argument("--delay", type=float, default=10.0, help="Delay between version tests (seconds)")
    parser.add_argument("--versions", nargs="+", choices=PROMPT_VERSIONS, default=PROMPT_VERSIONS, help="Specific versions to test")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    print("="*70)
    print("PROMPT VERSION COMPARISON TEST SUITE")
    print("="*70)
    print(f"\nVersions to test: {', '.join(args.versions)}")
    print(f"Output directory: {args.output_dir}")
    print(f"Delay between tests: {args.delay}s")
    print("\nThis will run the FULL test suite (59 tests) for each version.")
    print("Estimated time: ~5-10 minutes per version")
    print(f"Total estimated time: ~{len(args.versions) * 7} minutes")

    # Confirm
    if not args.yes:
        response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Test cancelled.")
            return
    else:
        print("\nAuto-confirming (--yes flag used)")

    start_time = time.time()
    results = []

    # Run tests for each version
    for i, version in enumerate(args.versions, 1):
        print(f"\n[{i}/{len(args.versions)}] Starting tests for '{version}' prompt version...")

        result = run_test_for_version(version, args.output_dir)
        results.append(result)

        # Delay between tests (except after last one)
        if i < len(args.versions):
            print(f"\nWaiting {args.delay}s before next test...")
            time.sleep(args.delay)

    # Generate comparison report
    print("\n" + "="*70)
    print("GENERATING COMPARISON REPORT")
    print("="*70)

    comparison = generate_comparison_report(results)
    print_comparison_summary(comparison)

    # Overall summary
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"✓ All tests completed in {minutes}m {seconds}s")
    print(f"✓ Individual reports saved in: {args.output_dir}/")
    print(f"✓ Comparison report: prompt_version_comparison.json")


if __name__ == "__main__":
    main()
