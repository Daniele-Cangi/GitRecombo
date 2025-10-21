"""
GitRecombo Discovery Engine - Professional Web Interface
Advanced GitHub repository discovery with AI-powered recombination
"""

import streamlit as st
import os
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# Page config
st.set_page_config(
    page_title="GitRecombo Discovery Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'topics' not in st.session_state:
    # 🔄 RIPRISTINATO ai 6 topics ORIGINALI
    st.session_state.topics = ["embedding", "blockchain", "data transfer", "machine learning", "P2P", "gateway"]
if 'running' not in st.session_state:
    st.session_state.running = False
if 'last_mission' not in st.session_state:
    st.session_state.last_mission = None
if 'presets' not in st.session_state:
    st.session_state.presets = {
        "AI/ML Infrastructure": {
            "topics": ["embedding", "machine learning", "neural network", "inference", "training"],
            "days": 90,
            "min_health": 0.25
        },
        "Blockchain & Web3": {
            "topics": ["blockchain", "smart contract", "defi", "consensus", "cryptocurrency"],
            "days": 60,
            "min_health": 0.30
        },
        "Edge Computing": {
            "topics": ["edge computing", "iot", "embedded", "real-time", "distributed"],
            "days": 90,
            "min_health": 0.20
        },
        "Security & Privacy": {
            "topics": ["encryption", "privacy", "authentication", "security", "zero-knowledge"],
            "days": 120,
            "min_health": 0.35
        }
    }

# Theme configurations
THEMES = {
    'dark': {
        'bg_primary': '#0E1117',
        'bg_secondary': '#1E1E1E',
        'bg_card': '#262730',
        'text_primary': '#FAFAFA',
        'text_secondary': '#D1D5DB',  # ⚡ Cambiato da #B3B3B3 a #D1D5DB (più leggibile!)
        'accent': '#667EEA',
        'accent_secondary': '#764BA2',
        'border': '#3D3D3D',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'chart_bg': '#1E1E1E'
    },
    'light': {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F7F7F7',
        'bg_card': '#FFFFFF',
        'text_primary': '#1F2937',
        'text_secondary': '#6B7280',
        'accent': '#667EEA',
        'accent_secondary': '#764BA2',
        'border': '#E5E7EB',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'chart_bg': '#FFFFFF'
    }
}

current_theme = THEMES[st.session_state.theme]

# Advanced CSS Styling with Theme Support
st.markdown(f"""
<style>
    /* Global Styles */
    .main {{
        background-color: {current_theme['bg_primary']};
        color: {current_theme['text_primary']};
    }}
    
    .stApp {{
        background-color: {current_theme['bg_primary']};
    }}
    
    /* Forza testo leggibile ovunque */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: {current_theme['text_primary']} !important;
    }}
    
    small, .stCaption {{
        color: {current_theme['text_secondary']} !important;
    }}
    
    /* Header */
    .app-header {{
        padding: 2rem 0;
        border-bottom: 2px solid {current_theme['border']};
        margin-bottom: 2rem;
    }}
    
    .app-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, {current_theme['accent']} 0%, {current_theme['accent_secondary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    
    .app-subtitle {{
        color: {current_theme['text_secondary']};
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }}
    
    /* Cards */
    .metric-card {{
        background: linear-gradient(135deg, {current_theme['accent']} 0%, {current_theme['accent_secondary']} 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }}
    
    .info-card {{
        background: {current_theme['bg_card']};
        border: 1px solid {current_theme['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }}
    
    .score-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        background: linear-gradient(135deg, {current_theme['accent']} 0%, {current_theme['accent_secondary']} 100%);
        color: white;
    }}
    
    /* Topic Pills */
    .topic-pill {{
        display: inline-block;
        background: {current_theme['bg_card']};
        border: 2px solid {current_theme['accent']};
        color: {current_theme['text_primary']};
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        margin: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s;
    }}
    
    .topic-pill:hover {{
        background: {current_theme['accent']};
        color: white;
        transform: scale(1.05);
    }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {current_theme['accent']} 0%, {current_theme['accent_secondary']} 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100%;
        transition: all 0.3s !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        cursor: pointer !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2) !important;
        opacity: 0.9 !important;
    }}
    
    .stButton>button:active {{
        transform: translateY(0) !important;
    }}
    
    .stButton>button:disabled {{
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }}
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }}
    
    /* Progress */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {current_theme['accent']} 0%, {current_theme['accent_secondary']} 100%);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        border-bottom: 2px solid {current_theme['border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {current_theme['text_secondary']};
        font-weight: 600;
        padding: 1rem 0;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {current_theme['accent']};
        border-bottom: 3px solid {current_theme['accent']};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {current_theme['bg_card']};
        border: 1px solid {current_theme['border']};
        border-radius: 8px;
        font-weight: 600;
        color: {current_theme['text_primary']};
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        background: {current_theme['bg_secondary']} !important;
        border: 1px solid {current_theme['border']};
        border-radius: 8px;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {current_theme['text_primary']};
        font-size: 2rem;
        font-weight: 700;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {current_theme['text_secondary']};
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {current_theme['bg_secondary']};
        border-right: 1px solid {current_theme['border']};
    }}
    
    [data-testid="stSidebar"] label {{
        color: {current_theme['text_primary']} !important;
        font-weight: 500 !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {current_theme['text_primary']} !important;
    }}
    
    [data-testid="stSidebar"] p {{
        color: {current_theme['text_primary']} !important;
    }}
    
    /* Input fields */
    .stTextInput input {{
        color: {current_theme['text_primary']} !important;
        background: {current_theme['bg_card']} !important;
        border: 1px solid {current_theme['border']} !important;
    }}
    
    .stTextInput input::placeholder {{
        color: {current_theme['text_secondary']} !important;
    }}
    
    /* Slider */
    .stSlider label {{
        color: {current_theme['text_primary']} !important;
    }}
    
    /* Multiselect */
    .stMultiSelect label {{
        color: {current_theme['text_primary']} !important;
    }}
    
    /* Checkbox */
    .stCheckbox label {{
        color: {current_theme['text_primary']} !important;
    }}
    
    /* Theme toggle */
    .theme-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
        background: {current_theme['bg_card']};
        border: 2px solid {current_theme['border']};
        border-radius: 9999px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-weight: 600;
        color: {current_theme['text_primary']};
        transition: all 0.3s;
    }}
    
    .theme-toggle:hover {{
        background: {current_theme['accent']};
        color: white;
        border-color: {current_theme['accent']};
    }}
    
    /* Status indicators */
    .status-success {{
        color: {current_theme['success']};
        font-weight: 600;
    }}
    
    .status-warning {{
        color: {current_theme['warning']};
        font-weight: 600;
    }}
    
    .status-error {{
        color: {current_theme['error']};
        font-weight: 600;
    }}
    
    /* Animation */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease-out;
    }}
</style>
""", unsafe_allow_html=True)

# Helper Functions
def toggle_theme():
    """Toggle between light and dark theme"""
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    st.rerun()

def create_score_chart(scores: Dict[str, float]) -> go.Figure:
    """Create radar chart for scores"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor=f'rgba(102, 126, 234, 0.3)',
        line=dict(color=current_theme['accent'], width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=current_theme['border']),
            bgcolor=current_theme['chart_bg']
        ),
        showlegend=False,
        paper_bgcolor=current_theme['chart_bg'],
        plot_bgcolor=current_theme['chart_bg'],
        font=dict(color=current_theme['text_primary']),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_gem_distribution(sources: List[Dict]) -> go.Figure:
    """Create GEM score distribution chart"""
    gem_scores = [s.get('gem_score', 0) for s in sources]
    names = [s.get('name', '').split('/')[-1] for s in sources]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names,
        y=gem_scores,
        marker=dict(
            color=gem_scores,
            colorscale=[[0, current_theme['error']], [0.5, current_theme['warning']], [1, current_theme['success']]],
            showscale=False
        ),
        text=[f'{score:.3f}' for score in gem_scores],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='GEM Score Distribution',
        xaxis_title='Repository',
        yaxis_title='GEM Score',
        paper_bgcolor=current_theme['chart_bg'],
        plot_bgcolor=current_theme['chart_bg'],
        font=dict(color=current_theme['text_primary']),
        xaxis=dict(gridcolor=current_theme['border']),
        yaxis=dict(gridcolor=current_theme['border'], range=[0, 1]),
        height=400
    )
    
    return fig

def create_score_breakdown(sources: List[Dict]) -> go.Figure:
    """Create stacked bar chart for score breakdown"""
    names = [s.get('name', '').split('/')[-1] for s in sources]
    novelty = [s.get('novelty_score', 0) * s.get('gem_score', 0) for s in sources]
    health = [s.get('health_score', 0) * s.get('gem_score', 0) * 0.5 for s in sources]
    relevance = [s.get('relevance', 0) * s.get('gem_score', 0) * 0.5 for s in sources]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Novelty', x=names, y=novelty, marker_color=current_theme['accent']))
    fig.add_trace(go.Bar(name='Health', x=names, y=health, marker_color=current_theme['success']))
    fig.add_trace(go.Bar(name='Relevance', x=names, y=relevance, marker_color=current_theme['warning']))
    
    fig.update_layout(
        barmode='stack',
        title='Score Component Breakdown',
        xaxis_title='Repository',
        yaxis_title='Weighted Score',
        paper_bgcolor=current_theme['chart_bg'],
        plot_bgcolor=current_theme['chart_bg'],
        font=dict(color=current_theme['text_primary']),
        xaxis=dict(gridcolor=current_theme['border']),
        yaxis=dict(gridcolor=current_theme['border']),
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def save_preset(name: str, config: Dict):
    """Save current configuration as preset"""
    st.session_state.presets[name] = config
    # Save to file
    preset_file = Path("presets.json")
    with open(preset_file, 'w') as f:
        json.dump(st.session_state.presets, f, indent=2)

def load_preset(name: str):
    """Load configuration from preset"""
    if name in st.session_state.presets:
        preset = st.session_state.presets[name]
        st.session_state.topics = preset.get('topics', [])
        return preset
    return None

# Header with Theme Toggle
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="app-title">GitRecombo Discovery Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Autonomous GitHub repository discovery with AI-powered recombination</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    theme_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
    if st.button(f"{theme_icon} Theme", key="theme_toggle"):
        toggle_theme()

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

# Topics Management
st.sidebar.subheader("📚 Topics")
st.sidebar.caption("Topics to search on GitHub")

# Display current topics
for i, topic in enumerate(st.session_state.topics):
    col1, col2 = st.sidebar.columns([4, 1])
    with col1:
        st.text(f"• {topic}")
    with col2:
        if st.button("❌", key=f"remove_{i}"):
            st.session_state.topics.pop(i)
            st.rerun()

# Add new topic
new_topic = st.sidebar.text_input("Add new topic", key="new_topic")
if st.sidebar.button("➕ Add Topic"):
    if new_topic and new_topic not in st.session_state.topics:
        st.session_state.topics.append(new_topic)
        st.rerun()

st.sidebar.markdown("---")

# Discovery Parameters
st.sidebar.subheader("🔧 Discovery Parameters")

days = st.sidebar.slider(
    "Days window",
    min_value=7,
    max_value=365,
    value=90,  # 🔄 RIPRISTINATO a 90 (valore originale)
    help="Search repos pushed in the last N days"
)

licenses = st.sidebar.multiselect(
    "Licenses",
    ["MIT", "Apache-2.0", "BSD-3-Clause", "MPL-2.0", "GPL-3.0", "LGPL-3.0"],
    default=["MIT", "Apache-2.0", "BSD-3-Clause", "MPL-2.0"],  # 🔄 RIPRISTINATO a 4 licenze
    help="Filter by license type"
)

min_health = st.sidebar.slider(
    "Min health score",
    min_value=0.0,
    max_value=1.0,
    value=0.25,  # 🔄 RIPRISTINATO a 0.25 (valore originale)
    step=0.05,
    help="Minimum health score"
)

max_repos = st.sidebar.slider(
    "Max repos per topic",
    min_value=5,
    max_value=50,
    value=20,  # 🔄 RIPRISTINATO a 20 (valore originale)
    help="Maximum repos to fetch per topic"
)

probe_limit = st.sidebar.slider(
    "Probe limit",
    min_value=5,
    max_value=100,
    value=40,  # 🔄 RIPRISTINATO a 40 (valore originale)
    help="Number of repos to analyze in depth"
)

# Advanced weights
st.sidebar.subheader("⚖️ Score Weights")
with st.sidebar.expander("Advanced Weights", expanded=False):
    w_novelty = st.slider("Novelty", 0.0, 1.0, 0.35, 0.05)
    w_health = st.slider("Health", 0.0, 1.0, 0.25, 0.05)
    w_relevance = st.slider("Relevance", 0.0, 1.0, 0.25, 0.05)
    w_diversity = st.slider("Diversity", 0.0, 1.0, 0.10, 0.05)
    
    total_weight = w_novelty + w_health + w_relevance + w_diversity
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_weight:.2f}, should be 1.0")

use_embeddings = st.sidebar.checkbox(
    "Use embeddings",
    value=True,  # 🔄 RIPRISTINATO a True - Ora puoi testare con AI embeddings!
    help="Enable semantic similarity scoring (finds related concepts by meaning)"
)

if use_embeddings:
    embedding_model = st.sidebar.selectbox(
        "Embedding Model",
        options=[
            "gte-large-en-v1.5 (Local, 1.3GB, Score 65.4) 🏆",
            "OpenAI text-embedding-3-small (Cloud, Score 62.3)",
            "bge-large-en-v1.5 (Local, 1.3GB, Score 63.9)"
        ],
        index=0,
        help="Choose embedding model: Local models are free and private, OpenAI is cloud-based"
    )
else:
    embedding_model = None

explore_longtail = st.sidebar.checkbox(
    "Explore long-tail",
    value=False,
    help="Include repos with low stars"
)

# Main area - Run Discovery
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.metric("Topics", len(st.session_state.topics))
with col2:
    st.metric("Days Window", f"{days} days")
with col3:
    st.metric("Max Repos", max_repos)

st.markdown("---")

# Discovery Goal
goal = st.text_area(
    "🎯 Discovery Goal (optional)",
    value="Discover cutting-edge repositories in AI/ML infrastructure that enable building local-first, privacy-preserving, real-time intelligent systems",
    height=100,
    help="Describe what you want to discover. Will be refined by GPT-5."
)

# Run button
if st.button("🚀 Start Discovery", disabled=st.session_state.running, type="primary"):
    st.session_state.running = True
    
    # Create config for ultra_autonomous.py
    config = {
        "topics": st.session_state.topics,
        "days": days,
        "licenses": ",".join(licenses),
        "min_health": min_health,
        "max": max_repos,
        "probe_limit": probe_limit,
        "w_novelty": w_novelty,
        "w_health": w_health,
        "w_relevance": w_relevance,
        "w_diversity": w_diversity,
        "use_embeddings": use_embeddings,
        "embedding_model": embedding_model if use_embeddings else None,
        "explore_longtail": explore_longtail,
        "goal": goal
    }
    
    # Save config to temp file
    config_path = Path("gui_config.json")
    with open(config_path, "w", encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    st.info(f"🔄 Running discovery with AI embeddings... Estimated time: ~{probe_limit // 5 + 3}-{probe_limit // 3 + 5} minutes")
    
    # Real-time progress display
    status_text = st.empty()
    output_container = st.expander("📜 Live Output", expanded=True)
    output_text = output_container.empty()
    
    # Run discovery with REAL-TIME output streaming
    try:
        import subprocess
        
        status_text.text("🚀 Phase 1/3: Autonomous Discovery (finding repos)...")
        
        # Launch discovery with streaming output
        process = subprocess.Popen(
            ["python", "ultra_autonomous.py", "--config", str(config_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
            # Show last 30 lines
            output_text.code('\n'.join(output_lines[-30:]), language='bash')
            
            # Update phase based on output
            if "PHASE 2" in line or "GOAL REFINEMENT" in line:
                status_text.text("🧠 Phase 2/3: Goal Refinement (GPT-5 analysis)...")
            elif "PHASE 3" in line or "ENRICHMENT" in line:
                status_text.text("📚 Phase 3/3: Fetching READMEs...")
            elif "Loading embedding model" in line:
                status_text.text("🔄 Loading embedding model (gte-large-en-v1.5)...")
        
        process.wait()
        
        if process.returncode == 0:
            status_text.text("✅ Discovery completed! Finding latest results...")
            
            # Find latest mission file
            mission_files = sorted(Path(".").glob("ultra_autonomous_*.json"))
            if mission_files:
                st.session_state.last_mission = str(mission_files[-1])
                
                # Count repos
                with open(mission_files[-1], 'r', encoding='utf-8') as f:
                    mission_data = json.load(f)
                    repos_selected = len(mission_data.get('sources', []))
                
                status_text.text("✅ Discovery completed!")
                st.success(f"🎉 Discovery completed! {repos_selected} repos selected.")
                st.balloons()
            else:
                st.error("No mission file generated")
        else:
            st.error(f"Discovery failed with exit code {process.returncode}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    finally:
        st.session_state.running = False
        if config_path.exists():
            config_path.unlink()

# Results section
st.markdown("---")
st.header("📊 Results")

# Find latest results
mission_files = sorted(Path(".").glob("ultra_autonomous_*.json"), reverse=True)
blueprint_files = sorted(Path(".").glob("ultra_blueprint_*.html"), reverse=True)
recomb_files = sorted(Path(".").glob("ultra_recombination_*.json"), reverse=True)

if mission_files and recomb_files:
    latest_mission = mission_files[0]
    latest_recomb = recomb_files[0]
    latest_blueprint = blueprint_files[0] if blueprint_files else None
    
    # Display timestamp
    timestamp = latest_mission.stem.split("_")[-2:]
    st.caption(f"Latest run: {timestamp[0]} {timestamp[1]}")
    
    # Load mission data with UTF-8 encoding
    with open(latest_mission, 'r', encoding='utf-8') as f:
        mission_data = json.load(f)
    
    # Load recombination data with UTF-8 encoding
    with open(latest_recomb, 'r', encoding='utf-8') as f:
        recomb_data = json.load(f)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sources Found", len(mission_data.get("sources", [])))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        avg_gem = sum(s.get("gem_score", 0) for s in mission_data.get("sources", [])) / max(len(mission_data.get("sources", [])), 1)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg GEM Score", f"{avg_gem:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        metrics = mission_data.get("metrics", {})
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Candidates", metrics.get("candidates", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Probed", metrics.get("probed", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Repos", "💡 Concepts", "🎯 Goal", "📄 Blueprint"])
    
    with tab1:
        st.subheader("Selected Repositories")
        
        for i, source in enumerate(mission_data.get("sources", []), 1):
            with st.expander(f"{i}. {source['name']} - GEM: {source.get('gem_score', 0):.4f} ⭐"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**URL:** [{source['url']}]({source['url']})")
                    st.write(f"**License:** {source.get('license', 'N/A')}")
                    st.write(f"**Role:** {source.get('role', 'N/A')}")
                
                with col2:
                    st.write("**Scores:**")
                    st.write(f"Novelty: {source.get('novelty_score', 0):.3f}")
                    st.write(f"Health: {source.get('health_score', 0):.3f}")
                    st.write(f"Relevance: {source.get('relevance', 0):.3f}")
                    st.write(f"Author: {source.get('author_rep', 0):.3f}")
                
                if source.get('concepts'):
                    st.write("**Concepts:**")
                    st.write(", ".join(source['concepts'][:8]))
    
    with tab2:
        st.subheader("Innovation Concepts")
        
        concepts = recomb_data.get("recombination", {}).get("concepts", [])
        
        for i, concept in enumerate(concepts, 1):
            st.markdown(f"### Concept {i}")
            
            problem = concept.get("problem", "")
            solution = concept.get("solution", "")
            
            st.write("**Problem:**")
            st.info(problem)
            
            st.write("**Solution:**")
            st.success(solution)
            
            if concept.get("architecture_ascii"):
                st.write("**Architecture:**")
                st.code(concept["architecture_ascii"], language="text")
            
            # KPIs
            if concept.get("kpis_90d"):
                st.write("**KPIs (90 days):**")
                for kpi in concept["kpis_90d"]:
                    st.write(f"• {kpi}")
            
            st.markdown("---")
    
    with tab3:
        st.subheader("Refined Goal")
        
        project = recomb_data.get("recombination", {}).get("project", {})
        
        st.write(f"### {project.get('name', 'N/A')}")
        st.write(f"**{project.get('tagline', '')}**")
        
        st.write("**Vision:**")
        st.info(project.get('vision', ''))
        
        st.write("**Why Now:**")
        st.success(project.get('why_now', ''))
    
    with tab4:
        st.subheader("Blueprint HTML")
        
        if latest_blueprint and latest_blueprint.exists():
            st.write(f"**File:** `{latest_blueprint.name}`")
            
            # Download button
            with open(latest_blueprint, "rb") as f:
                st.download_button(
                    label="📥 Download Blueprint",
                    data=f,
                    file_name=latest_blueprint.name,
                    mime="text/html"
                )
            
            # Preview
            with st.expander("Preview HTML"):
                with open(latest_blueprint, "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.code(html_content[:2000] + "...", language="html")
        else:
            st.warning("No blueprint HTML found")

else:
    st.info("👆 Run a discovery to see results")

# Footer
st.markdown("---")
st.caption("🔬 GitRecombo v0.6 - Ultra Autonomous Discovery Engine")
