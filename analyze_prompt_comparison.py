"""
Analyze and visualize prompt version comparison results.

This script reads the existing reports and generates detailed analysis.
"""

import json
import glob
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def load_latest_reports(report_dir: str = "reports") -> dict:
    """Load the most recent report for each prompt version."""

    reports = {}
    versions = ["strict", "moderate", "relaxed", "minimal", "none"]

    for version in versions:
        # Find all reports for this version
        pattern = f"{report_dir}/report_{version}_*.json"
        files = glob.glob(pattern)

        if not files:
            print(f"⚠️  No report found for version: {version}")
            continue

        # Get the most recent file
        latest_file = max(files, key=lambda x: Path(x).stat().st_mtime)

        try:
            with open(latest_file, 'r') as f:
                report = json.load(f)
                reports[version] = {
                    "file": latest_file,
                    "data": report
                }
                print(f"✓ Loaded {version}: {latest_file}")
        except Exception as e:
            print(f"✗ Error loading {latest_file}: {e}")

    return reports


def analyze_attack_patterns(reports: dict):
    """Analyze which attacks work on which versions."""

    print("\n" + "="*80)
    print("ATTACK PATTERN ANALYSIS")
    print("="*80)

    # Collect all unique attacks across all reports
    all_attacks = defaultdict(lambda: defaultdict(dict))

    for version, report_info in reports.items():
        data = report_info["data"]

        # Handle nested structure
        if "detailed_results" in data:
            test_details = data["detailed_results"]
        else:
            test_details = data.get("test_details", [])

        for test_detail in test_details:
            attack_type = test_detail.get("attack_type", "Unknown")
            target = test_detail.get("target_recipe", "General")
            leaked = test_detail.get("leaked", False)

            key = f"{attack_type} ({target})"
            all_attacks[key][version] = {
                "leaked": leaked,
                "response_preview": test_detail.get("response", "")[:100]
            }

    # Find attacks that succeeded on any version
    print("\n--- ATTACKS THAT SUCCEEDED ON ANY VERSION ---\n")

    vulnerable_found = False
    for attack_key, versions in all_attacks.items():
        leaked_on = [v for v, data in versions.items() if data["leaked"]]

        if leaked_on:
            vulnerable_found = True
            print(f"🔴 {attack_key}")
            print(f"   Succeeded on: {', '.join(leaked_on)}")
            print()

    if not vulnerable_found:
        print("✅ No attacks succeeded on any version!")

    # Find attacks that work ONLY on weaker versions
    print("\n--- ATTACKS EFFECTIVE ONLY ON WEAK PROMPTS ---\n")

    weak_only = False
    weak_versions = ["minimal", "none", "relaxed"]

    for attack_key, versions in all_attacks.items():
        leaked_on_weak = [v for v in weak_versions if v in versions and versions[v]["leaked"]]
        leaked_on_strong = any(versions.get(v, {}).get("leaked", False) for v in ["strict", "moderate"])

        if leaked_on_weak and not leaked_on_strong:
            weak_only = True
            print(f"⚠️  {attack_key}")
            print(f"   Only works on: {', '.join(leaked_on_weak)}")
            print()

    if not weak_only:
        print("No attacks were exclusive to weak prompts.")


def generate_markdown_report(reports: dict, output_file: str = "COMPARISON_REPORT.md"):
    """Generate a markdown report for easy reading."""

    with open(output_file, 'w') as f:
        f.write("# Prompt Version Comparison Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Summary table
        f.write("## Summary\n\n")
        f.write("| Version | Total Tests | Successful Leaks | Failed Attacks | Defense Rate |\n")
        f.write("|---------|------------|-----------------|----------------|-------------|\n")

        for version in ["strict", "moderate", "relaxed", "minimal", "none"]:
            if version not in reports:
                f.write(f"| {version} | N/A | N/A | N/A | N/A |\n")
                continue

            data = reports[version]["data"]
            # Handle nested structure
            if "report" in data:
                report = data["report"]
                summary = report.get("summary", {})
                total = summary.get("total_tests", 0)
                leaks = summary.get("successful_leaks", 0)
                failed = summary.get("failed_attacks", 0)
            else:
                total = data.get("total_tests", 0)
                leaks = data.get("successful_leaks", 0)
                failed = data.get("failed_attacks", 0)

            defense_rate = (failed / total * 100) if total > 0 else 0

            f.write(f"| {version} | {total} | {leaks} | {failed} | {defense_rate:.1f}% |\n")

        # Attack type breakdown
        f.write("\n## Attack Type Breakdown\n\n")

        # Collect attack types
        attack_types = set()
        for report_info in reports.values():
            data = report_info["data"]
            if "report" in data:
                by_attack = data["report"].get("by_attack_type", {})
            else:
                by_attack = data.get("results_by_attack_type", {})
            attack_types.update(by_attack.keys())

        f.write("| Attack Type | Strict | Moderate | Relaxed | Minimal | None |\n")
        f.write("|-------------|--------|----------|---------|---------|------|\n")

        for attack_type in sorted(attack_types):
            f.write(f"| {attack_type} ")

            for version in ["strict", "moderate", "relaxed", "minimal", "none"]:
                if version in reports:
                    data = reports[version]["data"]
                    if "report" in data:
                        attack_data = data["report"].get("by_attack_type", {}).get(attack_type, {})
                        success_rate = attack_data.get("success_rate", 0)
                        successful = attack_data.get("leaked", 0)
                        total = attack_data.get("total", 0)
                    else:
                        attack_data = data.get("results_by_attack_type", {}).get(attack_type, {})
                        success_rate = attack_data.get("success_rate", 0)
                        successful = attack_data.get("successful", 0)
                        total = attack_data.get("total", 0)

                    if successful > 0:
                        f.write(f"| 🔴 {successful}/{total} ({success_rate:.0f}%) ")
                    else:
                        f.write(f"| ✅ 0/{total} ")
                else:
                    f.write("| N/A ")

            f.write("|\n")

        # Cost comparison
        f.write("\n## Cost Comparison\n\n")
        f.write("| Version | Total Cost (EUR) | Total Tokens |\n")
        f.write("|---------|-----------------|-------------|\n")

        for version in ["strict", "moderate", "relaxed", "minimal", "none"]:
            if version not in reports:
                f.write(f"| {version} | N/A | N/A |\n")
                continue

            report = reports[version]["data"]
            cost = report.get("metadata", {}).get("cost_eur", 0)
            tokens = report.get("metadata", {}).get("total_tokens", 0)

            f.write(f"| {version} | €{cost:.4f} | {tokens:,} |\n")

        # Recommendations
        f.write("\n## Recommendations\n\n")

        # Find the most secure version
        sorted_versions = sorted(
            reports.items(),
            key=lambda x: x[1]["data"].get("successful_leaks", 100)
        )

        most_secure = sorted_versions[0][0] if sorted_versions else "unknown"
        least_secure = sorted_versions[-1][0] if sorted_versions else "unknown"

        f.write(f"- **Most Secure**: `{most_secure}` prompt version\n")
        f.write(f"- **Least Secure**: `{least_secure}` prompt version\n\n")

        leaks_in_strict = reports.get("strict", {}).get("data", {}).get("successful_leaks", 0)
        if leaks_in_strict == 0:
            f.write("- ✅ The **strict** prompt successfully blocked all attacks\n")
        else:
            f.write(f"- ⚠️  The **strict** prompt had {leaks_in_strict} leaks - consider strengthening defenses\n")

        f.write("\n---\n\n")
        f.write("*This report was automatically generated by analyze_prompt_comparison.py*\n")

    print(f"\n📄 Markdown report saved to: {output_file}")


def calculate_statistics(reports: dict):
    """Calculate detailed statistics."""

    print("\n" + "="*80)
    print("DETAILED STATISTICS")
    print("="*80)

    for version, report_info in reports.items():
        data = report_info["data"]

        print(f"\n--- {version.upper()} ---")

        # Handle nested structure
        if "report" in data:
            report = data["report"]
            summary = report.get("summary", {})
            total = summary.get("total_tests", 0)
            leaks = summary.get("successful_leaks", 0)
            failed = summary.get("failed_attacks", 0)
            compromised = list(report.get("leaked_recipes", {}).keys())
            metadata = data.get("metadata", {})
        else:
            total = data.get("total_tests", 0)
            leaks = data.get("successful_leaks", 0)
            failed = data.get("failed_attacks", 0)
            compromised = data.get("compromised_recipes", [])
            metadata = data.get("metadata", {})

        print(f"Total Tests: {total}")
        print(f"Successful Leaks: {leaks} ({leaks/total*100:.1f}%)" if total > 0 else "Successful Leaks: 0")
        print(f"Failed Attacks: {failed} ({failed/total*100:.1f}%)" if total > 0 else "Failed Attacks: 0")

        # Compromised recipes
        if compromised:
            print(f"Compromised Recipes: {', '.join(compromised)}")
        else:
            print("Compromised Recipes: None")

        # Cost
        cost = metadata.get("cost_eur", 0)
        tokens = metadata.get("total_tokens", 0)
        print(f"Cost: €{cost:.4f}")
        print(f"Tokens: {tokens:,}")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze prompt version comparison results")
    parser.add_argument("--report-dir", type=str, default="reports", help="Directory containing reports")
    parser.add_argument("--output", type=str, default="COMPARISON_REPORT.md", help="Output markdown file")

    args = parser.parse_args()

    print("="*80)
    print("PROMPT VERSION COMPARISON ANALYSIS")
    print("="*80)

    # Load reports
    print(f"\nLoading reports from: {args.report_dir}")
    reports = load_latest_reports(args.report_dir)

    if not reports:
        print("\n❌ No reports found!")
        print("Run compare_prompt_versions.py first to generate test reports.")
        return

    print(f"\n✓ Loaded {len(reports)} report(s)")

    # Generate analysis
    calculate_statistics(reports)
    analyze_attack_patterns(reports)
    generate_markdown_report(reports, args.output)

    print("\n" + "="*80)
    print("✓ Analysis complete!")
    print(f"✓ Markdown report: {args.output}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
