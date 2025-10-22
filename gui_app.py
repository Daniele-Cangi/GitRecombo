"""Minimal, robust Streamlit control room for GitRecombo.

This replacement focuses on stability and a small surface area:
- clear "fresh run" and "clear processed" buttons
- explicit flags: --no-cache, --clear-processed, --search-only
- resilient subprocess output streaming (utf-8 replace)
- show latest mission and allow download

The UI intentionally keeps the discovery parameter surface small; advanced
parameters can still be provided via a config file and the existing CLI flags.
"""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

RESULT_DIR = Path(".")
CONFIG_PATH = RESULT_DIR / "gui_config.json"


def _latest_file(pattern: str) -> Optional[Path]:
    files = sorted(RESULT_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path or not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        st.warning(f"Impossibile leggere {path.name}: {exc}")
        return None


def run_subprocess(command: List[str], preview_area, status_area, progress_bar=None, max_est_lines: int = 200) -> int:
    """Run a subprocess, stream a short preview to the GUI and update an approximate progress bar.

    The full log is stored in `st.session_state['last_log']` so the UI can show it on demand.
    """
    # Show the command for reproducibility
    status_area.info("Avviando: " + shlex.join(command))
    log_lines: List[str] = []
    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True,
            cwd=str(RESULT_DIR),
        )
    except Exception as exc:
        status_area.error(f"Impossibile avviare processo: {exc}")
        return -1

    try:
        for line in proc.stdout or []:
            cleaned = line.rstrip("\n")
            if cleaned:
                log_lines.append(cleaned)
                # show small preview (last 3 lines) to keep UI snappy
                preview_area.text("\n".join(log_lines[-3:]))
                # update approx progress
                if progress_bar is not None:
                    pct = min(100, int(len(log_lines) / max_est_lines * 100))
                    try:
                        progress_bar.progress(pct)
                    except Exception:
                        pass
    except Exception as exc:
        status_area.error(f"Errore leggendo output processo: {exc}")

    proc.wait()
    # ensure progress shows 100% at end
    if progress_bar is not None:
        try:
            progress_bar.progress(100)
        except Exception:
            pass

    # store full log for GUI inspection
    try:
        st.session_state['last_log'] = log_lines
    except Exception:
        pass

    if proc.returncode == 0:
        status_area.success("Completato con successo.")
    else:
        status_area.error(f"Terminato con codice {proc.returncode}.")
    return proc.returncode


st.set_page_config(page_title="GitRecombo Control Room", layout="wide")

if "running" not in st.session_state:
    st.session_state.running = False

st.title("GitRecombo Control Room - Minimal")
st.caption("Interfaccia semplificata per lanciare discovery e scaricare risultati.")

with st.sidebar:
    st.header("Run options")
    no_cache = st.checkbox("--no-cache (bypass cache read checks)", value=False)
    clear_processed = st.checkbox("--clear-processed (purge processed markers)", value=False)
    search_only = st.checkbox("--no-search (solo ricerca, no LLM)", value=False)
    auto_recombine = st.checkbox("Auto recombine dopo discovery", value=False)
    min_interval = st.number_input("Min interval between runs (s)", min_value=0, max_value=86400, value=30)
    st.markdown("---")
    st.subheader("Discovery query")
    topics_text = st.text_area("Topics (uno per riga)", value="networking\ndatabase\ndevops", height=120)
    days = st.number_input("Window (days)", min_value=7, max_value=365, value=90)

    st.markdown("---")
    st.subheader("Advanced (minimal)")
    max_repos = st.number_input("Max repos per topic", min_value=1, max_value=200, value=20)
    probe_limit = st.number_input("Probe limit", min_value=1, max_value=500, value=40)
    min_health = st.slider("Min health", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    explore_longtail = st.checkbox("Esplora long-tail", value=False)
    enable_max_stars = st.checkbox("Limita stelle massime", value=False)
    max_stars_value = st.number_input("Stelle massime", min_value=10, max_value=500000, step=10, value=500) if enable_max_stars else None
    use_embeddings = st.checkbox("Usa embeddings", value=True)
    embed_max_chars = st.number_input("Embedding max chars", min_value=1000, max_value=20000, step=500, value=8000)
    require_ci = st.checkbox("Richiedi CI", value=False)
    require_tests = st.checkbox("Richiedi test", value=False)
    authorsig = st.checkbox("Boost autore", value=True)
    EMBEDDING_CHOICES = [
        "gte-large (sbert)",
        "text-embedding-3-small (openai)",
        "bge-large (sbert)",
    ]
    embedding_choice = st.selectbox("Scelta embedding (opzionale)", options=EMBEDDING_CHOICES, index=0 if use_embeddings else 0)
    st.markdown('---')
    st.subheader('Past discoveries')
    # build list of mission files
    mission_files = sorted([p for p in RESULT_DIR.glob('ultra_autonomous_*.json')], key=lambda p: p.stat().st_mtime, reverse=True)
    mission_names = [p.name for p in mission_files]
    if 'selected_mission' not in st.session_state:
        st.session_state.selected_mission = mission_names[0] if mission_names else None

    sel_idx = 0
    if st.session_state.selected_mission and st.session_state.selected_mission in mission_names:
        sel_idx = mission_names.index(st.session_state.selected_mission)

    if mission_names:
        chosen = st.selectbox('Seleziona discovery', mission_names, index=sel_idx)
        st.session_state.selected_mission = chosen
        nav_col1, nav_col2, nav_col3 = st.columns([1,1,1])
        with nav_col1:
            if st.button('Prev'):
                i = max(0, mission_names.index(st.session_state.selected_mission) - 1)
                st.session_state.selected_mission = mission_names[i]
                st.experimental_rerun()
        with nav_col2:
            if st.button('Next'):
                i = min(len(mission_names)-1, mission_names.index(st.session_state.selected_mission) + 1)
                st.session_state.selected_mission = mission_names[i]
                st.experimental_rerun()
        with nav_col3:
            if st.button('Reload list'):
                # refresh the page to re-read files
                st.experimental_rerun()
    else:
        st.info('No past discoveries found')

col1, col2 = st.columns([1, 2])
run_btn = col1.button("Fresh discovery run", disabled=st.session_state.running)
clear_btn = col1.button("Purge processed now")
latest_mission = _latest_file("ultra_autonomous_*.json")

log_area = col2.empty()
status_area = col2.empty()
progress_placeholder = col2.empty()
if 'last_log' not in st.session_state:
    st.session_state['last_log'] = []


if run_btn and not st.session_state.running:
    import time as _time
    now_ts = _time.time()
    # enforce client-side cooldown
    if now_ts - float(st.session_state.get('last_run', 0.0)) < float(min_interval):
        wait_for = int(float(min_interval) - (now_ts - float(st.session_state.get('last_run', 0.0))))
        status_area.warning(f"Please wait {wait_for}s before starting a new run (min interval).")
    else:
        st.session_state.running = True
        # minimal config file written so CLI receives something; users can provide a full config otherwise
        cfg: Dict[str, Any] = {"notes": "Run from GUI"}
        # add user-provided discovery parameters
        topics = [t.strip() for t in topics_text.splitlines() if t.strip()]
        cfg.update({
            "topics": topics,
            "days": int(days),
            "max": int(max_repos),
            "probe_limit": int(probe_limit),
            "min_health": float(min_health),
            "explore_longtail": bool(explore_longtail),
            "max_stars": int(max_stars_value) if max_stars_value is not None else None,
            "use_embeddings": bool(use_embeddings),
            "embedding_model_choice": str(embedding_choice),
            "embed_max_chars": int(embed_max_chars),
            "require_ci": bool(require_ci),
            "require_tests": bool(require_tests),
            "authorsig": bool(authorsig),
        })
        with CONFIG_PATH.open("w", encoding="utf-8") as fh:
            json.dump(cfg, fh, ensure_ascii=False)

        cmd = ["python", "-u", "ultra_autonomous.py", "--config", str(CONFIG_PATH)]
        if no_cache:
            cmd.append("--no-cache")
        if clear_processed:
            cmd.append("--clear-processed")
        if search_only:
            cmd.append("--search-only")

    # record start timestamp
    st.session_state.last_run = _time.time()
    # create a progress bar and preview area
    p = progress_placeholder.progress(0)
    code = run_subprocess(cmd, log_area, status_area, progress_bar=p)
    try:
        CONFIG_PATH.unlink()
    except Exception:
        pass

    if code == 0 and auto_recombine:
        latest = _latest_file("ultra_autonomous_*.json")
        if latest:
            status_area.info("Avviando recombination...")
            run_subprocess(["python", "-u", "ultra_recombine.py", "--mission", str(latest)], log_area, status_area, progress_bar=progress_placeholder.progress(0))

    # mark not running before forcing a UI refresh
    st.session_state.running = False
    status_area.info("Aggiornamento UI per mostrare i risultati più recenti...")
    try:
        st.experimental_rerun()
    except Exception:
        # If rerun isn't allowed in this context, just continue and let the page refresh normally
        pass

if clear_btn:
    # quick action to purge processed markers via CLI
    status_area.info("Eseguo purge processed via CLI...")
    run_subprocess(["python", "-u", "ultra_autonomous.py", "--clear-processed"], log_area, status_area, progress_bar=progress_placeholder.progress(0))
    # Refresh GUI so it picks up any changes
    status_area.info("Aggiornamento UI dopo purge processed...")
    try:
        st.experimental_rerun()
    except Exception:
        pass

st.markdown("---")
st.header("Latest discovery / Selected")
# Use selected mission from sidebar if present
sel = st.session_state.get('selected_mission')
if sel:
    mission_path = Path(sel)
    if not mission_path.exists():
        # selected mission may be a name only in workspace root
        mission_path = RESULT_DIR / sel
else:
    mission_path = _latest_file("ultra_autonomous_*.json")

mission = _load_json(mission_path) if mission_path and mission_path.exists() else None
if mission:
    st.subheader(f"Mission: {mission_path.name}")
    st.write(mission.get("refined_goal", ""))
    col_dl, col_view = st.columns([1, 1])
    with col_dl:
        if st.button("Download mission JSON"):
            with mission_path.open("rb") as fh:
                st.download_button("Download", data=fh, file_name=mission_path.name, mime="application/json")
    with col_view:
        if st.button("Show latest discovery"):
            # Display structured discovery details
            st.subheader("Refined goal")
            st.write(mission.get("refined_goal", ""))
            st.subheader("Metrics")
            metrics = mission.get("metrics", {})
            st.write(metrics)

            st.subheader("Selected sources")
            sources = mission.get("sources", []) or []
            rows = []
            for src in sources:
                rows.append({
                    "Repository": src.get("name"),
                    "GEM": src.get("scores", {}).get("gem_score") if isinstance(src.get("scores"), dict) else src.get("gem_score"),
                    "Novelty": src.get("scores", {}).get("novelty") if isinstance(src.get("scores"), dict) else src.get("novelty_score"),
                    "Health": src.get("scores", {}).get("health") if isinstance(src.get("scores"), dict) else src.get("health_score"),
                    "Relevance": src.get("scores", {}).get("relevance") if isinstance(src.get("scores"), dict) else src.get("relevance"),
                    "Author": src.get("scores", {}).get("author_rep") if isinstance(src.get("scores"), dict) else src.get("author_rep"),
                    "Role": src.get("role") or src.get("language") or "N/A",
                    "License": src.get("license", "N/A"),
                    "URL": src.get("url"),
                })
            if rows:
                # show each source with clickable link and README expander
                for src in sources:
                    name = src.get('name')
                    url = src.get('url')
                    scores = src.get('scores') or {}
                    gem = scores.get('gem_score') if isinstance(scores, dict) else src.get('gem_score')
                    novelty = scores.get('novelty') if isinstance(scores, dict) else src.get('novelty_score')
                    health = scores.get('health') if isinstance(scores, dict) else src.get('health_score')
                    st.markdown(f"**[{name}]({url})** — GEM: {gem} • Novelty: {novelty} • Health: {health}")
                    snippet = src.get('readme_snippet') or src.get('description') or ''
                    with st.expander('README / snippet'):
                        st.write(snippet)
                    st.markdown('---')
            else:
                st.info("Nessuna sorgente selezionata nel file mission.")
    # Show / hide full log
    if st.button('Show/Hide last run log'):
        with st.expander('Last run log'):
            last = st.session_state.get('last_log', [])
            if last:
                st.text('\n'.join(last))
            else:
                st.info('No log available')
else:
    st.info("Nessuna mission trovata.")
