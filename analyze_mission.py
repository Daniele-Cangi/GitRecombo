"""
Analizza l'ultima missione per vedere cosa è stato trovato
"""
import json
from pathlib import Path

missions_dir = Path("missions")
json_files = sorted(missions_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

if not json_files:
    print("Nessuna missione trovata!")
    exit()

latest = json_files[0]
print(f"📂 Ultima missione: {latest.name}\n")

with open(latest, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("GOAL DELLA RICERCA:")
print("=" * 80)
print(data.get('goal', 'N/A'))

print("\n" + "=" * 80)
print("REPOSITORY TROVATI:")
print("=" * 80)

sources = data.get('sources', [])
print(f"\nTotale: {len(sources)} repository\n")

for i, repo in enumerate(sources, 1):
    name = repo.get('name', 'Unknown')
    desc = repo.get('description', 'No description')
    url = repo.get('url', '')
    lang = repo.get('language', 'N/A')
    
    # Scores
    scores = repo.get('scores', {})
    gem = scores.get('gem_score', 0)
    novelty = scores.get('novelty', 0)
    health = scores.get('health', 0)
    relevance = scores.get('relevance', 0)
    
    print(f"{i}. {name}")
    print(f"   URL: {url}")
    print(f"   Desc: {desc[:100]}...")
    print(f"   Lang: {lang}")
    print(f"   Scores: GEM={gem:.3f} | Novelty={novelty:.3f} | Health={health:.3f} | Relevance={relevance:.3f}")
    
    # Mostra i topics GitHub del repository
    repo_topics = repo.get('topics', [])
    if repo_topics:
        print(f"   GitHub Topics: {', '.join(repo_topics)}")
    else:
        print(f"   GitHub Topics: (nessuno)")
    
    print()

print("=" * 80)
print("ANALISI:")
print("=" * 80)

# Conta quanti repository hanno i topics che abbiamo cercato
search_topics = ['hacking', 'data', 'nvidia']
print(f"\nTopics cercati: {search_topics}\n")

for search_topic in search_topics:
    count = 0
    matching_repos = []
    
    for repo in sources:
        repo_topics = [t.lower() for t in repo.get('topics', [])]
        name_lower = repo.get('name', '').lower()
        desc_lower = (repo.get('description') or '').lower()
        
        # Controlla se il topic è nei GitHub Topics o nel nome/descrizione
        in_github_topics = search_topic.lower() in repo_topics
        in_name = search_topic.lower() in name_lower
        in_desc = search_topic.lower() in desc_lower
        
        if in_github_topics or in_name or in_desc:
            count += 1
            matching_repos.append({
                'name': repo.get('name'),
                'in_topics': in_github_topics,
                'in_name': in_name,
                'in_desc': in_desc
            })
    
    print(f"Topic '{search_topic}': trovato in {count}/{len(sources)} repository")
    if matching_repos:
        for m in matching_repos[:3]:  # Mostra primi 3
            where = []
            if m['in_topics']: where.append('GitHub Topics')
            if m['in_name']: where.append('Nome')
            if m['in_desc']: where.append('Descrizione')
            print(f"  - {m['name']}: {', '.join(where)}")
    print()
