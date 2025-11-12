# LOVABLE: Istruzioni per Costruire la GUI di GitRecombo

## COSA STAI COSTRUENDO

Una web UI per **GitRecombo** - un tool che trova repository GitHub **nascoste e di qualità** usando algoritmi di scoring AI.

**Analogia semplice**: GitRecombo è come un metal detector per gemme nascoste su GitHub. Invece di guardare solo le stelle (che tutti vedono), analizza qualità, freschezza, rilevanza semantica e reputazione per trovare progetti eccezionali con <100 stelle.

---

## ARCHITETTURA BACKEND (GIÀ PRONTA)

Il backend Python **esiste già** in questa repo. **NON devi riscriverlo**, solo chiamarlo.

### File Chiave (LEGGI QUESTI):
- `ultra_autonomous.py` → Entry point principale
- `discover.py` → Motore di discovery con GitHub API
- `embeddings.py` → Embedding locali (Alibaba/Hugging Face - GRATIS)
- `llm.py` → Generazione blueprint con OpenAI GPT
- `PROJECT_SPEC.json` → Specifica completa del progetto (LEGGI QUESTO!)

### Come Funziona il Backend:

```bash
# Input: JSON config
python ultra_autonomous.py --config my_config.json

# Output: JSON con risultati
ultra_autonomous_20251023_143000.json
```

**Config di esempio**:
```json
{
  "topics": ["vector-database", "semantic-search"],
  "goal": "Build a local-first semantic search system",
  "days": 90,
  "max": 20,
  "explore_longtail": true,
  "max_stars": 100,
  "use_embeddings": true,
  "embed_provider": "sbert",
  "embedding_model": "Alibaba-NLP/gte-large-en-v1.5",
  "min_health": 0.25,
  "probe_limit": 40,
  "w_novelty": 0.35,
  "w_health": 0.25,
  "w_relevance": 0.25,
  "w_author": 0.05,
  "w_diversity": 0.10
}
```

**Output di esempio** (modalità completa):
```json
{
  "timestamp": "2025-10-23T14:30:05.123456",
  "mode": "ultra_autonomous",
  "discovery_method": "discover.py_full_mode",
  "embeddings_used": true,
  "refined_goal": "Build a secure semantic search platform with vector embeddings...",
  "goal_refinement": {
    "goal": "Build a secure semantic search platform...",
    "why_these_repos": "Extensive analysis of why these specific repos work together...",
    "expected_impact": "Quantified outcomes and breakthrough innovations..."
  },
  "sources": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "description": "Repo description",
      "language": "Python",
      "license": "MIT",
      "readme_snippet": "First 2000 chars of README...",
      "scores": {
        "novelty": 0.82,
        "health": 0.75,
        "relevance": 0.92,
        "author_rep": 0.45,
        "gem_score": 0.87
      },
      "concepts": ["vector", "embeddings", "search", "index"]
    }
  ],
  "discovery_params": {...},
  "metrics": {
    "topics": ["vector-database"],
    "days": 90,
    "candidates": 150,
    "probed": 40,
    "selected": 6
  },
  "blueprint": {
    "architecture_ascii": "Visual diagram...",
    "why_it_works": ["Reason 1", "Reason 2"]
  }
}
```

**Output di esempio** (modalità `--search-only`, più veloce):
```json
{
  "timestamp": "2025-10-23T14:25:10.654321",
  "mode": "ultra_autonomous",
  "discovery_method": "discover.py_full_mode",
  "embeddings_used": false,
  "sources": [
    {
      "name": "kysely-org/kysely-typeorm",
      "url": "https://github.com/kysely-org/kysely-typeorm",
      "description": "",
      "language": "TypeScript",
      "license": "MIT",
      "scores": {
        "novelty": 0.3267,
        "health": 1.0,
        "relevance": 0.0,
        "author_rep": 0.6831,
        "gem_score": 0.4985
      },
      "concepts": ["type", "column", "varchar", "string"]
    }
  ],
  "metrics": {
    "candidates": 45,
    "probed": 15,
    "selected": 6
  }
}
```

**IMPORTANTE**: Il flag `--search-only` salta le fasi GPT-4 (goal refinement e blueprint generation), rendendo il processo molto più veloce e economico. Usa questa modalità per la GUI!

---

## TUO COMPITO: COSTRUIRE LA GUI

### Stack Consigliato:
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend API**: Python FastAPI (wrapper per ultra_autonomous.py)
- **Deployment**: Vercel (frontend) + backend su Railway/Render

---

## PAGINE DA CREARE

### 1. **Home/Discovery Page** (Pagina Principale)

**Layout**:
```
┌─────────────────────────────────────────┐
│ GitRecombo 🔍                           │
│ Discover Hidden Gem Repositories        │
├─────────────────────────────────────────┤
│                                         │
│ [Topics Input]                          │
│  🏷️ vector-database  🏷️ embeddings     │
│  + Add topic                            │
│                                         │
│ [Goal Description]                      │
│  📝 Build a local-first semantic...     │
│                                         │
│ ▼ Advanced Settings                     │
│   Days: [90] ⚙️                         │
│   Max Stars: [100] (longtail mode)      │
│   Weights: Novelty [0.35] Health [0.25] │
│                                         │
│ [🚀 Discover Repositories]              │
│                                         │
└─────────────────────────────────────────┘
```

**Componenti**:
- `TopicInput`: Input con chips/tags (rimuovibili)
- `GoalTextarea`: Textarea per descrizione obiettivo
- `AdvancedPanel`: Collapsible panel con sliders per weights
- `DiscoverButton`: Trigger API call

### 2. **Results Page** (Risultati)

**Layout**:
```
┌─────────────────────────────────────────┐
│ Results: 6 Hidden Gems Found ✨         │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🏆 owner/amazing-repo               │ │
│ │ Gem Score: ████████░░ 0.87          │ │
│ │                                     │ │
│ │ Novelty   ████████░░ 0.82           │ │
│ │ Health    ███████░░░ 0.75           │ │
│ │ Relevance █████████░ 0.92           │ │
│ │                                     │ │
│ │ 🏷️ vector embeddings search         │ │
│ │ 📄 MIT License | ⭐ 47 stars        │ │
│ │ [View on GitHub] [Add to Blueprint] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [More repos...]                         │
│                                         │
│ ▼ View Blueprint                        │
│                                         │
└─────────────────────────────────────────┘
```

**Componenti**:
- `RepoCard`: Card per ogni repository con score bars
- `ScoreBar`: Progress bar colorata per ogni metrica
- `ConceptTags`: Tags con concetti estratti
- `BlueprintSection`: Mostra architettura ASCII e comandi

### 3. **History Page** (Cronologia)

Lista delle discovery precedenti con filtri.

---

## API ENDPOINTS DA CREARE (FastAPI)

### Backend Python (Nuovo file: `api/server.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
from datetime import datetime
from pathlib import Path

app = FastAPI()

class DiscoveryConfig(BaseModel):
    topics: list[str]
    goal: str
    days: int = 90
    max: int = 20
    explore_longtail: bool = True
    max_stars: int | None = 100
    use_embeddings: bool = True
    embed_provider: str = "sbert"
    w_novelty: float = 0.35
    w_health: float = 0.25
    w_relevance: float = 0.25
    w_author: float = 0.05
    w_diversity: float = 0.10

@app.post("/api/discover")
async def run_discovery(config: DiscoveryConfig):
    """Esegue discovery e ritorna risultati"""
    
    # 1. Salva config temporaneo
    config_file = f"temp_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(config_file, 'w') as f:
        json.dump(config.dict(), f)
    
    try:
        # 2. Esegui ultra_autonomous.py
        result = subprocess.run(
            ["python", "ultra_autonomous.py", "--config", config_file, "--search-only"],
            capture_output=True,
            text=True,
            timeout=300  # 5 min timeout
        )
        
        if result.returncode != 0:
            raise HTTPException(500, detail=f"Discovery failed: {result.stderr}")
        
        # 3. Trova file output più recente
        output_files = list(Path(".").glob("ultra_autonomous_*.json"))
        if not output_files:
            raise HTTPException(500, detail="No output file generated")
        
        latest_output = max(output_files, key=lambda p: p.stat().st_mtime)
        
        # 4. Leggi e ritorna risultati
        with open(latest_output) as f:
            results = json.load(f)
        
        return {
            "success": True,
            "results": results,
            "output_file": str(latest_output)
        }
    
    finally:
        # Cleanup temp config
        Path(config_file).unlink(missing_ok=True)

@app.get("/api/missions")
async def list_missions():
    """Lista tutte le discovery precedenti"""
    missions = []
    for file in Path(".").glob("ultra_autonomous_*.json"):
        with open(file) as f:
            data = json.load(f)
            missions.append({
                "id": file.stem,
                "timestamp": file.stem.split('_', 2)[2],
                "title": data.get("title"),
                "sources_count": len(data.get("sources", []))
            })
    return sorted(missions, key=lambda x: x["timestamp"], reverse=True)

@app.get("/api/health")
async def health_check():
    """Verifica che API keys siano configurate"""
    import os
    return {
        "github_token": bool(os.getenv("GITHUB_TOKEN")),
        "openai_key": bool(os.getenv("OPENAI_API_KEY"))
    }
```

---

## FRONTEND COMPONENTS (React + TypeScript)

### Component: `DiscoveryForm.tsx`

```typescript
import { useState } from 'react';
import { TagInput } from './TagInput';
import { AdvancedSettings } from './AdvancedSettings';

interface DiscoveryConfig {
  topics: string[];
  goal: string;
  days: number;
  max: number;
  explore_longtail: boolean;
  max_stars: number | null;
  weights: {
    novelty: number;
    health: number;
    relevance: number;
    author: number;
    diversity: number;
  };
}

export function DiscoveryForm({ onSubmit }: { onSubmit: (config: DiscoveryConfig) => void }) {
  const [topics, setTopics] = useState<string[]>([]);
  const [goal, setGoal] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [config, setConfig] = useState<DiscoveryConfig>({
    topics: [],
    goal: '',
    days: 90,
    max: 20,
    explore_longtail: true,
    max_stars: 100,
    weights: {
      novelty: 0.35,
      health: 0.25,
      relevance: 0.25,
      author: 0.05,
      diversity: 0.10
    }
  });
  
  const handleSubmit = () => {
    if (topics.length === 0) {
      alert('Add at least one topic');
      return;
    }
    if (!goal.trim()) {
      alert('Describe your goal');
      return;
    }
    
    onSubmit({ ...config, topics, goal });
  };
  
  return (
    <div className="space-y-6 max-w-2xl mx-auto p-6">
      <div>
        <label className="block text-sm font-medium mb-2">Topics</label>
        <TagInput 
          tags={topics} 
          onChange={setTopics}
          placeholder="e.g. vector-database, embeddings"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-2">Goal</label>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          className="w-full border rounded-lg p-3 h-24"
          placeholder="Describe what you want to build..."
        />
      </div>
      
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-blue-600 text-sm"
      >
        {showAdvanced ? '▼' : '▶'} Advanced Settings
      </button>
      
      {showAdvanced && (
        <AdvancedSettings config={config} onChange={setConfig} />
      )}
      
      <button
        onClick={handleSubmit}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
      >
        🚀 Discover Repositories
      </button>
    </div>
  );
}
```

### Component: `RepoCard.tsx`

```typescript
interface Repo {
  name: string;
  url: string;
  license: string;
  gem_score: number;
  novelty_score: number;
  health_score: number;
  relevance: number;
  concepts: string[];
}

export function RepoCard({ repo }: { repo: Repo }) {
  return (
    <div className="border rounded-lg p-6 shadow-sm hover:shadow-md transition">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{repo.name}</h3>
          <div className="flex gap-2 mt-2 text-sm text-gray-600">
            <span>📄 {repo.license}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {(repo.gem_score * 100).toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">Gem Score</div>
        </div>
      </div>
      
      <div className="space-y-2 mb-4">
        <ScoreBar label="Novelty" value={repo.novelty_score} color="purple" />
        <ScoreBar label="Health" value={repo.health_score} color="green" />
        <ScoreBar label="Relevance" value={repo.relevance} color="blue" />
      </div>
      
      <div className="flex flex-wrap gap-2 mb-4">
        {repo.concepts.map(c => (
          <span key={c} className="px-2 py-1 bg-gray-100 rounded text-xs">
            🏷️ {c}
          </span>
        ))}
      </div>
      
      <a
        href={repo.url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block bg-gray-900 text-white px-4 py-2 rounded hover:bg-gray-800"
      >
        View on GitHub →
      </a>
    </div>
  );
}

function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
  const colors = {
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500'
  };
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="font-medium">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${colors[color]} h-2 rounded-full transition-all`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  );
}
```

---

## FLUSSO UTENTE COMPLETO

1. **User arriva sulla home**
   - Vede form con campi Topics e Goal
   - Può cliccare esempi pre-compilati ("Try: Vector DB Discovery")

2. **User compila form**
   - Aggiunge topics come tags (es: "vector-database", "embeddings")
   - Scrive goal in textarea
   - Opzionale: apre Advanced Settings per regolare weights

3. **User clicca "Discover"**
   - Frontend chiama `POST /api/discover` con config
   - Mostra loading spinner con messaggio: "Searching GitHub... This may take 2-3 minutes"
   - Backend esegue `ultra_autonomous.py`

4. **Backend processa**
   - Cerca repos su GitHub
   - Calcola scores (novelty, health, relevance, etc.)
   - Ritorna top 6 hidden gems

5. **Frontend mostra risultati**
   - Grid di RepoCard con scores visualizzati
   - Sezione Blueprint collapsible con ASCII architecture
   - Bottone "Export as JSON" per scaricare risultati

6. **User esplora risultati**
   - Clicca "View on GitHub" per aprire repo
   - Vede perché ogni repo è stato scelto (scores breakdown)
   - Copia comandi dal blueprint per iniziare integrazione

---

## VARIABILI AMBIENTE (.env)

```bash
# Backend
GITHUB_TOKEN=github_pat_11BT3DXPA0...
OPENAI_API_KEY=sk-proj-...

# Frontend (optional)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## COMANDI DEPLOYMENT

### Backend (Railway/Render):
```bash
pip install -r requirements.txt
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### Frontend (Vercel):
```bash
npm run build
npm start
```

---

## CHIAVI DEL SUCCESSO

✅ **NON riscrivere discover.py** - è complesso e funziona già  
✅ **Usa subprocess per chiamare ultra_autonomous.py** - è il modo più semplice  
✅ **Focus sulla UX**: form chiaro, risultati visualizzati bene  
✅ **Spiega gli score**: user deve capire PERCHÉ un repo è stato scelto  
✅ **Loading states**: discovery richiede 1-3 minuti, mostra progresso  

---

## DOMANDE FREQUENTI

**Q: Come testo il backend senza GUI?**  
A: Usa il CLI direttamente:
```bash
python ultra_autonomous.py --config quick_test_config.json --search-only
```

**Q: Posso usare embeddings di OpenAI invece di quelli locali?**  
A: Sì, nel form Advanced Settings aggiungi toggle per `embed_provider` (sbert vs openai)

**Q: Il discovery è troppo lento, come velocizzarlo?**  
A: Riduci `probe_limit` da 40 a 20 nel config, oppure usa `--no-cache` solo quando necessario

**Q: Come funziona il longtail mode?**  
A: `explore_longtail=true` + `max_stars=100` cerca solo repo con <100 stelle (hidden gems)

---

## INIZIA DA QUI

1. Leggi `PROJECT_SPEC.json` per capire tutto il sistema
2. Testa il backend CLI: `python ultra_autonomous.py --config quick_test_config.json`
3. Crea FastAPI wrapper in `api/server.py`
4. Costruisci frontend con i componenti React sopra
5. Testa end-to-end con esempi reali

**Ricorda**: Il backend funziona già perfettamente. Il tuo lavoro è renderlo accessibile via GUI! 🚀
