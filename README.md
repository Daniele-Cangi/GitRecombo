# 🎯 GitRecombo - AI-Powered GitHub Repository Discovery

**Ultra-intelligent repository discovery system with semantic search and recombination engine.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
![AI](https://img.shields.io/badge/AI-OpenAI-orange.svg)

---

## 🚀 Features

- 🧠 **AI-Powered Semantic Search**: Uses OpenAI embeddings to find repositories by meaning, not just keywords
- 📊 **Intelligent Scoring System**: Multi-dimensional health scoring (maintenance, popularity, quality, documentation)
- 🔍 **Advanced GitHub API Integration**: Smart rate-limit management with SearchPlanner
- 🎨 **Modern Web GUI**: Beautiful Streamlit interface with dark/light themes
- 🔄 **Autonomous Discovery**: Hands-free repository exploration across multiple topics
- 📝 **Smart Recombination**: LLM-powered analysis and blueprint generation
- ⚡ **Optimized Performance**: Caching, parallel processing, and intelligent API usage

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- GitHub Personal Access Token
- OpenAI API Key (for semantic search)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/GitRecombo.git
cd GitRecombo/gitrecombo
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy example and edit with your tokens
cp .env.example .env
```

Edit `.env` and add your tokens:
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
OPENAI_API_KEY=sk-your_key_here
```

4. **Launch the GUI**
```bash
streamlit run gui_app.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 🎮 Usage

### Web Interface (Recommended)

1. **Start the GUI**: `streamlit run gui_app.py`
2. **Configure parameters** in the sidebar:
   - Topics to search
   - Time window (days)
   - Number of repositories
   - Health thresholds
   - Enable/disable AI embeddings
3. **Click "Start Discovery"** and watch the magic happen!
4. **View results** in organized tabs with scores and metrics

### Command Line

```bash
# Basic discovery
python ultra_autonomous.py

# Custom configuration
python ultra_autonomous.py --config my_config.json

# Recombine discovered repos
python ultra_recombine.py --json ultra_autonomous_TIMESTAMP.json
```

---

## ⚙️ Configuration

### GUI Parameters

- **Topics**: Define search terms (e.g., "blockchain", "machine learning")
- **Days Window**: How far back to search for repos (default: 90)
- **Licenses**: Filter by open-source licenses (MIT, Apache, BSD, etc.)
- **Min Health Score**: Quality threshold (0.0-1.0)
- **Max Repositories**: Limit results (default: 20)
- **Probe Limit**: Deep analysis depth (default: 40)
- **Use Embeddings**: Enable AI semantic search (slower but smarter)

### Config File Format

```json
{
  "topics": ["embedding", "blockchain", "data transfer"],
  "days": 90,
  "licenses": ["MIT", "Apache-2.0"],
  "min_health_score": 0.25,
  "max_repos_per_topic": 20,
  "probe_limit": 40,
  "use_embeddings": true
}
```

---

## 🧩 Architecture

```
gitrecombo/
├── gui_app.py                    # Streamlit web interface
├── ultra_autonomous.py           # Core discovery engine
├── discover.py                   # GitHub API interactions
├── github_search_planner.py      # Rate limit management
├── embeddings.py                 # OpenAI semantic search
├── llm.py                        # LLM interactions
├── ultra_recombine.py            # Recombination engine
├── repo_cache.py                 # SQLite caching layer
├── cli.py                        # Command-line interface
├── api/
│   └── server.py                 # REST API server
├── prompts/
│   └── futures_recombiner.prompt.txt
├── schemas/
│   └── futures_kit.schema.json
└── templates/
    └── onepage.html.j2
```

---

## 🔬 How It Works

### 1. Discovery Phase
- **Search**: Queries GitHub API with intelligent rate-limit management
- **Filter**: Applies health scoring (stars, forks, issues, commits, docs)
- **Semantic**: Uses OpenAI embeddings to find semantically similar repos
- **Rank**: Scores repositories on multiple dimensions

### 2. Analysis Phase
- **Deep Dive**: Fetches README, code samples, dependencies
- **Cache**: Stores in SQLite for fast re-analysis
- **Score**: Calculates comprehensive health metrics

### 3. Recombination Phase
- **LLM Analysis**: Uses GPT-4 to understand repository purposes
- **Blueprint**: Generates implementation plans
- **Export**: Creates HTML reports with actionable insights

---

## 🎯 Use Cases

- 🔍 **Tech Stack Research**: Find the best libraries for your project
- 🏗️ **Architecture Planning**: Discover patterns and implementations
- 📚 **Learning**: Explore cutting-edge repositories in your field
- 🔄 **Code Reuse**: Find high-quality components to integrate
- 🌟 **Trend Analysis**: See what's popular and well-maintained

---

## 🛠️ Advanced Features

### SearchPlanner

Intelligent rate-limit management that:
- Monitors GitHub API quotas in real-time
- Prevents violations with preventive waits
- Optimizes API call distribution
- Handles both search and code_search endpoints

### Semantic Search

Uses OpenAI embeddings to:
- Find repos by concept, not just keywords
- Match "distributed ledger" with "blockchain"
- Understand natural language queries
- Score semantic similarity (0.0-1.0)

### Health Scoring

Multi-dimensional quality metrics:
- **Maintenance**: Commit frequency, last update
- **Popularity**: Stars, forks, watchers
- **Quality**: Issues resolved, documentation presence
- **Activity**: Contributors, pull requests

---

## 📊 Performance

- **Without Embeddings**: ~3-5 minutes for 40 repos
- **With Embeddings**: ~10-18 minutes for 40 repos (more accurate)
- **Rate Limits**: Automatically managed (30/min search, 10/min code_search)
- **Caching**: Reduces redundant API calls by 60-80%

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT and embedding models
- GitHub for the comprehensive API
- Streamlit for the amazing web framework
- The open-source community for inspiration

---

## 📧 Contact

**Daniele Cangi** - [@Daniele-Cangi](https://github.com/Daniele-Cangi)

Project Link: [https://github.com/Daniele-Cangi/GitRecombo](https://github.com/Daniele-Cangi/GitRecombo)

---

## ⚡ Quick Tips

- Start with **embeddings OFF** for fast testing
- Use **probe_limit=15** for quick exploration
- Enable **embeddings** for production-quality results
- Set **days=30** for recent, active projects
- Check **GitHub rate limits** before long runs

**Star ⭐ this repo if you find it useful!**
