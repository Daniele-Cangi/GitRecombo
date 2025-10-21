# -*- coding: utf-8 -*-
"""
GitRecombo ULTRA AUTONOMOUS MODE
Discovery potenziato con discover.py full mode:
- Novelty score (alta velocity)
- Health score (CI/CD + tests + releases)
- Author reputation
- Concept extraction
- Embeddings (optional)
- Relevance score (semantic similarity con goal)
- Diversity bonus (repos complementari garantiti)
"""
import os
import sys
import json
from datetime import datetime

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import discover module
from discover import discover

def ultra_autonomous_discovery(use_embeddings=True, config_file=None):
    """
    Discovery ultra potenziato con discover.py full mode
    Supports loading config from JSON file for GUI integration
    """
    print("\n🚀 GITRECOMBO ULTRA AUTONOMOUS MODE")
    print("="*80)
    print("Full discovery engine: novelty + health + author + embeddings + diversity\n")
    
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')  # FIX: Supporta entrambi i nomi
    if not token:
        print("❌ GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN not set")
        return None
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not set")
        return None
    
    # Load config from file if provided (GUI mode)
    if config_file and os.path.exists(config_file):
        print(f"📂 Loading config from: {config_file}\n")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        topics = config.get("topics", [])
        discovery_goal = config.get("goal", "")
        days = config.get("days", 90)
        licenses = config.get("licenses", "MIT,Apache-2.0,BSD-3-Clause,MPL-2.0")
        max_repos = config.get("max", 20)
        explore_longtail = config.get("explore_longtail", False)
        min_health = config.get("min_health", 0.25)
        probe_limit = config.get("probe_limit", 40)
        w_novelty = config.get("w_novelty", 0.35)
        w_health = config.get("w_health", 0.25)
        w_relevance = config.get("w_relevance", 0.25)
        w_diversity = config.get("w_diversity", 0.10)
        use_embeddings = config.get("use_embeddings", True)
        embedding_model_choice = config.get("embedding_model", None)
    else:
        # Default hardcoded config (CLI mode)
        topics = [
            "embedding",
            "blockchain",
            "data transfer",
            "machine learning",
            "P2P",
            "gateway",
        ]
        discovery_goal = (
            "Discover cutting-edge repositories in AI/ML infrastructure that enable "
            "building local-first, privacy-preserving, real-time intelligent systems"
        )
        days = 90
        licenses = "MIT,Apache-2.0,BSD-3-Clause,MPL-2.0"
        max_repos = 20
        explore_longtail = False
        min_health = 0.25
        probe_limit = 40
        w_novelty = 0.35
        w_health = 0.25
        w_relevance = 0.25
        w_diversity = 0.10
        embedding_model_choice = None
    
    # Parse embedding model choice from GUI
    if embedding_model_choice:
        if "gte-large" in embedding_model_choice:
            embed_provider = "sbert"
            embed_model = "Alibaba-NLP/gte-large-en-v1.5"
        elif "OpenAI" in embedding_model_choice:
            embed_provider = "openai"
            embed_model = "text-embedding-3-small"
        elif "bge-large" in embedding_model_choice:
            embed_provider = "sbert"
            embed_model = "BAAI/bge-large-en-v1.5"
        else:
            embed_provider = "sbert"
            embed_model = "Alibaba-NLP/gte-large-en-v1.5"
    else:
        # Default: use gte-large-en-v1.5 (best local model)
        embed_provider = "sbert" if use_embeddings else None
        embed_model = "Alibaba-NLP/gte-large-en-v1.5"
    
    # ====================================================================
    # PHASE 1: DISCOVERY CON DISCOVER.PY FULL MODE
    # ====================================================================
    
    print("🔍 PHASE 1: AUTONOMOUS DISCOVERY")
    print("-" * 80)
    
    print(f"🎯 Discovery goal: {discovery_goal}")
    print(f"📚 Topics: {', '.join(topics)}")
    print(f"🔬 Embeddings: {'ENABLED' if use_embeddings else 'DISABLED'}")
    print()
    
    # Parametri discover.py (usa config se caricato, altrimenti defaults)
    discover_params = {
        "token": token,
        "topics": topics,
        "days": days,
        "licenses": licenses,
        "max": max_repos,
        "explore_longtail": explore_longtail,
        "max_stars": None,  # Nessun cap
        "min_health": min_health,
        "require_ci": False,  # Non obbligatorio ma privilegiato
        "require_tests": False,
        "authorsig": True,  # Author reputation
        "embed_provider": embed_provider,  # 🔄 SWITCHED to local gte-large-en-v1.5 by default
        "embed_model": embed_model,  # 🏆 BINGO: Score 65.4, 1.3GB, 8K tokens
        "embed_max_chars": 8000,
        "goal": discovery_goal,
        "w_novelty": w_novelty,
        "w_health": w_health,
        "w_relevance": w_relevance,
        "w_author": 0.05,     # Trust signal
        "w_diversity": w_diversity,
        "probe_limit": probe_limit,
    }
    
    print("⚙️ Discovery parameters:")
    print(f"   Days window: {discover_params['days']}")
    print(f"   Max stars: {discover_params['max_stars']}")
    print(f"   Min health: {discover_params['min_health']}")
    print(f"   Explore longtail: {discover_params['explore_longtail']}")
    print(f"   Weights: novelty={discover_params['w_novelty']}, "
          f"health={discover_params['w_health']}, "
          f"relevance={discover_params['w_relevance']}, "
          f"diversity={discover_params['w_diversity']}")
    print()
    
    print("🔄 Running discover.py full mode...\n")
    
    try:
        blueprint = discover(discover_params)
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    sources = blueprint.get('sources', [])
    
    print("\n✅ DISCOVERY COMPLETED!")
    print("="*80)
    print(f"📊 Metrics:")
    metrics = blueprint.get('metrics', {})
    
    # DEBUG: Check if sources is empty
    if not sources:
        print("\n⚠️ WARNING: No sources returned from discover()!")
        print(f"   Candidates found: {metrics.get('candidates', 0)}")
        print(f"   Probed: {metrics.get('probed', 0)}")
        print(f"   Selected: {metrics.get('selected', 0)}")
        print("\n💡 Possible issues:")
        print("   1. min_health=0.25 too restrictive")
        print("   2. probe_limit=40 not enough")
        print("   3. Topics too broad - all repos filtered out")
        print("   4. GitHub rate limit hit")
        print("\n🔧 Try adjusting ultra_autonomous.py discovery params:")
        print("   - min_health: 0.25 → 0.15")
        print("   - probe_limit: 40 → 60")
        print("   - max: 20 → 30")
        return None
    print(f"   Candidates: {metrics.get('candidates', 0)}")
    print(f"   Probed (deep analysis): {metrics.get('probed', 0)}")
    print(f"   Selected: {metrics.get('selected', 0)}")
    print()
    
    print("🏆 SELECTED REPOS (scored & ranked):")
    print("-" * 80)
    for i, src in enumerate(sources, 1):
        print(f"\n{i}. {src['name']} ({src.get('role', 'N/A')})")
        print(f"   URL: {src['url']}")
        print(f"   License: {src['license']}")
        print(f"   Scores:")
        print(f"     • Novelty:   {src['novelty_score']:.4f}")
        print(f"     • Health:    {src['health_score']:.4f}")
        print(f"     • Relevance: {src['relevance']:.4f}")
        print(f"     • Author:    {src['author_rep']:.4f}")
        print(f"     • GEM SCORE: {src['gem_score']:.4f} ⭐")
        print(f"   Concepts: {', '.join(src['concepts'][:5])}")
    
    # ====================================================================
    # PHASE 2: GOAL REFINEMENT CON GPT-5
    # ====================================================================
    
    print("\n\n🧠 PHASE 2: GOAL REFINEMENT WITH GPT-5")
    print("-" * 80)
    
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)
    
    # Prepara summary per GPT-5
    repos_summary = []
    for src in sources:
        repos_summary.append({
            "name": src['name'],
            "role": src.get('role', 'module'),
            "concepts": src['concepts'][:8],
            "novelty": src['novelty_score'],
            "health": src['health_score'],
            "relevance": src['relevance']
        })
    
    refinement_prompt = f"""You discovered these {len(repos_summary)} cutting-edge repositories:

{json.dumps(repos_summary, indent=2)}

Your mission: Analyze this COMBINATION and explain its breakthrough potential.

Return JSON with:
{{
  "goal": "BRIEF statement (1-2 sentences, ~50 words). What to build with this combo.",
  "why_these_repos": "EXTENSIVE technical analysis (400-600 words). Focus on:
    - What NOVEL capabilities emerge from combining THESE specific repos?
    - HOW do they integrate? (specific APIs, patterns, data flows)
    - WHY is THIS combination better than alternatives?
    - What was IMPOSSIBLE before but is now POSSIBLE?
    - Cite concrete features from each repo
    - Explain technical synergies in detail",
  "expected_impact": "EXTENSIVE breakthrough analysis (400-600 words). Focus on:
    - What NON-OBVIOUS innovations does this combo enable?
    - What competitive advantages emerge from this recombination?
    - What problems can ONLY be solved with this exact combination?
    - Quantified outcomes with specific metrics
    - Real-world use cases unlocked by this integration"
}}

CRITICAL: Spend 90% of tokens analyzing THE RECOMBINATION ITSELF (why_these_repos + expected_impact). The goal should be minimal - just 1-2 sentences.
"""
    
    print("⏳ Refining goal with CHATGPT-5...\n")
    
    completion = client.chat.completions.create(
        model='chatgpt-5',
        messages=[
            {"role": "system", "content": "You are an expert in AI/ML infrastructure and innovation strategy."},
            {"role": "user", "content": refinement_prompt}
        ],
        max_completion_tokens=2000,  # Goal refinement: up to 2K tokens
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    refinement = json.loads(completion.choices[0].message.content)
    refined_goal = refinement['goal']
    
    print("✅ GOAL REFINED!")
    print("="*80)
    print(f"🎯 Refined Goal:")
    print(f"   {refined_goal}")
    print()
    print(f"💡 Why These Repos:")
    print(f"   {refinement['why_these_repos']}")
    print()
    print(f"🚀 Expected Impact:")
    print(f"   {refinement['expected_impact']}")
    
    # ====================================================================
    # PHASE 3: ENRICHMENT - Fetch README snippets
    # ====================================================================
    
    print("\n\n📚 PHASE 3: ENRICHMENT (fetching READMEs)")
    print("-" * 80)
    
    from discover import get_readme_text
    
    enriched_sources = []
    for src in sources:
        owner, repo = src['name'].split('/', 1)
        
        print(f"📖 Fetching README: {src['name']}...")
        
        try:
            readme = get_readme_text(owner, repo, token, max_chars=8000)
            readme_snippet = readme[:2000] if readme else src.get('description', '')
        except Exception as e:
            print(f"   ⚠️ Failed to fetch README: {e}")
            readme_snippet = src.get('description', '')
        
        enriched_sources.append({
            "name": src['name'],
            "url": src['url'],
            "description": src.get('description', ''),
            "language": src.get('role', '').split()[0] if src.get('role') else 'Unknown',
            "license": src['license'],
            "readme_snippet": readme_snippet,
            "scores": {
                "novelty": src['novelty_score'],
                "health": src['health_score'],
                "relevance": src['relevance'],
                "author_rep": src['author_rep'],
                "gem_score": src['gem_score']
            },
            "concepts": src['concepts']
        })
    
    print("\n✅ Enrichment completed!")
    
    # ====================================================================
    # SAVE MISSION
    # ====================================================================
    
    mission = {
        "timestamp": datetime.now().isoformat(),
        "mode": "ultra_autonomous",
        "discovery_method": "discover.py_full_mode",
        "embeddings_used": use_embeddings,
        "refined_goal": refined_goal,
        "goal_refinement": refinement,
        "sources": enriched_sources,
        "discovery_params": {
            k: v for k, v in discover_params.items() 
            if k not in ['token']  # Don't save token
        },
        "metrics": metrics,
        "blueprint": blueprint
    }
    
    output_file = f"ultra_autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mission, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("🎉 ULTRA AUTONOMOUS DISCOVERY COMPLETED")
    print("="*80)
    print(f"💾 Mission saved to: {output_file}")
    print(f"🎯 Goal: {refined_goal[:100]}...")
    print(f"📚 Sources: {len(enriched_sources)}")
    
    if enriched_sources:
        avg_gem = sum(s['scores']['gem_score'] for s in enriched_sources) / len(enriched_sources)
        print(f"⭐ Avg GEM score: {avg_gem:.4f}")
    else:
        print("⚠️ WARNING: No repos passed filters! Try:")
        print("   - Lower min_health (currently 0.25)")
        print("   - Increase probe_limit (currently 40)")
        print("   - Check topics are not too niche")
    
    return mission

def main():
    """
    Esegue discovery ultra potenziato
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='GitRecombo Ultra Autonomous Discovery')
    parser.add_argument('--no-embeddings', action='store_true', 
                        help='Disable embeddings (faster but less precise)')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to JSON config file (for GUI integration)')
    args = parser.parse_args()
    
    use_embeddings = not args.no_embeddings
    
    mission = ultra_autonomous_discovery(use_embeddings=use_embeddings, config_file=args.config)
    
    if mission:
        print("\n✅ SUCCESS! Next steps:")
        print("   1. Review discovered repos and refined goal")
        print("   2. Run recombination:")
        print("      python ultra_recombine.py")
        sys.exit(0)  # 🔥 FIX: Explicit success exit code
    else:
        print("\n❌ Discovery failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
