# Prompt Version Comparison Testing Guide

## Overview

This guide explains how to run comprehensive comparison tests across all prompt security levels and analyze the results.

## Quick Start

### Run All Tests Automatically

```bash
# Run full comparison (all 5 versions, ~35 minutes)
python compare_prompt_versions.py --yes

# Run with custom delay between tests
python compare_prompt_versions.py --delay 10 --yes

# Run only specific versions
python compare_prompt_versions.py --versions strict moderate --yes
```

### Analyze Existing Results

```bash
# Generate comparison analysis from existing reports
python analyze_prompt_comparison.py

# Specify custom report directory
python analyze_prompt_comparison.py --report-dir my_reports
```

## Available Scripts

### 1. `compare_prompt_versions.py`

**Purpose**: Automatically runs the full test suite (59 tests) for all prompt versions.

**Features**:
- Runs tests sequentially with configurable delays
- Saves individual reports for each version
- Generates a combined comparison JSON
- Prints summary statistics
- Estimates total time and costs

**Usage**:
```bash
python compare_prompt_versions.py [OPTIONS]

Options:
  --output-dir DIR     Directory to store reports (default: reports)
  --delay SECONDS      Delay between version tests (default: 10.0)
  --versions V1 V2...  Specific versions to test (default: all)
  --yes, -y            Skip confirmation prompt
```

**Example**:
```bash
# Test all versions with 5-second delays
python compare_prompt_versions.py --delay 5 --yes

# Test only weak versions
python compare_prompt_versions.py --versions relaxed minimal none --yes

# Save to custom directory
python compare_prompt_versions.py --output-dir my_test_results --yes
```

**Output**:
- Individual reports: `reports/report_{version}_{timestamp}.json`
- Comparison JSON: `prompt_version_comparison.json`
- Console summary with tables and statistics

### 2. `analyze_prompt_comparison.py`

**Purpose**: Analyzes existing test reports and generates detailed comparisons.

**Features**:
- Loads most recent report for each version
- Identifies attack patterns
- Shows which attacks work on which versions
- Generates markdown report
- Calculates detailed statistics

**Usage**:
```bash
python analyze_prompt_comparison.py [OPTIONS]

Options:
  --report-dir DIR     Directory containing reports (default: reports)
  --output FILE        Output markdown file (default: COMPARISON_REPORT.md)
```

**Example**:
```bash
# Analyze with defaults
python analyze_prompt_comparison.py

# Custom input/output
python analyze_prompt_comparison.py \
  --report-dir my_reports \
  --output MY_ANALYSIS.md
```

**Output**:
- Markdown report: `COMPARISON_REPORT.md`
- Console output with:
  - Statistics per version
  - Attack pattern analysis
  - Vulnerability rankings
  - Cost comparisons

### 3. `automated_injection_tests.py` (Enhanced)

**Purpose**: Original test suite, now with prompt version support.

**New Usage**:
```bash
# Test with specific prompt version
python automated_injection_tests.py --prompt-version moderate --yes

# Test all versions manually
for version in strict moderate relaxed minimal none; do
  python automated_injection_tests.py \
    --prompt-version $version \
    --output "report_${version}.json" \
    --yes
  sleep 10
done
```

### 4. `quick_test.py` (Enhanced)

**Purpose**: Fast testing (14 tests instead of 59).

**New Usage**:
```bash
# Quick test with different versions
python quick_test.py --prompt-version relaxed --yes
python quick_test.py --prompt-version none --yes
```

## Workflow Examples

### Complete Comparison Workflow

```bash
# Step 1: Run all comparison tests
python compare_prompt_versions.py --yes

# Step 2: Wait for completion (~35 minutes)
# You can monitor progress by checking the reports/ directory

# Step 3: Analyze results
python analyze_prompt_comparison.py

# Step 4: Review the markdown report
cat COMPARISON_REPORT.md

# Step 5: Check individual reports if needed
ls -lh reports/
```

### Quick Comparison (Subset)

```bash
# Test just weak vs strong
python compare_prompt_versions.py --versions strict none --yes

# Wait ~15 minutes

# Analyze
python analyze_prompt_comparison.py
```

### Research Workflow

```bash
# Test different models with same prompt versions
for model in gemini-2.0-flash-001 gpt-4o-mini; do
  for version in strict moderate relaxed; do
    python automated_injection_tests.py \
      --model $model \
      --prompt-version $version \
      --output "report_${model}_${version}.json" \
      --yes
    sleep 10
  done
done
```

## Understanding Results

### Output Files

**Individual Reports** (`reports/report_{version}_{timestamp}.json`):
```json
{
  "total_tests": 59,
  "successful_leaks": 0,
  "failed_attacks": 59,
  "results_by_attack_type": { ... },
  "test_details": [ ... ],
  "compromised_recipes": [],
  "metadata": {
    "cost_eur": 0.0069,
    "total_tokens": 48234,
    ...
  }
}
```

**Comparison Report** (`prompt_version_comparison.json`):
```json
{
  "timestamp": "2026-01-07T20:00:00",
  "summary": {
    "strict": {
      "total_tests": 59,
      "successful_leaks": 0,
      "leak_percentage": 0.0
    },
    ...
  },
  "attack_type_comparison": { ... },
  "cost_comparison": { ... }
}
```

**Markdown Report** (`COMPARISON_REPORT.md`):
- Human-readable tables
- Attack type breakdown
- Cost comparison
- Recommendations

### Interpreting Results

**Defense Rate**:
- 100% = Perfect defense
- 90-99% = Strong defense (minor vulnerabilities)
- 70-89% = Moderate defense
- <70% = Weak defense

**Attack Success Indicators**:
- ✅ 0/{total} = All attacks blocked
- 🔴 {n}/{total} = Some attacks succeeded

**Cost Considerations**:
- Strict prompts may use slightly more tokens (longer)
- Difference is typically negligible (< €0.001 per test)

## Time & Cost Estimates

### Full Comparison (All 5 Versions)

| Metric | Estimate |
|--------|----------|
| Total tests | 295 (59 × 5) |
| Time | ~35-40 minutes |
| Cost (gemini-2.0-flash-001) | ~€0.035 |
| Cost (gpt-4o-mini) | ~€0.20 |
| Cost (gpt-4o) | ~€3.40 |

### Quick Comparison (3 Versions)

| Metric | Estimate |
|--------|----------|
| Total tests | 177 (59 × 3) |
| Time | ~20-25 minutes |
| Cost (gemini-2.0-flash-001) | ~€0.021 |

## Tips & Best Practices

### 1. Start with Quick Tests

```bash
# Test just 2 versions quickly
python quick_test.py --prompt-version strict --yes
python quick_test.py --prompt-version none --yes
```

### 2. Use Appropriate Delays

```bash
# Faster testing (if provider allows)
python compare_prompt_versions.py --delay 2 --yes

# Conservative (avoid rate limits)
python compare_prompt_versions.py --delay 15 --yes
```

### 3. Monitor Progress

```bash
# In another terminal, watch report directory
watch -n 5 'ls -lh reports/ | tail -10'

# Or check cost logs
tail -f cost_logs.jsonl
```

### 4. Save Results by Date

```bash
# Create dated directory
mkdir -p results/$(date +%Y%m%d)

# Run tests with custom output
python compare_prompt_versions.py \
  --output-dir results/$(date +%Y%m%d) \
  --yes
```

### 5. Analyze Incrementally

```bash
# Don't wait for all tests - analyze partial results
python analyze_prompt_comparison.py

# Re-run after more tests complete
python analyze_prompt_comparison.py
```

## Troubleshooting

### Tests Taking Too Long

- Use `quick_test.py` instead (14 tests vs 59)
- Test fewer versions: `--versions strict none`
- Reduce delay: `--delay 2`

### Rate Limit Errors

- Increase delay: `--delay 30`
- Test fewer versions at once
- Use cheaper model (gemini-2.0-flash-001)

### Out of Memory

- Tests run sequentially, shouldn't cause memory issues
- Close other applications
- Check provider connection

### Reports Not Found

```bash
# Verify reports exist
ls -lh reports/

# Check for errors in individual test runs
cat reports/report_*.json | jq '.metadata.error'

# Re-run failed versions
python automated_injection_tests.py --prompt-version {failed_version} --yes
```

## Advanced Usage

### Custom Prompt Versions

1. Edit `prompt_versions.py`:
```python
PROMPT_VERSIONS["custom"] = {
    "name": "Custom Test",
    "description": "My experimental prompt",
    "prompt": "Your system prompt here..."
}
```

2. Run tests:
```bash
python automated_injection_tests.py --prompt-version custom --yes
```

### Parallel Testing (Different Models)

```bash
# Test multiple models in parallel (different terminals)
# Terminal 1:
python compare_prompt_versions.py --model gemini-2.0-flash-001 --yes

# Terminal 2:
python compare_prompt_versions.py --model gpt-4o-mini --yes
```

### Automated Daily Testing

Create a cron job:
```bash
# Daily comparison test at 2 AM
0 2 * * * cd /path/to/project && source venv/bin/activate && python compare_prompt_versions.py --yes >> daily_test.log 2>&1
```

## What to Look For

### Security Assessment

1. **Zero leaks on strict**: ✅ Good baseline
2. **Leaks on moderate**: ⚠️ Consider strengthening
3. **Attack patterns**: Which types succeed on weak prompts?
4. **Cost vs security**: Is strict worth the extra cost?

### Attack Analysis

- **Direct injection**: Basic attacks (should all fail on strict)
- **Social engineering**: Tricky attacks (may succeed on weak)
- **Obfuscation**: Encoded attacks (tests detection)
- **Role-play**: Confusion tactics (tests consistency)

### Recommendations

Based on results:
- **0% leaks**: Current prompt is sufficient
- **1-5% leaks**: Minor tweaks needed
- **5-20% leaks**: Significant improvements needed
- **>20% leaks**: Consider stricter prompt version

---

**Pro Tip**: Run comparison tests periodically (e.g., monthly) to track how defenses hold up against evolving attack techniques!
