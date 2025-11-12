
"""
ultra_recombine.py — cleaned and consolidated

Purpose:
  Two‑step recombination pipeline driven by a compact JSON blueprint and an
  expansion pass using the LATERAL‑RECOMB protocol prompt.

Notes:
  - Keeps prior behavior (prompt path, model fallback, optional HTML output).
  - Adds env overrides for model selection.
  - Handles dry‑run cleanly when OPENAI_API_KEY is missing.
  - Removes duplicated code and stray appended strings from corrupted file.
"""

import os
import sys
import json
import glob
import time
from datetime import datetime
from pathlib import Path
import tempfile

from dotenv import load_dotenv

# External wrapper expected in the repository
from gitrecombo.llm import openai_recombine

# Configure output encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# -----------------------------------------------------------------------------
# Env loading
# -----------------------------------------------------------------------------
def _load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path), override=True)
    else:
        load_dotenv()

_load_env()


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def find_latest_mission() -> str | None:
    """Return newest ultra_autonomous_*.json in missions/ folder, or None."""
    missions = glob.glob('missions/ultra_autonomous_*.json')
    if not missions:
        print("[ERR] No ultra_autonomous mission found!")
        print("[INFO] Run: python -m gitrecombo.ultra_autonomous first")
        return None
    return max(missions, key=os.path.getmtime)


# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
def ultra_recombination(mission_file: str | None = None):
    """Two‑step recombination: compact JSON → expanded narrative.


    Returns a dict with compact result + metadata; also prints expansion text.
    """
    # Resolve mission file
    if not mission_file:
        mission_file = find_latest_mission()
        if not mission_file:
            return None

    print(f"[LOAD] Loading mission: {mission_file}\n")
    with open(mission_file, 'r', encoding='utf-8') as f:
        mission = json.load(f)

    goal = mission.get('refined_goal', '')
    sources = mission.get('sources', [])

    print(f"[GOAL] Goal: {goal}")
    print(f"[SRC] Sources: {len(sources)}\n")

    # Prepare sources for LLM context
    gpt_sources = []
    for src in sources:
        gpt_sources.append({
            'name': src.get('name'),
            'url': src.get('url'),
            'description': src.get('description', ''),
            'language': src.get('language', 'Unknown'),
            'license': src.get('license', ''),
            'readme_snippet': src.get('readme_snippet', '')[:2000],
            'role': f"module ({src.get('language', 'NA')})",
            'concepts': (src.get('concepts', []) or [])[:8],
            'novelty': src.get('scores', {}).get('novelty', 0),
            'relevance': src.get('scores', {}).get('relevance', 0),
            'health': src.get('scores', {}).get('health', 0),
        })

    openai_key = os.getenv('OPENAI_API_KEY')

    # Model selection (env overrides allowed)
    primary_model = os.getenv('ULTRA_MODEL_ALIAS', 'gpt-5')
    fallback_models = [m.strip() for m in os.getenv('ULTRA_MODEL_FALLBACKS', '').split(',') if m.strip()]

    # Step 1: compact JSON via prompt file
    def try_model_for_json(model_name: str):
        return openai_recombine(
            goal,
            gpt_sources,
            'gitrecombo/prompts/futures_recombiner.prompt.txt',
            schema=None,
            model=model_name,
            max_tokens=10000,
            json_mode=True,
        )

    if not openai_key:
        # Dry‑run to help debugging upstream inputs
        payload = {
            'step': 'compact_json',
            'prompt_path': 'gitrecombo/prompts/futures_recombiner.prompt.txt',
            'model_alias': primary_model,
            'fallbacks': fallback_models,
            'user_msg': {'goal': goal, 'sources': gpt_sources},
        }
        dr_file = f"dry_run_payload_step1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(dr_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"[OK] OPENAI_API_KEY not set: payload saved to {dr_file}. Set the key to call the API.")
        return None

    tried = []
    model_used = None
    compact_result = None
    start = time.time()

    # Try primary then fallbacks
    try:
        tried.append(primary_model)
        compact_result = try_model_for_json(primary_model)
        model_used = primary_model
    except Exception as e:
        print(f"[WARN] Primary {primary_model} failed: {e}. Trying fallbacks...")
        for m in fallback_models:
            try:
                tried.append(m)
                compact_result = try_model_for_json(m)
                model_used = m
                print(f"[OK] Compact JSON generated with {m}")
                break
            except Exception as e2:
                print(f"   [ERR] {m} failed: {e2}")

    if compact_result is None:
        print(f"[ERR] Failed to generate compact JSON with models: {tried}")
        return None

    # Step 2: expansion with LATERAL‑RECOMB protocol
    blueprint_json = compact_result

    expansion_prompt = (
        "# LATERAL-RECOMB PROTOCOL v1.0\n"
        "Mental mode: You're a brilliant engineer who sees hidden potential in existing systems. Find non-obvious connections between components. Be creative.\n"
        "Input: You'll receive 2-5 GitHub repositories.\n"
        "Output: Produce 2 non-obvious designs that recombine repos via unconventional bridges (creative repurposing of artifacts) and optimize with analytics. That it is of the highest engineering level.\n"
        "minimum output length: 7000 tokens."
        "Create an \"illicit bridge\" - connect components in ways their creators never intended."
        "Solve a real problem that's difficult to solve otherwise."
        "Don't suggest obvious combinations everyone would think of."
        "Design the technical recombination with concrete details, but leaving freedom on the form."

    )

    # Assemble a temp prompt file with sources + blueprint to maximize context
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', suffix='.prompt.txt') as tf:
        tf.write(expansion_prompt)
        tf.write('\n=== MARKET & TECHNICAL SOURCES ===\n')
        for src in gpt_sources:
            tf.write(json.dumps(src, ensure_ascii=False) + '\n')
        tf.write('\n=== COMPACT STRATEGIC BLUEPRINT ===\n')
        tf.write(json.dumps(blueprint_json, ensure_ascii=False))
        temp_prompt = tf.name

    expansion_text = None
    try:
        expansion_text = openai_recombine(
            goal,
            [{'blueprint': blueprint_json, 'sources': gpt_sources}],
            temp_prompt,
            schema=None,
            model=model_used,
            max_tokens=10000,
            json_mode=False,
        )
    except Exception as e:
        print(f"[WARN] Expansion call failed with {model_used}: {e}")
        for m in fallback_models:
            try:
                expansion_text = openai_recombine(
                    goal,
                    [{'blueprint': blueprint_json}],
                    temp_prompt,
                    schema=None,
                    model=m,
                    max_tokens=10000,
                    json_mode=False,
                )
                model_used = m
                print(f"[OK] Expansion succeeded with fallback {m}")
                break
            except Exception as e2:
                print(f"   [ERR] fallback {m} failed: {e2}")

    finally:
        try:
            os.remove(temp_prompt)
        except Exception:
            pass

    elapsed = time.time() - start

    if expansion_text:
        print("\n--- FULL EXPANDED NARRATIVE START ---\n")
        print(expansion_text)
        print("\n--- FULL EXPANDED NARRATIVE END ---\n")
    else:
        print("[WARN] No expansion text returned.")

    # Save structured output for later reuse
    result = compact_result or {}
    output = {
        'timestamp': datetime.now().isoformat(),
        'mission_file': mission_file,
        'goal': goal,
        'sources': gpt_sources,
        'result': result,
        'metrics': {
            'generation_time_s': elapsed,
            'tokens_used': None,
            'concepts_generated': len(result.get('concepts', [])),
            'model_used': model_used,
        },
    }

    # Create missions directory if it doesn't exist
    os.makedirs("missions", exist_ok=True)
    
    json_out = f"missions/ultra_recombination_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[SAVE] Output saved to: {json_out}")

    # Optional HTML blueprint if templates available
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('onepage_ultra.html.j2')
        html_content = template.render({
            'project': result.get('project', {}),
            'sources': gpt_sources,
            'concepts': result.get('concepts', []),
            'mission_file': mission_file,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {
                'discovery_method': mission.get('mode', 'ultra'),
                'embeddings_used': True,
                'generation_time': f"{elapsed:.1f}s",
                'tokens': None,
                'model_used': model_used,
            },
        })
        html_out = f"ultra_blueprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_out, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[OK] HTML blueprint saved to: {html_out}")
    except Exception as e:
        print(f"[WARN] HTML generation skipped/failed (non-critical): {e}")

    print("\n" + "=" * 80)
    print("[OK] ALL DONE! Ultra recombination complete.")
    print("=" * 80)
    return output


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description='GitRecombo Ultra Recombination')
    parser.add_argument('--mission', type=str, help='Mission file to use (default: latest)')
    args = parser.parse_args()

    out = ultra_recombination(mission_file=args.mission)
    if not out:
        print("\n[ERR] Recombination failed. Check errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
