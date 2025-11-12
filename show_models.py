import os
os.environ['OPENAI_API_KEY'] = open('gitrecombo/.env').read().split('OPENAI_API_KEY=')[1].strip()

from openai import OpenAI
client = OpenAI()
models = client.models.list()

print('\n🔍 MODELLI GPT-5 DISPONIBILI:')
gpt5 = sorted([m.id for m in models if 'gpt-5' in m.id.lower()])
for m in gpt5:
    print(f'  ✓ {m}')

print('\n🔍 MODELLI GPT-4O DISPONIBILI:')
gpt4o = sorted([m.id for m in models if 'gpt-4o' in m.id.lower()])
for m in gpt4o[:10]:
    print(f'  ✓ {m}')

print('\n🔍 MODELLI O1 E O3 DISPONIBILI:')
o_models = sorted([m.id for m in models if m.id.startswith('o') and m.id[1].isdigit()])
for m in o_models:
    print(f'  ✓ {m}')
