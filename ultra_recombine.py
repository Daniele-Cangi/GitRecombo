"""
GitRecombo ULTRA RECOMBINATION
Usa mission da ultra_autonomous.py per generare futures kit con GPT-5
"""
import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

def find_latest_mission():
    """
    Trova l'ultima mission ultra_autonomous
    """
    missions = glob.glob('ultra_autonomous_*.json')
    if not missions:
        print("❌ No ultra_autonomous mission found!")
        print("💡 Run: python ultra_autonomous.py first")
        return None
    
    latest = max(missions, key=os.path.getmtime)
    return latest

def ultra_recombination(mission_file=None):
    """
    Ricombinazione ultra con GPT-5 usando mission scoperta
    """
    print("\n🤖 GITRECOMBO ULTRA RECOMBINATION")
    print("="*80)
    
    # Load mission
    if not mission_file:
        mission_file = find_latest_mission()
        if not mission_file:
            return None
    
    print(f"📂 Loading mission: {mission_file}\n")
    
    with open(mission_file, 'r', encoding='utf-8') as f:
        mission = json.load(f)
    
    goal = mission['refined_goal']
    sources = mission['sources']
    
    print(f"🎯 Goal: {goal}")
    print(f"📚 Sources: {len(sources)}")
    print()
    
    # Display sources with scores
    print("🏆 SOURCES (by GEM score):")
    print("-" * 80)
    for i, src in enumerate(sources, 1):
        scores = src.get('scores', {})
        print(f"{i}. {src['name']} - GEM: {scores.get('gem_score', 0):.4f} ⭐")
        print(f"   Novelty: {scores.get('novelty', 0):.3f} | "
              f"Health: {scores.get('health', 0):.3f} | "
              f"Relevance: {scores.get('relevance', 0):.3f}")
    print()
    
    # ====================================================================
    # RECOMBINATION CON GPT-5
    # ====================================================================
    
    print("🔄 PHASE: RECOMBINATION WITH GPT-5")
    print("-" * 80)
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not set")
        return None
    
    # Load prompt
    prompt_path = 'prompts/futures_recombiner.prompt.txt'
    if not os.path.exists(prompt_path):
        print(f"❌ Prompt not found: {prompt_path}")
        return None
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        sys_prompt = f.read()
    
    # Prepara sources per GPT-5 (formato ottimizzato)
    gpt_sources = []
    for src in sources:
        gpt_sources.append({
            "name": src['name'],
            "url": src['url'],
            "description": src.get('description', ''),
            "language": src.get('language', 'Unknown'),
            "license": src['license'],
            "readme_snippet": src.get('readme_snippet', '')[:2000],  # Max 2K chars
            "role": f"module ({src.get('language', 'NA')})",
            "concepts": src.get('concepts', [])[:8],
            "novelty": src['scores']['novelty'],
            "relevance": src['scores']['relevance'],
            "health": src['scores']['health']
        })
    
    user_msg = {
        "goal": goal,
        "sources": gpt_sources
    }
    
    print(f"📤 Sending to GPT-5:")
    print(f"   Goal length: {len(goal)} chars")
    print(f"   Sources: {len(gpt_sources)}")
    print(f"   Total README text: {sum(len(s.get('readme_snippet', '')) for s in gpt_sources)} chars")
    print()
    print("⏳ This may take 30-60 seconds...\n")
    
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)
    
    import time
    start = time.time()
    
    try:
        completion = client.chat.completions.create(
            model='gpt-5',
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": json.dumps(user_msg)}
            ],
            response_format={"type": "json_object"}
        )
        
        elapsed = time.time() - start
        
        result = json.loads(completion.choices[0].message.content)
        
        print(f"✅ GPT-5 completed in {elapsed:.1f}s!")
        print(f"📊 Tokens used: {completion.usage.total_tokens}")
        print(f"   Prompt: {completion.usage.prompt_tokens}")
        print(f"   Completion: {completion.usage.completion_tokens}")
        
    except Exception as e:
        print(f"❌ GPT-5 call failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ====================================================================
    # DISPLAY RESULTS
    # ====================================================================
    
    print("\n" + "="*80)
    print("🎉 ULTRA RECOMBINATION COMPLETED")
    print("="*80)
    
    project = result.get('project', {})
    concepts = result.get('concepts', [])
    
    print(f"\n🚀 PROJECT: {project.get('name', 'Unnamed')}")
    print(f"   Tagline: {project.get('tagline', 'N/A')}")
    print(f"   Vision: {project.get('vision', 'N/A')[:200]}...")
    print()
    
    print(f"💡 CONCEPTS: {len(concepts)}")
    for i, concept in enumerate(concepts, 1):
        print(f"\n   {i}. {concept.get('solution', 'Unnamed')[:100]}...")
        print(f"      Problem: {concept.get('problem', 'N/A')[:150]}...")
        
        why_works = concept.get('why_it_works', [])
        if why_works:
            print(f"      Why it works: {why_works[0][:100]}...")
        
        kpis = concept.get('kpis_90d', [])
        if kpis:
            print(f"      KPI: {kpis[0][:80]}...")
    
    # ====================================================================
    # SAVE OUTPUT
    # ====================================================================
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "mission_file": mission_file,
        "goal": goal,
        "sources": gpt_sources,
        "result": result,
        "metrics": {
            "generation_time_s": elapsed,
            "tokens_used": completion.usage.total_tokens,
            "concepts_generated": len(concepts)
        }
    }
    
    output_file = f"ultra_recombination_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Output saved to: {output_file}")
    
    # ====================================================================
    # GENERATE HTML BLUEPRINT (optional)
    # ====================================================================
    
    try:
        print("\n📄 Generating HTML blueprint...")
        
        # Usa template ultra migliorato
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('onepage_ultra.html.j2')
        
        # Prepara dati per template ultra completo
        blueprint_data = {
            "project": project,
            "sources": gpt_sources,
            "concepts": result.get('concepts', []),
            "mission_file": mission_file,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "metrics": {
                "discovery_method": mission.get('mode', 'ultra'),
                "embeddings_used": True,
                "generation_time": f"{elapsed:.1f}s",
                "tokens": completion.usage.total_tokens
            }
        }
        
        html_content = template.render(blueprint_data)
        
        html_file = f"ultra_blueprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML blueprint saved to: {html_file}")
        
    except Exception as e:
        print(f"⚠️ HTML generation failed (non-critical): {e}")
    
    print("\n" + "="*80)
    print("✅ ALL DONE! Your ultra-powered innovation is ready.")
    print("="*80)
    
    return output

def main():
    """
    Esegue recombination ultra
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='GitRecombo Ultra Recombination')
    parser.add_argument('--mission', type=str, help='Mission file to use (default: latest)')
    args = parser.parse_args()
    
    output = ultra_recombination(mission_file=args.mission)
    
    if not output:
        print("\n❌ Recombination failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
