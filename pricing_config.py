"""
LLM Pricing Configuration

Pricing per 1M tokens (as of January 2025)
Prices in EUR (converted from USD at ~0.93 EUR/USD)
"""

# Pricing per 1 million tokens (input / output) in EUR
MODEL_PRICING = {
    # Google Gemini (via Vertex AI and API)
    "gemini-2.0-flash-exp": {
        "input": 0.0,  # Free during preview
        "output": 0.0,
        "provider": "Google",
        "notes": "Free during experimental preview"
    },
    "gemini-2.0-flash-001": {
        "input": 0.07,  # $0.075/1M tokens
        "output": 0.28,  # $0.30/1M tokens
        "provider": "Google Vertex AI"
    },
    "gemini-1.5-flash": {
        "input": 0.07,
        "output": 0.28,
        "provider": "Google"
    },
    "gemini-1.5-flash-001": {
        "input": 0.07,
        "output": 0.28,
        "provider": "Google"
    },
    "gemini-1.5-flash-002": {
        "input": 0.07,
        "output": 0.28,
        "provider": "Google"
    },
    "gemini-1.5-pro": {
        "input": 1.16,  # $1.25/1M tokens
        "output": 4.65,  # $5.00/1M tokens
        "provider": "Google"
    },
    "gemini-1.5-pro-001": {
        "input": 1.16,
        "output": 4.65,
        "provider": "Google"
    },
    "gemini-1.5-pro-002": {
        "input": 1.16,
        "output": 4.65,
        "provider": "Google"
    },

    # OpenAI
    "gpt-4o": {
        "input": 2.33,  # $2.50/1M tokens
        "output": 9.30,  # $10.00/1M tokens
        "provider": "OpenAI"
    },
    "gpt-4o-mini": {
        "input": 0.14,  # $0.15/1M tokens
        "output": 0.56,  # $0.60/1M tokens
        "provider": "OpenAI"
    },
    "gpt-4-turbo": {
        "input": 9.30,  # $10.00/1M tokens
        "output": 27.90,  # $30.00/1M tokens
        "provider": "OpenAI"
    },
    "gpt-4": {
        "input": 27.90,  # $30.00/1M tokens
        "output": 55.80,  # $60.00/1M tokens
        "provider": "OpenAI"
    },
    "gpt-3.5-turbo": {
        "input": 0.47,  # $0.50/1M tokens
        "output": 1.40,  # $1.50/1M tokens
        "provider": "OpenAI"
    },

    # Anthropic Claude
    "claude-3-5-sonnet-20241022": {
        "input": 2.79,  # $3.00/1M tokens
        "output": 13.95,  # $15.00/1M tokens
        "provider": "Anthropic"
    },
    "claude-3-5-sonnet-20240620": {
        "input": 2.79,
        "output": 13.95,
        "provider": "Anthropic"
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.93,  # $1.00/1M tokens
        "output": 4.65,  # $5.00/1M tokens
        "provider": "Anthropic"
    },
    "claude-3-opus-20240229": {
        "input": 13.95,  # $15.00/1M tokens
        "output": 69.75,  # $75.00/1M tokens
        "provider": "Anthropic"
    },
    "claude-3-sonnet-20240229": {
        "input": 2.79,
        "output": 13.95,
        "provider": "Anthropic"
    },
    "claude-3-haiku-20240307": {
        "input": 0.23,  # $0.25/1M tokens
        "output": 1.16,  # $1.25/1M tokens
        "provider": "Anthropic"
    },
}

# Default pricing if model not found (use most expensive as safety margin)
DEFAULT_PRICING = {
    "input": 30.0,
    "output": 80.0,
    "provider": "Unknown",
    "notes": "Using conservative estimates - actual model not in pricing database"
}


def get_model_pricing(model_name: str) -> dict:
    """
    Get pricing for a model.

    Args:
        model_name: Name of the model

    Returns:
        Dict with 'input' and 'output' prices per 1M tokens in EUR
    """
    # Exact match
    if model_name in MODEL_PRICING:
        return MODEL_PRICING[model_name]

    # Try partial match (for models with version suffixes)
    model_lower = model_name.lower()
    for key in MODEL_PRICING:
        if key.lower() in model_lower or model_lower in key.lower():
            return MODEL_PRICING[key]

    # Not found - return default
    return DEFAULT_PRICING


def estimate_cost(input_tokens: int, output_tokens: int, model_name: str) -> dict:
    """
    Estimate cost for a given number of tokens.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_name: Name of the model

    Returns:
        Dict with cost breakdown in EUR
    """
    pricing = get_model_pricing(model_name)

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_eur": round(input_cost, 4),
        "output_cost_eur": round(output_cost, 4),
        "total_cost_eur": round(total_cost, 4),
        "model": model_name,
        "provider": pricing.get("provider", "Unknown"),
        "pricing_per_1m_tokens": {
            "input": pricing["input"],
            "output": pricing["output"]
        }
    }


def format_cost_summary(cost_data: dict) -> str:
    """Format cost data as readable string."""
    return f"""
Cost Estimate:
  Model: {cost_data['model']} ({cost_data['provider']})
  Tokens: {cost_data['input_tokens']:,} input + {cost_data['output_tokens']:,} output = {cost_data['total_tokens']:,} total
  Cost: €{cost_data['input_cost_eur']:.4f} + €{cost_data['output_cost_eur']:.4f} = €{cost_data['total_cost_eur']:.4f}

  Pricing: €{cost_data['pricing_per_1m_tokens']['input']:.2f}/€{cost_data['pricing_per_1m_tokens']['output']:.2f} per 1M tokens (input/output)
"""
