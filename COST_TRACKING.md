# Cost Tracking & Token Usage Guide

Complete guide to understanding and managing costs when running prompt injection tests.

## Overview

The test suite now includes comprehensive cost tracking that:
- **Estimates costs before running** tests
- **Asks for confirmation** before spending money
- **Tracks actual token usage** during tests
- **Logs all costs** to a file for historical analysis
- **Shows cost summaries** after tests complete

## Quick Start

### Check Costs Without Running Tests

```bash
# Check costs for a specific model
python check_cost.py --model gemini-2.0-flash-001

# See what 100 full test runs would cost
python check_cost.py --model gpt-4o --tests 5900
```

### Run Tests with Cost Confirmation

```bash
# Will show cost estimate and ask for confirmation
python automated_injection_tests.py

# Skip confirmation (auto-accept)
python automated_injection_tests.py --yes
```

## Cost Estimation

Before any tests run, you'll see an estimate like this:

```
======================================================================
COST ESTIMATE
======================================================================

Cost Estimate:
  Model: gemini-2.0-flash-001 (Google Vertex AI)
  Tokens: 31,980 input + 17,700 output = 49,680 total
  Cost: €0.0022 + €0.0050 = €0.0072

  Pricing: €0.07/€0.28 per 1M tokens (input/output)

Historical Usage (last 30 days):
  Total Cost: €0.0156
  Total Tokens: 124,560
  Total Requests: 147

======================================================================

Do you want to proceed with this test? (yes/no):
```

### Understanding the Estimate

- **Tokens**: Estimated based on average prompt/response lengths
- **Cost**: Calculated using current model pricing
- **Historical**: Shows your past 30 days of usage

## Actual Cost Tracking

During test execution, every API call is:
1. **Token counted** (input + output)
2. **Cost calculated** (based on model pricing)
3. **Logged to file** (`cost_logs.jsonl`)

After tests complete, you see actual costs:

```
======================================================================
COST SUMMARY
======================================================================

Session Duration: 142.3 seconds
Total Requests: 59
Total Tokens: 48,234
Total Cost: €0.0069

Breakdown by Model:
  gemini-2.0-flash-001
    Requests: 59
    Tokens:   48,234
    Cost:     €0.0069
======================================================================
```

## Model Pricing

Current pricing (as of January 2025) in EUR:

### Google Gemini

| Model | Input (€/1M tokens) | Output (€/1M tokens) | Notes |
|-------|---------------------|----------------------|-------|
| gemini-2.0-flash-exp | FREE | FREE | Preview only |
| gemini-2.0-flash-001 | €0.07 | €0.28 | Recommended |
| gemini-1.5-flash | €0.07 | €0.28 | Stable |
| gemini-1.5-pro | €1.16 | €4.65 | High quality |

### OpenAI

| Model | Input (€/1M tokens) | Output (€/1M tokens) |
|-------|---------------------|----------------------|
| gpt-4o-mini | €0.14 | €0.56 |
| gpt-4o | €2.33 | €9.30 |
| gpt-4-turbo | €9.30 | €27.90 |
| gpt-3.5-turbo | €0.47 | €1.40 |

### Anthropic Claude

| Model | Input (€/1M tokens) | Output (€/1M tokens) |
|-------|---------------------|----------------------|
| claude-3-5-haiku | €0.93 | €4.65 |
| claude-3-5-sonnet | €2.79 | €13.95 |
| claude-3-opus | €13.95 | €69.75 |

## Estimated Costs per Test Run

### Full Test Suite (59 tests)

| Model | Estimated Cost | Tokens |
|-------|---------------|---------|
| gemini-2.0-flash-exp | €0.00 | ~50,000 |
| gemini-2.0-flash-001 | €0.01 | ~50,000 |
| gemini-1.5-pro | €0.34 | ~50,000 |
| gpt-4o-mini | €0.04 | ~50,000 |
| gpt-4o | €0.68 | ~50,000 |
| claude-3-5-haiku | €0.31 | ~50,000 |
| claude-3-5-sonnet | €0.94 | ~50,000 |

### Quick Test (14 tests)

| Model | Estimated Cost | Tokens |
|-------|---------------|---------|
| gemini-2.0-flash-001 | <€0.01 | ~12,000 |
| gpt-4o-mini | €0.01 | ~12,000 |
| gpt-4o | €0.16 | ~12,000 |
| claude-3-5-sonnet | €0.22 | ~12,000 |

## Cost Logging

All costs are logged to `cost_logs.jsonl` (JSON Lines format).

### Log Entry Format

```json
{
  "timestamp": "2025-01-07T19:30:15.123456",
  "session_start": "2025-01-07T19:28:00.000000",
  "model": "gemini-2.0-flash-001",
  "test_name": "Direct Injection / Jailbreak",
  "input_tokens": 542,
  "output_tokens": 287,
  "total_tokens": 829,
  "cost_eur": 0.0001,
  "cost_breakdown": {
    "input_eur": 0.00004,
    "output_eur": 0.00008
  },
  "metadata": {
    "target_recipe": null,
    "prompt_preview": "IGNORE ALL PREVIOUS INSTRUCTIONS..."
  }
}
```

### Analyzing Logs

```bash
# View recent logs
tail -20 cost_logs.jsonl

# Count total requests
wc -l cost_logs.jsonl

# Calculate total cost (requires jq)
cat cost_logs.jsonl | jq -s 'map(.cost_eur) | add'
```

## Budget Planning

### Examples

**€1 Budget:**
- ~140 full tests with gemini-2.0-flash-001
- ~1.5 full tests with gpt-4o
- ~1 full test with claude-3-5-sonnet

**€10 Budget:**
- ~1,400 full tests with gemini-2.0-flash-001
- ~15 full tests with gpt-4o
- ~10 full tests with claude-3-5-sonnet

**€50 Budget:**
- ~7,000 full tests with gemini-2.0-flash-001
- ~75 full tests with gpt-4o
- ~50 full tests with claude-3-5-sonnet

### Cost-Effective Testing Strategy

1. **Development**: Use gemini-2.0-flash-exp (FREE) or gemini-2.0-flash-001 (cheap)
2. **Validation**: Test with gpt-4o-mini or claude-3-5-haiku
3. **Final Verification**: Run 1-2 tests with premium models

## Command Reference

### Run with Cost Tracking

```bash
# Full test with confirmation
python automated_injection_tests.py

# Skip confirmation
python automated_injection_tests.py --yes

# Test specific model
python automated_injection_tests.py --model gemini-1.5-pro

# Quick test with confirmation
python quick_test.py

# Quick test auto-confirm
python quick_test.py --yes
```

### Check Costs

```bash
# Basic cost check
python check_cost.py --model gemini-2.0-flash-001

# Check for custom number of tests
python check_cost.py --model gpt-4o --tests 100

# Show more historical data
python check_cost.py --model claude-3-5-sonnet --history 90
```

## Features

### Pre-Run Confirmation

Shows:
- Model and provider
- Estimated tokens (input + output)
- Estimated cost
- Historical usage (if any)
- Budget projections

### Real-Time Tracking

During tests:
- Counts actual tokens used
- Calculates actual costs
- Logs each request

### Post-Run Summary

After tests:
- Total requests made
- Total tokens used
- Actual cost incurred
- Breakdown by model (if multiple)
- Session duration

## Tips for Saving Money

1. **Use Free Models First**
   - gemini-2.0-flash-exp is currently free
   - Perfect for development and iteration

2. **Run Quick Tests During Development**
   - 14 tests vs 59 tests = ~4x cheaper
   - Iterate faster, spend less

3. **Batch Your Testing**
   - Run full suite less frequently
   - Use quick tests for rapid iteration

4. **Monitor Your Logs**
   - Check `cost_logs.jsonl` regularly
   - Track spending trends

5. **Set a Budget Alert**
   - Check historical costs before running
   - Stop if you're approaching your limit

## Token Counting

Token counts are estimated using:

1. **tiktoken** (if installed): Most accurate for OpenAI/similar models
2. **Character-based estimate** (fallback): ~3.5 characters per token

To improve accuracy:
```bash
pip install tiktoken
```

## Troubleshooting

### "Model not found in pricing database"

The system will use conservative estimates (€30 input, €80 output per 1M tokens). Update `pricing_config.py` to add your model's actual pricing.

### Costs seem high

- Check the model you're using - some are much more expensive
- Verify pricing in `pricing_config.py` matches current rates
- Consider switching to a cheaper model for testing

### Historical costs not showing

- Cost logs are stored in `cost_logs.jsonl`
- File is created after first run
- Only shows data from runs using the cost tracking system

## Example Workflow

```bash
# 1. Check what it will cost
python check_cost.py --model gemini-2.0-flash-001

# 2. Run quick test first (cheaper)
python quick_test.py

# 3. If needed, run full suite
python automated_injection_tests.py

# 4. Review costs
tail cost_logs.jsonl

# 5. Compare different models
python check_cost.py --model gpt-4o
python check_cost.py --model claude-3-5-sonnet
```

## Advanced: Cost Optimization

### Compare Models Before Running

```bash
for model in gemini-2.0-flash-001 gpt-4o-mini claude-3-5-haiku; do
  echo "=== $model ==="
  python check_cost.py --model $model --tests 59
done
```

### Track Daily Spending

Add to your shell rc file:
```bash
alias check_spending='cat cost_logs.jsonl | jq -s "map(select(.timestamp > \"$(date -d "1 day ago" -I)\")) | map(.cost_eur) | add"'
```

Then run:
```bash
check_spending  # Shows spending in last 24 hours
```

---

**Remember**: Always check costs before running, especially with expensive models!
