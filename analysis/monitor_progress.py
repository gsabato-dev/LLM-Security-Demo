"""
Real-time Progress Monitor for Prompt Version Comparison Tests

Displays live progress while tests are running.
"""

import os
import sys
import time
import glob
import json
from datetime import datetime, timedelta
from pathlib import Path


VERSIONS = ["strict", "moderate", "relaxed", "none"]
TESTS_PER_VERSION = 59


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_terminal_width():
    """Get terminal width for progress bar."""
    try:
        return os.get_terminal_size().columns
    except:
        return 80


def draw_progress_bar(current, total, width=50, label=""):
    """Draw a progress bar."""
    filled = int(width * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    percentage = (current / total * 100) if total > 0 else 0
    return f"{label} [{bar}] {current}/{total} ({percentage:.1f}%)"


def count_completed_reports(report_dir="reports"):
    """Count how many version reports have been completed."""
    completed = {}

    for version in VERSIONS:
        pattern = f"{report_dir}/report_{version}_*.json"
        files = glob.glob(pattern)

        if files:
            # Get the most recent file
            latest_file = max(files, key=lambda x: Path(x).stat().st_mtime)

            # Check if it's a complete report
            try:
                with open(latest_file, 'r') as f:
                    data = json.load(f)

                    # Handle different report structures
                    if "report" in data:
                        # New structure: report.summary.total_tests
                        report = data["report"]
                        summary = report.get("summary", {})
                        metadata = data.get("metadata", {})

                        completed[version] = {
                            "file": latest_file,
                            "tests": summary.get("total_tests", 0),
                            "leaks": summary.get("successful_leaks", 0),
                            "cost": metadata.get("cost_eur", 0),
                            "time": metadata.get("execution_time_seconds", 0)
                        }
                    elif "total_tests" in data:
                        # Old structure: direct keys
                        completed[version] = {
                            "file": latest_file,
                            "tests": data.get("total_tests", 0),
                            "leaks": data.get("successful_leaks", 0),
                            "cost": data.get("metadata", {}).get("cost_eur", 0),
                            "time": data.get("metadata", {}).get("execution_time_seconds", 0)
                        }
            except:
                pass

    return completed


def get_current_test_from_log(log_file="prompt_comparison.log"):
    """Try to determine current test from log file."""
    if not os.path.exists(log_file):
        return None, None

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

        # Look for recent test indicators
        for line in reversed(lines[-100:]):  # Check last 100 lines
            # Look for version being tested
            if "TESTING PROMPT VERSION:" in line:
                version = line.split(":")[-1].strip().lower()
                return version, None

            # Look for individual test progress
            if "[" in line and "/" in line and "]" in line:
                try:
                    # Extract [X/Y] pattern
                    bracket_content = line[line.find("[")+1:line.find("]")]
                    if "/" in bracket_content:
                        current, total = bracket_content.split("/")
                        return None, (int(current), int(total))
                except:
                    pass
    except:
        pass

    return None, None


def format_time(seconds):
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds / 3600)
        mins = int((seconds % 3600) / 60)
        return f"{hours}h {mins}m"


def display_progress(report_dir="reports", log_file="prompt_comparison.log"):
    """Display live progress dashboard."""

    completed = count_completed_reports(report_dir)
    current_version, current_test = get_current_test_from_log(log_file)

    # Calculate overall progress
    total_versions = len(VERSIONS)
    completed_versions = len(completed)

    # Terminal width for responsive display
    term_width = get_terminal_width()
    bar_width = min(50, term_width - 30)

    # Header
    print("=" * term_width)
    print("  PROMPT VERSION COMPARISON - LIVE PROGRESS")
    print("=" * term_width)
    print()

    # Overall progress
    overall_bar = draw_progress_bar(
        completed_versions,
        total_versions,
        width=bar_width,
        label="Overall Progress"
    )
    print(overall_bar)
    print()

    # Version-by-version status
    print("─" * term_width)
    print("VERSION STATUS:")
    print("─" * term_width)

    total_cost = 0
    total_leaks = 0
    total_tests = 0

    for i, version in enumerate(VERSIONS, 1):
        status_icon = "✓" if version in completed else "⏳" if version == current_version else "⏸"
        status_text = "DONE" if version in completed else "RUNNING" if version == current_version else "PENDING"

        print(f"{i}. {status_icon} {version.upper():<12} ", end="")

        if version in completed:
            data = completed[version]
            leak_indicator = "🔴" if data["leaks"] > 0 else "✅"
            print(f"[{status_text}] - {data['tests']} tests, {data['leaks']} leaks {leak_indicator}, €{data['cost']:.4f}, {format_time(data['time'])}")
            total_cost += data["cost"]
            total_leaks += data["leaks"]
            total_tests += data["tests"]
        elif version == current_version:
            if current_test:
                mini_bar = draw_progress_bar(current_test[0], current_test[1], width=20, label="")
                print(f"[{status_text}] - {mini_bar}")
            else:
                print(f"[{status_text}]")
        else:
            print(f"[{status_text}]")

    # Summary statistics
    if completed:
        print()
        print("─" * term_width)
        print("SUMMARY (Completed Versions):")
        print("─" * term_width)
        print(f"  Total Tests:      {total_tests}")
        print(f"  Total Leaks:      {total_leaks} ({total_leaks/total_tests*100:.1f}%)" if total_tests > 0 else "  Total Leaks:      0")
        print(f"  Total Cost:       €{total_cost:.4f}")
        print(f"  Avg Cost/Version: €{total_cost/len(completed):.4f}")

    print()
    print("=" * term_width)

    # Status message
    if completed_versions == total_versions:
        print("✓ ALL TESTS COMPLETED!")
        print("\nRun: python analyze_prompt_comparison.py")
        return True
    elif current_version:
        print(f"⏳ Currently testing: {current_version.upper()}")
        remaining = total_versions - completed_versions
        print(f"   {remaining} version(s) remaining")
        return False
    else:
        print("⏸  Waiting for tests to start...")
        return False


def monitor_loop(report_dir="reports", log_file="prompt_comparison.log", refresh_interval=5):
    """Main monitoring loop."""

    start_time = time.time()

    try:
        while True:
            clear_screen()

            # Display progress
            completed = display_progress(report_dir, log_file)

            # Show elapsed time
            elapsed = time.time() - start_time
            print(f"\nElapsed Time: {format_time(elapsed)}")
            print(f"Refreshing every {refresh_interval}s... (Press Ctrl+C to exit)")

            # Exit if completed
            if completed:
                print("\n🎉 Testing complete! Exiting monitor...")
                break

            # Wait before next refresh
            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        sys.exit(0)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor prompt version comparison progress")
    parser.add_argument("--report-dir", type=str, default="reports", help="Directory containing reports")
    parser.add_argument("--log-file", type=str, default="prompt_comparison.log", help="Log file to monitor")
    parser.add_argument("--interval", type=int, default=5, help="Refresh interval in seconds")
    parser.add_argument("--once", action="store_true", help="Show progress once and exit (no loop)")

    args = parser.parse_args()

    if args.once:
        # Single display
        display_progress(args.report_dir, args.log_file)
    else:
        # Continuous monitoring
        monitor_loop(args.report_dir, args.log_file, args.interval)


if __name__ == "__main__":
    main()
