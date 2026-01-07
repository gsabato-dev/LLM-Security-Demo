# Cost Tracking - Quick Summary

## ✅ What's Been Added

### 1. Pre-Run Cost Estimation
Before any test runs, you'll see:
```
COST ESTIMATE
Model: gemini-2.0-flash-001
Estimated Cost: €0.0072
Historical Usage (last 30 days): €0.0156

Do you want to proceed? (yes/no):
```

### 2. Real-Time Token & Cost Tracking
- Every API call is counted
- Actual tokens measured
- Costs calculated and logged

### 3. Post-Run Cost Summary
```
COST SUMMARY
Total Requests: 59
Total Tokens: 48,234
Total Cost: €0.0069
```

### 4. Historical Cost Logging
All costs saved to `cost_logs.jsonl` for analysis

### 5. Cost Checker Utility
Check costs without running tests:
```bash
python check_cost.py --model gemini-2.0-flash-001
```

## 🚀 Quick Start

### Check Costs First
```bash
python check_cost.py --model gemini-2.0-flash-001
```

**Output:**
- Estimated cost for full suite (59 tests): €0.0072
- Estimated cost for quick test (14 tests): €0.0017
- Budget projections (how many tests for €1, €5, €10, etc.)

### Run Tests with Confirmation
```bash
# Will ask for confirmation
python automated_injection_tests.py

# Auto-confirm (skip prompt)
python automated_injection_tests.py --yes
```

### Run Quick Test
```bash
# Cheaper - only 14 tests
python quick_test.py
```

## 💰 Example Costs

### Full Test Suite (59 tests)

| Model | Cost | Good For |
|-------|------|----------|
| gemini-2.0-flash-exp | **FREE** | Development |
| gemini-2.0-flash-001 | **€0.01** | ✅ Recommended |
| gpt-4o-mini | €0.04 | Budget testing |
| gpt-4o | €0.68 | Validation |
| claude-3-5-sonnet | €0.94 | Final check |

### Quick Test (14 tests)

| Model | Cost |
|-------|------|
| gemini-2.0-flash-001 | **<€0.01** |
| gpt-4o-mini | €0.01 |
| gpt-4o | €0.16 |

## 📊 New Features

### 1. `pricing_config.py`
- Model pricing database
- Auto-updates with current rates
- Supports all major providers

### 2. `token_counter.py`
- Accurate token counting (uses tiktoken)
- Fallback estimation if tiktoken unavailable
- Model-specific counting

### 3. `cost_logger.py`
- Logs every API call
- Tracks historical costs
- Session summaries

### 4. `check_cost.py`
- Estimate costs before running
- Compare model costs
- Budget planning tool

### 5. Updated Test Suites
Both `automated_injection_tests.py` and `quick_test.py` now:
- Show cost estimate before running
- Ask for confirmation
- Track actual costs
- Show cost summary after completion

## 💡 Best Practices

1. **Always check costs first**
   ```bash
   python check_cost.py --model YOUR_MODEL
   ```

2. **Use cheap models during development**
   - gemini-2.0-flash-exp (FREE)
   - gemini-2.0-flash-001 (€0.01 per run)

3. **Run quick tests more often**
   - 14 tests vs 59 = 4x cheaper
   - Faster iteration

4. **Monitor your spending**
   ```bash
   tail -20 cost_logs.jsonl
   ```

5. **Use --yes flag for automation**
   ```bash
   python automated_injection_tests.py --yes
   ```

## 📝 Command Cheat Sheet

```bash
# Check costs for a model
python check_cost.py --model gemini-2.0-flash-001

# Run full test with confirmation
python automated_injection_tests.py

# Run full test without confirmation
python automated_injection_tests.py --yes

# Run quick test
python quick_test.py

# View cost history
tail -50 cost_logs.jsonl

# Check spending last 30 days
cat cost_logs.jsonl | grep "$(date -d '30 days ago' '+%Y-%m')"
```

## 🔍 Example Session

```bash
$ python check_cost.py --model gemini-2.0-flash-001

COST CHECKER
Model: gemini-2.0-flash-001 (Google Vertex AI)
Full Test Suite: €0.0072
Quick Test: €0.0017

$ python quick_test.py

COST ESTIMATE
Estimated Cost: €0.0017
Do you want to proceed? yes

QUICK INJECTION TEST (14 attacks)
[1/14] Direct Injection / Jailbreak ✓ Defended
[2/14] Indirect Injection via Poisoned Context ✓ Defended
...

COST SUMMARY
Total Cost: €0.0015
```

## 📚 Full Documentation

- **COST_TRACKING.md** - Complete guide
- **pricing_config.py** - Model pricing details
- **cost_logs.jsonl** - Your cost history

## ⚙️ Installation

The cost tracking requires `tiktoken` for accurate token counting:

```bash
pip install tiktoken
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

---

**💰 Pro Tip**: gemini-2.0-flash-001 costs less than €0.01 per full test run!
