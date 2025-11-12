from __future__ import annotations
import os, json
from typing import Dict, Any, List
from jsonschema import validate, Draft202012Validator

# Carica variabili d'ambiente da file .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass  # dotenv non installato, usa variabili d'ambiente normali

def load_schema(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_valid(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    Draft202012Validator(schema).validate(data)

def openai_recombine(goal: str,
                     sources: List[Dict[str, Any]],
                     prompt_path: str,
                     schema: Dict[str, Any] | None = None,
                     model: str = "chatgpt-4o-latest",
                     max_tokens: int = 2048,
                     temperature: float = 0.7,
                     json_mode: bool = False) -> Dict[str, Any] | str:
    """Call provider chat completion.

    - If json_mode=True will attempt to parse and (if schema provided) validate JSON and return a dict.
    - Otherwise returns raw text (string).
    - For GPT-5 and reasoning models, uses max_completion_tokens instead of max_tokens.
    """
    from openai import OpenAI
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI()

    with open(prompt_path, "r", encoding="utf-8") as f:
        sys_prompt = f.read()

    user_msg = {
        "goal": goal,
        "sources": sources,
    }

    # Build API params - standard approach
    api_params = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": json.dumps(user_msg)}
        ],
    }
    
    # GPT-5 and reasoning models have special parameter restrictions
    if "gpt-5" in model.lower() or "reasoning" in model.lower():
        # GPT-5: temperature must be 1.0 (default), max_completion_tokens instead of max_tokens
        api_params["max_completion_tokens"] = max_tokens  # Use the passed max_tokens value
        # Do NOT set temperature for GPT-5
    else:
        # Standard models: support temperature and max_tokens
        api_params["temperature"] = temperature
        api_params["max_tokens"] = max_tokens
    
    completion = client.chat.completions.create(**api_params)

    # provider-dependent extraction of text
    try:
        txt = completion.choices[0].message.content
    except Exception as e:
        try:
            txt = completion.choices[0].text
        except Exception as e2:
            txt = ""

    if not json_mode:
        return txt

    # json_mode == True: try to extract a leading JSON object if present
    def _extract_leading_json(text: str):
        if not text:
            return None
        start = text.find('{')
        if start == -1:
            return None
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if ch == '"' and not escape:
                in_string = not in_string
            if in_string and ch == '\\' and not escape:
                escape = True
                continue
            escape = False
            if not in_string:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            return None
        return None

    parsed = None
    # first try direct parse (often the model returns pure JSON)
    try:
        parsed = json.loads(txt)
    except Exception:
        parsed = _extract_leading_json(txt)

    if parsed is None:
        # Return raw text under error to allow caller to inspect and fallback
        raise ValueError("Failed to parse JSON from model output; raw output returned instead.", txt)

    # Validate schema if provided
    if schema is not None:
        ensure_valid(parsed, schema)

    return parsed
