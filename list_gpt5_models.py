#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Carica .env
env_path = Path(__file__).parent / "gitrecombo" / ".env"
load_dotenv(env_path)

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY non trovato in .env")
    exit(1)

client = OpenAI(api_key=api_key)
models = client.models.list()

print("\n🔍 TUTTI I MODELLI GPT-5 DISPONIBILI:\n")
gpt5_models = [m.id for m in models if "gpt-5" in m.id.lower()]
for m in sorted(gpt5_models):
    print(f"  ✓ {m}")

print("\n🔍 TUTTI I MODELLI GPT-4 DISPONIBILI:\n")
gpt4_models = [m.id for m in models if "gpt-4" in m.id.lower() and "gpt-5" not in m.id.lower()]
for m in sorted(gpt4_models):
    print(f"  ✓ {m}")
