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

def openai_recombine(goal: str, sources: List[Dict[str, Any]], prompt_path: str, schema: Dict[str, Any],
                     model: str = "chatgpt-5") -> Dict[str, Any]:
    from openai import OpenAI
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI()
    with open(prompt_path, "r", encoding="utf-8") as f:
        sys_prompt = f.read()
    # Compose user message with inputs
    user_msg = {
        "goal": goal,
        "sources": sources,
    }
    # Ask for JSON only with DETAILED analysis (up to 16K tokens)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": json.dumps(user_msg)}
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=16000,  # CHATGPT-5-MINI: maximum detailed blueprints
        temperature=0.7    # Creative but consistent
    )
    txt = completion.choices[0].message.content
    data = json.loads(txt)
    ensure_valid(data, schema)
    return data
