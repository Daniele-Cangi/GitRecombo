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
from copy import deepcopy
from datetime import datetime

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import io
    # Only re-wrap stdout/stderr when necessary. Guard against double-wrapping
    # which can close underlying buffers and raise "I/O operation on closed file".
    try:
        out_enc = getattr(sys.stdout, "encoding", None)
        err_enc = getattr(sys.stderr, "encoding", None)
        if not out_enc or out_enc.lower() != "utf-8":
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not err_enc or err_enc.lower() != "utf-8":
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        # If anything goes wrong (no buffer attribute, already wrapped, etc.), skip re-wrap
        pass

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import discover module
from discover import discover

DEFAULT_DISCOVERY_CONFIG = {
    "topics": [
        "networking",
        "drone",
        "mml",
    ],
    "goal": (
        "Discover cutting-edge repositories in infrastructure and developer tooling that enable "
        "robust, scalable, and maintainable software systems"
    ),
    "days": 90,
    "licenses": ["MIT", "Apache-2.0", "BSD-3-Clause", "MPL-2.0"],
    "max": 20,
    "explore_longtail": False,
    "max_stars": None,
    "min_health": 0.25,
    "probe_limit": 40,
    "w_novelty": 0.35,
    "w_health": 0.25,
    "w_relevance": 0.25,
    "w_diversity": 0.10,
    "use_embeddings": True,
    "embedding_model": "thenlper/gte-small",
    "require_ci": False,
    "require_tests": False,
    "authorsig": True,
    "embed_max_chars": 8000,
}


def load_discovery_config(config_file: str | None) -> dict:
    """Load discovery configuration merging GUI overrides with backend defaults."""
    cfg = deepcopy(DEFAULT_DISCOVERY_CONFIG)
    user_cfg = {}

    if config_file and os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            user_cfg = json.load(f) or {}

    for key, value in (user_cfg or {}).items():
        cfg[key] = value

    cfg["topics"] = [t for t in cfg.get("topics", []) if isinstance(t, str) and t.strip()]
    if isinstance(cfg.get("licenses"), str):
        cfg["licenses"] = [s.strip() for s in cfg["licenses"].split(",") if s.strip()]

    cfg["days"] = int(cfg.get("days", DEFAULT_DISCOVERY_CONFIG["days"]))
    cfg["max"] = int(cfg.get("max", DEFAULT_DISCOVERY_CONFIG["max"]))
    cfg["probe_limit"] = int(cfg.get("probe_limit", DEFAULT_DISCOVERY_CONFIG["probe_limit"]))
    cfg["min_health"] = float(cfg.get("min_health", DEFAULT_DISCOVERY_CONFIG["min_health"]))
    cfg["w_novelty"] = float(cfg.get("w_novelty", DEFAULT_DISCOVERY_CONFIG["w_novelty"]))
    cfg["w_health"] = float(cfg.get("w_health", DEFAULT_DISCOVERY_CONFIG["w_health"]))
    cfg["w_relevance"] = float(cfg.get("w_relevance", DEFAULT_DISCOVERY_CONFIG["w_relevance"]))
    cfg["w_diversity"] = float(cfg.get("w_diversity", DEFAULT_DISCOVERY_CONFIG["w_diversity"]))
    cfg["use_embeddings"] = bool(cfg.get("use_embeddings", DEFAULT_DISCOVERY_CONFIG["use_embeddings"]))
    cfg["explore_longtail"] = bool(cfg.get("explore_longtail", DEFAULT_DISCOVERY_CONFIG["explore_longtail"]))
    cfg["require_ci"] = bool(cfg.get("require_ci", DEFAULT_DISCOVERY_CONFIG["require_ci"]))
    cfg["require_tests"] = bool(cfg.get("require_tests", DEFAULT_DISCOVERY_CONFIG["require_tests"]))
    cfg["authorsig"] = bool(cfg.get("authorsig", DEFAULT_DISCOVERY_CONFIG["authorsig"]))
    cfg["embed_max_chars"] = int(cfg.get("embed_max_chars", DEFAULT_DISCOVERY_CONFIG["embed_max_chars"]))

    max_stars = cfg.get("max_stars")
    try:
        cfg["max_stars"] = int(max_stars) if max_stars is not None else None
    except (TypeError, ValueError):
        cfg["max_stars"] = None

    # Embedding model selection (only SBert/Hugging Face models supported)
    if not cfg["use_embeddings"]:
        cfg["embedding_model"] = None
    else:
        cfg["embedding_model"] = cfg.get("embedding_model") or DEFAULT_DISCOVERY_CONFIG["embedding_model"]

    cfg["goal"] = cfg.get("goal") or DEFAULT_DISCOVERY_CONFIG["goal"]

    return cfg

def ultra_autonomous_discovery(use_embeddings=True, config_file=None, no_cache: bool = False, exclude_processed: bool = False, skip_llm_insertion: bool = False):
    """
    Discovery ultra potenziato con discover.py full mode
    Supports loading config from JSON file for GUI integration
    
    Args:
        use_embeddings: Enable semantic embeddings for relevance scoring
        config_file: Path to JSON config file (for GUI integration)
        no_cache: Skip repository cache consultation
        exclude_processed: Skip repositories that have already been analyzed
        skip_llm_insertion: Skip LLM insertion in recombination (conservative mode)
    """
    print("\n🚀 GITRECOMBO ULTRA AUTONOMOUS MODE")
    print("="*80)
    print("Full discovery engine: novelty + health + author + embeddings + diversity\n")
    
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')  # FIX: Supporta entrambi i nomi
    if not token:
        print("❌ GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN not set")
        return None
    
    openai_key = os.getenv('OPENAI_API_KEY')  # Optional for goal refinement
    
    # Load config from file if provided (GUI mode)
    cfg = load_discovery_config(config_file)
    if config_file and os.path.exists(config_file):
        print(f"📂 Loading config from: {config_file}\n")

    topics = cfg["topics"]
    discovery_goal = cfg["goal"]
    days = cfg["days"]
    licenses = cfg["licenses"]
    max_repos = cfg["max"]
    explore_longtail = cfg["explore_longtail"]
    min_health = cfg["min_health"]
    probe_limit = cfg["probe_limit"]
    w_novelty = cfg["w_novelty"]
    w_health = cfg["w_health"]
    w_relevance = cfg["w_relevance"]
    w_diversity = cfg["w_diversity"]
    use_embeddings = cfg["use_embeddings"]
    embed_model = cfg["embedding_model"]
    max_stars = cfg["max_stars"]
    require_ci = cfg["require_ci"]
    require_tests = cfg["require_tests"]
    authorsig = cfg["authorsig"]
    embed_max_chars = cfg["embed_max_chars"]

    # ====================================================================
    # PHASE 1: DISCOVERY CON DISCOVER.PY FULL MODE
    # ====================================================================
    
    print("🔍 PHASE 1: AUTONOMOUS DISCOVERY")
    print("-" * 80)
    
    print(f"🎯 Discovery goal: {discovery_goal}")
    print(f"📚 Topics: {', '.join(topics)}")
    print(f"🔬 Embeddings: {'ENABLED' if use_embeddings else 'DISABLED'}")
    print()
    
    # Verify GitHub token early and print concise diagnostic (masked)
    def verify_github_token(tok: str) -> bool:
        """Verify token by calling /user and print masked login/status.

        Returns True if token appears valid (HTTP 200), False otherwise.
        """
        import requests
        try:
            h = {"Authorization": f"token {tok}", "User-Agent": "gitrecombo-cli"}
            r = requests.get("https://api.github.com/user", headers=h, timeout=10)
            if r.status_code == 200:
                try:
                    js = r.json()
                    login = js.get("login")
                    print(f"[AUTH] GitHub token valid for user: {login}")
                except Exception:
                    print("[AUTH] GitHub token appears valid (200 OK)")
                return True
            else:
                print(f"[AUTH] Token verification failed: {r.status_code} {r.reason}")
                return False
        except Exception as exc:
            print(f"[AUTH] Token verification error: {exc}")
            return False

    # Parametri discover.py (usa config se caricato, altrimenti defaults)
    discover_params = {
        "token": token,
        "topics": topics,
        "custom_queries": cfg.get("custom_queries"),  # Pass custom queries from config if provided
        "days": days,
        "licenses": licenses,
        "max": max_repos,
        "explore_longtail": explore_longtail,
        "max_stars": max_stars,
        "min_health": min_health,
        "require_ci": require_ci,
        "require_tests": require_tests,
        "authorsig": authorsig,
        "embed_provider": "sbert" if use_embeddings else None,
        "embed_model": embed_model,
        "embed_max_chars": embed_max_chars,
        "goal": discovery_goal,
        "w_novelty": w_novelty,
        "w_health": w_health,
        "w_relevance": w_relevance,
        "w_author": 0.05,     # Trust signal
        "w_diversity": w_diversity,
        "probe_limit": probe_limit,
        # Exclude already processed repos if requested (e.g., when skipping analyzed repos)
        "exclude_processed": exclude_processed,
        # use_cache is for readme/metadata cache: when False we bypass cache reads
        "use_cache": (not no_cache),
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
    # PHASE 2: GOAL REFINEMENT WITH GPT-5
    # ====================================================================
    
    print("\n\n[LLM] PHASE 2: DEEP ANALYSIS WITH GPT-5")
    print("-" * 80)
    
    refined_goal = discovery_goal
    repository_synergy = ""
    technical_architecture = ""
    expected_impact = ""
    innovation_analysis = ""
    
    if openai_key:
        try:
            from .llm import openai_recombine
            import tempfile
            
            print("[INFO] OpenAI key found, starting LLM analysis...")
            
            # Prepare context for LLM
            sources_context = json.dumps([
                {
                    "name": src['name'],
                    "url": src['url'],
                    "description": src.get('description', ''),
                    "concepts": src.get('concepts', [])[:5],
                    "gem_score": src.get('gem_score', 0)
                }
                for src in sources
            ], ensure_ascii=False, indent=2)
            
            # Determine LLM insertion instruction based on skip_llm_insertion flag
            if skip_llm_insertion:
                llm_insertion_instruction = """CRITICAL: Keep the architecture focused on the ACTUAL selected repositories.
Do NOT suggest adding AI/LLM components unless they are:
1) Directly mentioned in one of the selected repositories
2) Essential to solve a key problem identified in the goal
3) Directly relevant to the selected technologies

This is a conservative mode. Prioritize solutions that use the existing repos,
not solutions that would require adding new paradigms or technologies."""
            else:
                llm_insertion_instruction = """Think creatively about innovative ways to integrate components.
You can suggest new architectural patterns, novel combinations, and even
the addition of complementary technologies (including AI/LLM components)
if they significantly enhance the solution.

Balance innovation with practicality. Suggest bold combinations that
other architects might miss."""
            
            # Read base prompt template (use absolute path relative to this file)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(current_dir, 'prompts', 'goal_refinement_controlled.prompt.txt')
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            # Create refinement prompt with dynamic LLM insertion instruction + original topics
            topics_context = f"ORIGINAL TOPICS: {', '.join(topics)}\n\n"
            refinement_prompt = topics_context + prompt_template.format(
                DISCOVERY_GOAL=discovery_goal,
                SOURCES_CONTEXT=sources_context,
                LLM_INSERTION_INSTRUCTION=llm_insertion_instruction
            )
            
            # Write prompt to temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as tf:
                tf.write(refinement_prompt)
                prompt_file = tf.name
            
            try:
                # Call LLM
                result = openai_recombine(
                    discovery_goal,
                    [{"sources": sources, "blueprint": blueprint}],
                    prompt_file,
                    schema=None,
                    model="gpt-5",
                    max_tokens=8000,  # Increased for GPT-5 reasoning + output
                    json_mode=False
                )
                
                # Parse result
                if result:
                    try:
                        # Try to extract JSON from result
                        import re
                        json_match = re.search(r'\{.*\}', result, re.DOTALL)
                        if json_match:
                            analysis = json.loads(json_match.group())
                            refined_goal = analysis.get('refined_goal', discovery_goal)
                            repository_synergy = analysis.get('repository_synergy', '')
                            technical_architecture = analysis.get('technical_architecture', '')
                            expected_impact = analysis.get('expected_impact', '')
                            innovation_analysis = analysis.get('innovation_analysis', '')
                            
                            print(f"[OK] Deep analysis completed with GPT-5 ({len(result)} chars)")
                            print(f"     Refined goal: {refined_goal}")
                            print(f"     LLM Insertion Mode: {'CONSERVATIVE' if skip_llm_insertion else 'CREATIVE'}")
                            print(f"\n📊 COMPREHENSIVE ANALYSIS:")
                            print(f"\n🔄 Repository Synergy:\n{repository_synergy}\n")
                            print(f"🏗️ Technical Architecture:\n{technical_architecture}\n")
                            print(f"💡 Expected Impact:\n{expected_impact}\n")
                            print(f"⭐ Innovation Analysis:\n{innovation_analysis}\n")
                        else:
                            print(f"[WARN] Could not extract JSON from LLM response")
                            print(f"       Response: {result[:200]}...")
                            refined_goal = discovery_goal
                            repository_synergy = ''
                            technical_architecture = ''
                            expected_impact = ''
                            innovation_analysis = ''
                    except json.JSONDecodeError as e:
                        print(f"[WARN] JSON parse error: {e}")
                        print(f"       Raw result: {result[:300]}...")
                        refined_goal = discovery_goal
                        repository_synergy = ''
                        technical_architecture = ''
                        expected_impact = ''
                        innovation_analysis = ''

                else:
                    print("[WARN] LLM returned empty result")
                    
            finally:
                try:
                    os.remove(prompt_file)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"[WARN] Phase 2 LLM analysis failed: {e}")
            import traceback
            traceback.print_exc()
            refined_goal = discovery_goal
    else:
        print("[INFO] OPENAI_API_KEY not set - skipping LLM goal refinement")
    
    # ====================================================================
    # PHASE 3: ENRICHMENT - Fetch README snippets
    # ====================================================================
    
    print("\n\n📚 PHASE 3: ENRICHMENT (fetching READMEs)")
    print("-" * 80)
    
    from .discover import get_readme_text
    
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
        "repository_synergy": repository_synergy,
        "technical_architecture": technical_architecture,
        "expected_impact": expected_impact,
        "innovation_analysis": innovation_analysis,
        "sources": enriched_sources,
        "discovery_params": {
            k: v for k, v in discover_params.items() 
            if k not in ['token']  # Don't save token
        },
        "metrics": metrics,
        "blueprint": blueprint
    }
    
    # Create missions directory if it doesn't exist
    os.makedirs("missions", exist_ok=True)
    
    output_file = f"missions/ultra_autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mission, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("🎉 ULTRA AUTONOMOUS DISCOVERY COMPLETED")
    print("="*80)
    print(f"💾 Mission saved to: {output_file}")
    print(f"🎯 Goal: {refined_goal}")
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
    parser.add_argument('--config', type=str, default='config_lightweight.json',
                        help='Path to JSON config file (default: config_lightweight.json)')
    parser.add_argument('--no-cache', action='store_true',
                        help='Do not consult or mark processed repos; force fresh discovery')
    parser.add_argument('--clear-processed', action='store_true',
                        help='Clear the processed repos markers before running')
    parser.add_argument('--exclude-processed', action='store_true',
                        help='Skip repositories that have already been analyzed/processed')
    parser.add_argument('--skip-llm-insertion', action='store_true',
                        help='Skip LLM insertion in recombination analysis')
    parser.add_argument('--search-only', action='store_true',
                        help='Run only the discovery/search phase and exit (no LLM refinement)')
    args = parser.parse_args()

    use_embeddings = not args.no_embeddings
    no_cache = bool(args.no_cache)
    clear_processed = bool(args.clear_processed)
    exclude_processed = bool(args.exclude_processed)
    skip_llm_insertion = bool(args.skip_llm_insertion)

    # Auto-detect config changes and invalidate cache accordingly
    if not no_cache:
        try:
            import hashlib
            config_path = args.config
            
            if os.path.exists(config_path):
                # Calculate current config hash
                with open(config_path, 'rb') as f:
                    current_hash = hashlib.md5(f.read()).hexdigest()
                
                # Check against saved hash
                cache_hash_file = '.config_hash'
                previous_hash = None
                
                if os.path.exists(cache_hash_file):
                    with open(cache_hash_file, 'r') as f:
                        previous_hash = f.read().strip()
                
                # If config changed, auto-invalidate cache
                if previous_hash and previous_hash != current_hash:
                    print("🔄 Config file changed detected - invalidating cache automatically\n")
                    no_cache = True
                
                # Save current hash for next run
                with open(cache_hash_file, 'w') as f:
                    f.write(current_hash)
                    
        except Exception as e:
            print(f"⚠️ Config change detection failed: {e}")

    # If requested, clear processed markers (non-destructive to repo metadata)
    if clear_processed:
        try:
            from gitrecombo.repo_cache import RepoCache
            rc = RepoCache()
            deleted = rc.purge_processed_older_than(days=0)  # delete all processed markers
            print(f"📦 Cleared {deleted} processed markers from cache")
        except Exception as e:
            print(f"⚠️ Failed to clear processed markers: {e}")

    # If search-only requested, run discovery and exit before LLM stage
    if args.search_only:
        print("\n🔎 Running search-only mode (discovery)\n")
        mission = ultra_autonomous_discovery(use_embeddings=use_embeddings, config_file=args.config, no_cache=no_cache, exclude_processed=exclude_processed, skip_llm_insertion=skip_llm_insertion)
        # ultra_autonomous_discovery returns the mission dict; exit after reporting
        if mission:
            print("\n✅ Search-only discovery completed. Repos found:")
            for i, s in enumerate(mission.get('sources', []), 1):
                print(f"{i}. {s.get('name')} — {s.get('url')}")
            sys.exit(0)
        else:
            sys.exit(1)

    mission = ultra_autonomous_discovery(use_embeddings=use_embeddings, config_file=args.config, no_cache=no_cache, exclude_processed=exclude_processed, skip_llm_insertion=skip_llm_insertion)
    
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
