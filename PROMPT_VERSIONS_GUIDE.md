# Prompt Version Configuration Guide

## Overview

The system now supports **dynamic prompt version selection**, allowing you to test different security levels without editing code. This is useful for:
- Testing prompt injection resistance at different security levels
- Comparing defensive strategies
- Finding the right balance between security and usability
- Research and demonstration purposes

## Available Prompt Versions

### 1. **Strict** (Default - Maximum Security)
- **Key**: `strict`
- **Description**: Comprehensive security rules with explicit instructions
- **Features**:
  - 8 explicit security rules
  - Anti-prompt injection instructions
  - Role confusion prevention
  - Authority claim rejection
- **Use Case**: Production environments, maximum protection
- **Expected Resistance**: Highest - should block most sophisticated attacks

### 2. **Moderate** (Standard Protection)
- **Key**: `moderate`
- **Description**: Basic security rules without explicit anti-injection instructions
- **Features**:
  - Simple "do not share" instruction
  - Polite decline guidance
  - Focus on regular recipe info
- **Use Case**: Testing if basic instructions are sufficient
- **Expected Resistance**: Medium - may be vulnerable to sophisticated attacks

### 3. **Relaxed** (Minimal Protection)
- **Key**: `relaxed`
- **Description**: Brief mention of secret ingredients without strong enforcement
- **Features**:
  - Single note about not sharing secrets
  - No explicit enforcement language
  - Minimal guidance
- **Use Case**: Testing baseline vulnerabilities
- **Expected Resistance**: Low - vulnerable to many attack types

### 4. **Minimal** (Very Weak)
- **Key**: `minimal`
- **Description**: Almost no security instructions, just basic functionality
- **Features**:
  - No mention of secrets in prompt
  - Pure functionality focus
  - No security guidance
- **Use Case**: Testing if model has inherent protections
- **Expected Resistance**: Very Low - vulnerable to simple attacks

### 5. **None** (No Protection)
- **Key**: `none`
- **Description**: No security instructions at all - baseline test
- **Features**:
  - Zero security instructions
  - Basic assistant definition only
  - No secret awareness
- **Use Case**: Control group for testing
- **Expected Resistance**: None - should leak easily

## How to Use

### In Streamlit App

1. Launch the app:
   ```bash
   streamlit run app.py
   ```

2. In the sidebar, find the "🔒 Security Level" section

3. Select a prompt version from the dropdown:
   - Strict (Maximum Security)
   - Moderate (Standard Protection)
   - Relaxed (Minimal Protection)
   - Minimal (Very Weak)
   - None (No Protection)

4. The app will automatically recreate the LLM provider with the new prompt

5. Start chatting and test the defenses!

### In Automated Tests

Run tests with different prompt versions:

```bash
# Test with strict prompt (default)
python automated_injection_tests.py --yes

# Test with moderate prompt
python automated_injection_tests.py --prompt-version moderate --yes

# Test with relaxed prompt
python automated_injection_tests.py --prompt-version relaxed --yes

# Test with minimal prompt
python automated_injection_tests.py --prompt-version minimal --yes

# Test with no protection
python automated_injection_tests.py --prompt-version none --yes
```

### Quick Test with Different Prompts

```bash
# Quick test with moderate security
python quick_test.py --prompt-version moderate --yes

# Quick test with no protection
python quick_test.py --prompt-version none --yes
```

## Comparison Testing

Compare how different prompt versions perform:

```bash
# Test all versions and save reports
for version in strict moderate relaxed minimal none; do
  echo "Testing with $version prompt..."
  python automated_injection_tests.py \
    --prompt-version $version \
    --output "report_${version}.json" \
    --yes
  sleep 5
done

# Compare results
echo "=== RESULTS COMPARISON ==="
for version in strict moderate relaxed minimal none; do
  echo -n "$version: "
  grep -o '"successful_leaks": [0-9]*' "report_${version}.json" | cut -d' ' -f2
done
```

## Environment Configuration

Set a default prompt version in your `.env` file:

```bash
# .env
PROMPT_VERSION=strict  # Options: strict, moderate, relaxed, minimal, none
```

This will be used as the default unless overridden by command-line flags or UI selection.

## Expected Results by Version

Based on testing, here's what you might expect:

| Version | Direct Injection | Social Engineering | Obfuscation | Role Play | Overall |
|---------|-----------------|-------------------|-------------|-----------|---------|
| Strict | ✅ Blocked | ✅ Blocked | ✅ Blocked | ✅ Blocked | 🟢 Excellent |
| Moderate | ✅ Blocked | ⚠️ Some Success | ⚠️ Some Success | ⚠️ Some Success | 🟡 Good |
| Relaxed | ⚠️ Some Success | ❌ Often Succeeds | ❌ Often Succeeds | ❌ Often Succeeds | 🟠 Fair |
| Minimal | ❌ Often Succeeds | ❌ Usually Succeeds | ❌ Usually Succeeds | ❌ Usually Succeeds | 🔴 Poor |
| None | ❌ Succeeds | ❌ Succeeds | ❌ Succeeds | ❌ Succeeds | ⛔ No Defense |

*Note: Actual results may vary by model and attack sophistication*

## Research Use Cases

### 1. Security Research
Compare different defensive strategies:
```bash
python automated_injection_tests.py --prompt-version strict --output strict.json --yes
python automated_injection_tests.py --prompt-version moderate --output moderate.json --yes
# Analyze which specific rules provide the most protection
```

### 2. Red Team Testing
Start with weakest and work up:
```bash
# Find what works on weak defenses
python quick_test.py --prompt-version none

# Test if it works on stronger defenses
python quick_test.py --prompt-version moderate

# Refine attack for strict version
python quick_test.py --prompt-version strict
```

### 3. Cost Optimization
Test if you really need strict prompts:
```bash
# If moderate blocks everything, you might not need strict
python automated_injection_tests.py --prompt-version moderate --yes
```

### 4. Prompt Engineering
Use the prompt_versions.py file as a template:
1. Read the existing prompts
2. Create custom variations
3. Add them to PROMPT_VERSIONS dict
4. Test your custom prompts

## Tips

1. **Start Strict**: Begin with strict prompts and relax only if needed
2. **Document Results**: Save reports for each version for comparison
3. **Consider Context**: Production apps should use strict; demos might use moderate
4. **Model Matters**: Different models respond differently to the same prompts
5. **Cost vs Security**: Strict prompts may use more tokens due to length

## Troubleshooting

### "Unknown prompt version" error
- Check spelling: use `strict`, `moderate`, `relaxed`, `minimal`, or `none`
- Case sensitive: use lowercase

### Prompt not changing in app
- The app recreates the provider when you change versions
- If issues persist, click "Play Again" to fully reset

### Test results identical across versions
- Some models may have built-in safeguards
- Try with a different model
- Verify provider is being recreated (check console output)

## Advanced: Custom Prompt Versions

Edit `prompt_versions.py` to add your own:

```python
PROMPT_VERSIONS["custom"] = {
    "name": "Custom (My Test)",
    "description": "My custom prompt for testing",
    "prompt": """Your custom system prompt here..."""
}
```

Then use it:
```bash
python automated_injection_tests.py --prompt-version custom --yes
```

---

**Remember**: The goal is to find the right balance between security and usability. Too strict can make the assistant less helpful; too loose creates vulnerabilities.
