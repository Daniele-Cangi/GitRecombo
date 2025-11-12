# GitRecombo v0.6 (Full Package)
**AI-Powered GitHub Repository Discovery + LLM Recombination** - All-in-one toolkit for discovering, analyzing, and recombining GitHub repositories using advanced scoring, embeddings, and LLM intelligence.

---

## 🚀 Features

### Core Modules
- **Discover Engine** (Deterministic): Multi-dimensional scoring (Novelty, Health, Author Reputation, Relevance, Diversity) with GitHub search integration
- **Embeddings** (Optional): Semantic similarity using OpenAI or local SBERT models for relevance and diversity scoring
- **Ultra Autonomous Mode**: 3-phase workflow (Discover → LLM Refinement → Recombination) with GPT-5 integration
- **LLM Recombination** (Optional): Generate structured *Futures Kit* blueprints from discovered repositories
- **FastAPI Server** (Optional): RESTful endpoints `/discover`, `/recombine`, `/run`
- **Desktop GUI** (Optional): Modern CustomTkinter interface with dark/light themes, real-time logs, and advanced controls

### Key Capabilities
- **Advanced Filtering**: License filtering, CI/CD requirements, health thresholds, star limits
- **Long-tail Exploration**: Discover hidden gems with low stars but high quality
- **Semantic Relevance**: Goal-based relevance scoring using embeddings
- **Diversity Bonus**: Avoid conceptual duplicates with diversity weighting
- **LLM Goal Refinement**: GPT-5 refines discovery goals based on selected repositories
- **Topic Alignment Constraint**: Ensures LLM stays aligned with original topics (prevents AI/ML drift)
- **Customizable Prompts**: Control LLM behavior with custom prompt templates in `prompts/`

---

## 📦 Installation

### Basic (CLI Discover Only)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Optional Extensions
```bash
# API Server
pip install -r requirements-api.txt

# LLM & Embeddings (OpenAI or local SBERT)
pip install -r requirements-llm.txt

# Desktop GUI (CustomTkinter)
pip install -r requirements-gui.txt
```

---

## 🎯 Quick Start

### Ultra Autonomous Mode (Recommended)
Complete 3-phase workflow with LLM refinement:

```bash
export GITHUB_TOKEN="ghp_..."
export OPENAI_API_KEY="sk-..."  # Optional for LLM refinement

# Using config file
python -m gitrecombo.ultra_autonomous --config config_lightweight.json

# Or launch GUI
python run_gui.py
```

**Output**: Mission files in `missions/ultra_autonomous_YYYYMMDD_HHMMSS.json` with:
- Discovered repositories with GEM scores
- LLM-refined goal analysis
- Repository synergy explanation
- Technical architecture blueprint
- Innovation analysis

---

## 🔧 CLI Usage

### Discover Repositories
```bash
export GITHUB_TOKEN="ghp_..."

# Basic discovery
python -m gitrecombo.cli discover \
  --topics "red team,penetration,security" \
  --days 180 \
  --licenses "MIT,Apache-2.0" \
  --max-stars 100 \
  --min-health 0.25 \
  --json out/blueprint.json

# With semantic embeddings
python -m gitrecombo.cli discover \
  --topics "vector-db,embeddings" \
  --embed-provider sbert \
  --embed-model thenlper/gte-small \
  --goal "Build scalable vector database for RAG" \
  --w-relevance 0.25 \
  --w-diversity 0.15 \
  --json out/blueprint.json
```

### LLM Recombination
```bash
export OPENAI_API_KEY="sk-..."

python -m gitrecombo.cli recombine \
  --goal "Edge-native RAG for IoT devices" \
  --sources blueprint.json \
  --out futures_kit.json
```

### End-to-End Pipeline
```bash
python -m gitrecombo.cli run \
  --topics "streaming,kafka,edge" \
  --goal "Real-time analytics for edge computing" \
  --json out/blueprint.json \
  --out out/futures_kit.json
```

---

## 🖥️ Desktop GUI

Launch the modern desktop interface:

```bash
python run_gui.py
# or
python -m gitrecombo.gui_app
```

### GUI Features

#### 🎨 Modern Interface
- **Dark/Light Themes**: Toggle between themes with smooth transitions
- **Responsive Layout**: Two-column design with scrollable frames
- **Ultra-fast Scrolling**: 6x acceleration on all scrollable areas
- **Purple Accents**: Modern color scheme with visual hierarchy

#### ⚙️ Configuration Tab
- **Discovery Parameters**: Topics, date range, licenses, star limits
- **Quality Controls**: Health thresholds, CI/CD requirements, test requirements
- **Embeddings Config**: Provider selection (SBERT/OpenAI), model choice
- **Scoring Weights**: Adjust Novelty, Health, Relevance, Diversity weights
- **LLM Controls**: 
  - `skip_llm_insertion` toggle (Conservative vs Creative mode)
  - Custom prompt template selection
- **Auto-save**: Settings persist between sessions

#### 🔍 Discovery Tab
- **Real-time Logs**: Live discovery progress with colored output
- **Cache Management**: View cache size, clear cache, exclude processed repos
- **Advanced Controls**: 
  - Long-tail exploration toggle
  - Probe limit adjustment
  - Max stars filter
- **Stop/Resume**: Interrupt long-running discoveries

#### 📊 Results Tab
- **Expandable Sections**: 
  - Refined Goal Analysis
  - Repository Synergy
  - Technical Architecture
  - Innovation Analysis
- **Repository Cards**: Name, URL, license, scores (Novelty, Health, Relevance, GEM)
- **Export Options**: JSON and HTML output
- **Direct Links**: Click repository names to open in browser

---

## 📖 Configuration Files

### config_lightweight.json
```json
{
  "topics": ["red team", "penetration", "security"],
  "goal": "Build ethical red team infrastructure",
  "days": 180,
  "licenses": ["MIT", "Apache-2.0", "GPL-3.0"],
  "max": 20,
  "max_stars": 100,
  "min_health": 0.25,
  "explore_longtail": false,
  "use_embeddings": true,
  "embedding_model": "thenlper/gte-small",
  "w_novelty": 0.35,
  "w_health": 0.25,
  "w_relevance": 0.25,
  "w_diversity": 0.15,
  "skip_llm_insertion": true
}
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `topics` | Search topics (can use GitHub topic names) | required |
| `goal` | Discovery goal for relevance scoring | optional |
| `days` | Days back for activity filter | 90 |
| `max_stars` | Maximum stars ceiling (applies even with `explore_longtail: false`) | null |
| `min_health` | Minimum health score (0.0-1.0) | 0.0 |
| `explore_longtail` | Enable long-tail discovery mode | false |
| `use_embeddings` | Enable semantic embeddings | false |
| `embedding_model` | SBERT model name | `thenlper/gte-small` |
| `skip_llm_insertion` | Conservative LLM mode (prevents AI/ML drift) | false |
| `w_novelty` | Novelty weight in GEM score | 0.35 |
| `w_health` | Health weight in GEM score | 0.25 |
| `w_relevance` | Relevance weight in GEM score | 0.25 |
| `w_diversity` | Diversity weight in GEM score | 0.15 |

---

## 🧠 How It Works

### GEM Score Formula
```
GEM = 0.35×Novelty + 0.25×Health + 0.25×Relevance + 0.15×Diversity
```

#### Scoring Components

**Novelty Score**:
- High velocity (recent pushes)
- Fork/star ratio
- Recent creation

**Health Score**:
- CI/CD presence (GitHub Actions, Travis, CircleCI)
- Test suite presence
- Recent releases
- Package manifest (package.json, Cargo.toml, etc.)

**Relevance Score** (requires embeddings):
- Cosine similarity between repository README and goal
- Uses SBERT embeddings (768-dimensional vectors)

**Diversity Score**:
- Penalizes conceptually similar repositories
- Ensures variety in selected repos

### Ultra Autonomous Workflow

**Phase 1: Discovery**
- Build GitHub search queries from topics
- Fetch repositories with novelty ranking
- Deep probe: analyze README, CI/CD, tests, releases
- Calculate embeddings and relevance (if enabled)
- Apply GEM scoring with diversity bonus
- Select top N repositories

**Phase 2: LLM Refinement** (if OpenAI key provided)
- Pass selected repositories to GPT-5
- Refine discovery goal based on repo synergies
- Apply topic alignment constraint (prevents drift)
- Generate repository synergy analysis
- Create technical architecture blueprint

**Phase 3: Output**
- Save mission JSON with complete analysis
- Include all scores, concepts, and LLM insights
- Ready for further recombination or implementation

---

## 🎛️ API Server

Start the FastAPI server:

```bash
export GITHUB_TOKEN="ghp_..."
export OPENAI_API_KEY="sk-..."
uvicorn gitrecombo.api.server:app --reload --port 8000
```

### Endpoints

**POST /discover**
```json
{
  "topics": ["rust", "async"],
  "days": 30,
  "licenses": ["MIT", "Apache-2.0"],
  "max": 15,
  "use_embeddings": true,
  "goal": "Build async runtime"
}
```

**POST /recombine**
```json
{
  "goal": "Create futures kit for async IO",
  "sources": [...]
}
```

**POST /run**
- Combined discover + recombine pipeline

---

## 🔑 Environment Variables

```bash
# Required for GitHub API
export GITHUB_TOKEN="ghp_your_token_here"

# Optional for LLM features
export OPENAI_API_KEY="sk-your_key_here"

# Optional for embeddings (if using OpenAI instead of SBERT)
# Uses OPENAI_API_KEY by default
```

---

## 📁 Project Structure

```
GitRecombo_v06_full/
├── gitrecombo/
│   ├── discover.py           # Core discovery engine
│   ├── embeddings.py          # SBERT embeddings
│   ├── ultra_autonomous.py    # 3-phase workflow
│   ├── ultra_recombine.py     # LLM recombination
│   ├── desktop_gui.py         # GUI application
│   ├── llm.py                 # OpenAI integration
│   ├── repo_cache.py          # SQLite cache layer
│   └── prompts/
│       ├── goal_refinement_controlled.prompt.txt
│       └── futures_recombiner.prompt.txt
├── missions/                  # Output directory for discoveries
├── config_lightweight.json    # Example configuration
├── run_gui.py                 # GUI launcher
├── requirements.txt           # Core dependencies
├── requirements-llm.txt       # LLM & embeddings
└── README.md
```

---

## 🛠️ Troubleshooting

### Common Issues

**Rate Limiting**
- GitHub API: 5000 requests/hour (authenticated)
- Use `probe_limit` to reduce API calls
- Discovery automatically handles rate limits with waits

**Embeddings Performance**
- SBERT first run downloads ~90MB model
- Subsequent runs use cached model
- Embeddings calculated only for top candidates (probe_limit)

**LLM Refinement**
- Requires OpenAI API key
- GPT-5 used by default
- Set `skip_llm_insertion: true` for conservative mode
- Topic alignment constraint prevents AI/ML drift

**Cache Issues**
- Cache stored in `repo_cache.db`
- Clear via GUI or delete file manually
- Use `--no-cache` flag to bypass reads

---

## 🤝 Contributing

This is a research/educational tool. Contributions welcome for:
- New scoring algorithms
- Additional embedding models
- UI/UX improvements
- Prompt engineering

---

## 📄 License

See LICENSE file for details.

---

## 🙏 Acknowledgments

- **SBERT**: Sentence transformers for embeddings
- **CustomTkinter**: Modern GUI framework
- **GitHub API**: Repository discovery
- **OpenAI**: GPT-5 for LLM refinement
