"""
Check available models in OpenAI account
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path('gitrecombo/.env')
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ OPENAI_API_KEY non trovata in .env o variabili d'ambiente")
    exit(1)

from openai import OpenAI
client = OpenAI(api_key=api_key)

print("📋 MODELLI DISPONIBILI NEL TUO ACCOUNT:\n")
print("-" * 100)
print(f"{'ID':<50} {'Owner':<20}")
print("-" * 100)

models = client.models.list()
count = 0
for m in models:
    print(f"{m.id:<50} {m.owned_by:<20}")
    count += 1

print("-" * 100)
print(f"\n✅ Totale modelli: {count}\n")

# Filtrare modelli GPT comuni
print("\n🎯 MODELLI GPT CONSIGLIATI (filtrati):\n")
gpt_models = [m for m in models if any(x in m.id.lower() for x in ['gpt-4', 'gpt-5', 'o1', 'o3', 'chatgpt'])]
for m in gpt_models:
    print(f"  • {m.id}")

print("\n✨ Usa uno di questi modelli nella recombinazione (senza alias personalizzato).")
