"""
Cost Checker Utility

Check estimated costs for running tests without actually running them.
"""

import argparse
from token_counter import estimate_test_suite_cost
from pricing_config import format_cost_summary, get_model_pricing
from cost_logger import get_cost_logger


def main():
    parser = argparse.ArgumentParser(description="Check estimated costs for test suite")
    parser.add_argument("--model", type=str, required=True, help="Model name")
    parser.add_argument("--tests", type=int, default=59, help="Number of tests (default: 59 for full suite)")
    parser.add_argument("--history", type=int, default=30, help="Days of historical usage to show (default: 30)")

    args = parser.parse_args()

    print("\n" + "="*70)
    print("COST CHECKER")
    print("="*70)

    # Show model pricing
    pricing = get_model_pricing(args.model)
    print(f"\nModel: {args.model}")
    print(f"Provider: {pricing.get('provider', 'Unknown')}")
    print(f"Pricing: €{pricing['input']:.2f}/€{pricing['output']:.2f} per 1M tokens (input/output)")

    if 'notes' in pricing:
        print(f"Note: {pricing['notes']}")

    # Estimate costs for full suite
    cost_full = estimate_test_suite_cost(59, args.model)
    print("\n" + "-"*70)
    print(f"Full Test Suite (59 tests):")
    print(f"  Estimated Cost: €{cost_full['total_cost_eur']:.4f}")
    print(f"  Estimated Tokens: {cost_full['total_tokens']:,}")

    # Estimate costs for quick test
    cost_quick = estimate_test_suite_cost(14, args.model)
    print("\n" + "-"*70)
    print(f"Quick Test (14 tests):")
    print(f"  Estimated Cost: €{cost_quick['total_cost_eur']:.4f}")
    print(f"  Estimated Tokens: {cost_quick['total_tokens']:,}")

    # Custom number of tests
    if args.tests not in [59, 14]:
        cost_custom = estimate_test_suite_cost(args.tests, args.model)
        print("\n" + "-"*70)
        print(f"Custom ({args.tests} tests):")
        print(f"  Estimated Cost: €{cost_custom['total_cost_eur']:.4f}")
        print(f"  Estimated Tokens: {cost_custom['total_tokens']:,}")

    # Show historical costs
    logger = get_cost_logger()
    historical = logger.get_total_historical_cost(days=args.history)

    if historical["total_cost_eur"] > 0:
        print("\n" + "-"*70)
        print(f"Historical Usage (last {args.history} days):")
        print(f"  Total Cost: €{historical['total_cost_eur']:.4f}")
        print(f"  Total Tokens: {historical['total_tokens']:,}")
        print(f"  Total Requests: {historical['total_requests']}")
        print(f"  Average Cost per Request: €{historical['total_cost_eur']/historical['total_requests']:.4f}")

    # Projections
    print("\n" + "="*70)
    print("COST PROJECTIONS")
    print("="*70)

    # 100 runs projection
    cost_100 = estimate_test_suite_cost(59 * 100, args.model)
    print(f"\n100 Full Test Runs: €{cost_100['total_cost_eur']:.2f}")

    # Monthly projection (1 test per day)
    cost_month = estimate_test_suite_cost(59 * 30, args.model)
    print(f"1 Full Test Daily for 30 days: €{cost_month['total_cost_eur']:.2f}")

    # Budget estimates
    budgets = [1.0, 5.0, 10.0, 50.0]
    print("\n" + "-"*70)
    print("Tests per Budget:")
    for budget in budgets:
        if cost_full['total_cost_eur'] > 0:
            num_runs = int(budget / cost_full['total_cost_eur'])
            total_tests = num_runs * 59
            print(f"  €{budget:.0f} budget: {num_runs} full test runs ({total_tests} total tests)")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
