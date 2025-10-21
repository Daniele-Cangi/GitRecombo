from __future__ import annotations
import os, json, math, re, time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import requests
from dateutil import parser as dtp
from github_search_planner import SearchPlanner
from repo_cache import RepoCache

GH_API = "https://api.github.com"
GH_ACCEPT = "application/vnd.github+json"
GH_VERSION = "2022-11-28"

# Global search planner and cache instances
_search_planner: Optional[SearchPlanner] = None
_repo_cache: Optional[RepoCache] = None

# Legacy rate limit tracking (for backward compatibility)
_last_code_search_time = 0.0
_code_search_count = 0
_code_search_window_start = 0.0

PRESETS = {
    "vector-rust": "pushed:>{date} language:Rust topic:vector",  # Use pushed: for activity-based search
    "mamba": "pushed:>{date} language:Python topic:mamba",
    "gpu-kernel": "pushed:>{date} language:C++ topic:cuda",
    "streaming": "pushed:>{date} language:TypeScript topic:webtransport",
}

STOP = set("""a an and are as at be by for from has have in is it its of on or that the to with you your we i our this these those via into over under using use used new fast real
il lo la gli le un una uno che di a da in con su per tra fra e o ma se non piu più come""".split())

def days_since(dt_str: str) -> float:
    try:
        dt = dtp.parse(dt_str)
        return max((datetime.now(timezone.utc) - dt).total_seconds() / 86400.0, 1e-6)
    except Exception:
        return 3650.0

def novelty_score(repo: Dict[str, Any]) -> float:
    stars = repo.get("stargazers_count", 0) or 0
    created_days = days_since(repo.get("created_at", "1970-01-01T00:00:00Z"))
    pushed_days = days_since(repo.get("pushed_at", "1970-01-01T00:00:00Z"))
    forks = repo.get("forks_count", 0) or 0
    fork_penalty = 0.2 if repo.get("fork", False) else 0.0
    sv_norm = math.tanh((stars / max(created_days, 1e-6)) / 50.0)
    fr_norm = 1.0 / (1.0 + pushed_days)
    base = 0.55*sv_norm + 0.40*fr_norm + 0.05*math.tanh(forks / 50.0)
    return max(0.0, min(1.0, base - fork_penalty))

def get_search_planner() -> SearchPlanner:
    """Get or create global SearchPlanner instance."""
    global _search_planner
    if _search_planner is None:
        _search_planner = SearchPlanner()
    return _search_planner

def get_repo_cache() -> RepoCache:
    """Get or create global RepoCache instance."""
    global _repo_cache
    if _repo_cache is None:
        _repo_cache = RepoCache()
    return _repo_cache

def gh_get(url: str, token: str, params: Dict[str, Any] | None = None, retry: int = 3, use_planner: bool = True) -> Dict[str, Any]:
    """GitHub API call with smart rate limit handling"""
    global _last_code_search_time, _code_search_count, _code_search_window_start
    
    # Determine endpoint type
    endpoint_type = "rest"
    if "/search/repositories" in url:
        endpoint_type = "search"
    elif "/search/code" in url:
        endpoint_type = "code_search"
    
    planner = get_search_planner() if use_planner else None
    
    for attempt in range(retry):
        # Use SearchPlanner for rate limiting
        if planner:
            planner.wait_if_needed(endpoint_type)
        else:
            # Legacy throttling for backward compatibility
            if "/search/code" in url:
                current_time = time.time()
                
                if current_time - _code_search_window_start > 60:
                    _code_search_count = 0
                    _code_search_window_start = current_time
                
                if _code_search_count >= 25:
                    wait_time = 60 - (current_time - _code_search_window_start)
                    if wait_time > 0:
                        print(f"[WAIT]  Code search throttle: waiting {int(wait_time)}s...")
                        time.sleep(wait_time + 1)
                        _code_search_count = 0
                        _code_search_window_start = time.time()
                
                elapsed = current_time - _last_code_search_time
                if elapsed < 2.5:
                    time.sleep(2.5 - elapsed)
                
                _last_code_search_time = time.time()
                _code_search_count += 1
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": GH_ACCEPT,
            "X-GitHub-Api-Version": GH_VERSION,
            "User-Agent": "gitrecombo-cli"
        }
        
        r = requests.get(url, headers=headers, params=params, timeout=30)
        
        # Record request with SearchPlanner
        if planner:
            planner.record_request(endpoint_type, dict(r.headers))
        
        # Check rate limit headers
        remaining = int(r.headers.get('X-RateLimit-Remaining', 1000))
        reset_time = int(r.headers.get('X-RateLimit-Reset', 0))
        limit = int(r.headers.get('X-RateLimit-Limit', 5000))
        
        # Show rate limit status periodically
        if remaining % 100 == 0 or remaining < 50:
            print(f"[INFO]  Rate limit: {remaining}/{limit} remaining")
        
        if r.status_code == 403 and "rate limit" in r.text.lower():
            if attempt < retry - 1:
                wait = max(reset_time - time.time(), 60)
                print(f"[WAIT]  Rate limit hit! Waiting {int(wait)}s before retry {attempt+2}/{retry}...")
                time.sleep(wait + 2)
                continue
            raise RuntimeError("GitHub rate limit exceeded after retries")
        
        # Preventive wait ONLY if really running low (2 or less)
        if remaining <= 2 and reset_time > 0:
            wait = reset_time - time.time()
            if wait > 0:
                print(f"[WARN]  Critical rate limit ({remaining}). Waiting {int(wait)}s...")
                time.sleep(wait + 2)
        
        r.raise_for_status()
        return r.json()
    
    raise RuntimeError("GitHub API request failed after retries")

def search_repos(query: str, per_page: int, token: str) -> List[Dict[str, Any]]:
    data = gh_get(f"{GH_API}/search/repositories", token, {
        "q": query, "sort": "stars", "order": "desc", "per_page": per_page
    })
    
    # DEBUG: Check what API returns
    total_count = data.get("total_count", 0)
    items_count = len(data.get("items", []))
    if total_count == 0 or items_count == 0:
        print(f"[DEBUG] API response: total_count={total_count}, items={items_count}")
        print(f"[DEBUG] Query was: {query[:100]}")
    
    out = []
    for it in data.get("items", [])[:per_page]:
        out.append({
            "full_name": it.get("full_name"),
            "html_url": it.get("html_url"),
            "description": it.get("description"),
            "language": it.get("language"),
            "license": (it.get("license") or {}).get("spdx_id"),
            "stargazers_count": it.get("stargazers_count"),
            "created_at": it.get("created_at"),
            "pushed_at": it.get("pushed_at"),
            "fork": it.get("fork", False),
            "forks_count": it.get("forks_count", 0),
        })
    return out

def search_code(q: str, token: str, per_page: int = 1) -> int:
    # Use SearchPlanner per rispettare i rate limits di GitHub
    data = gh_get(f"{GH_API}/search/code", token, {"q": q, "per_page": per_page}, use_planner=True)
    return int(data.get("total_count", 0) or 0)

def get_topics(owner: str, repo: str, token: str) -> List[str]:
    try:
        data = gh_get(f"{GH_API}/repos/{owner}/{repo}/topics", token)
        return data.get("names", []) or data.get("topics", []) or []
    except Exception:
        return []

def get_readme_text(owner: str, repo: str, token: str, max_chars: int, use_cache: bool = True) -> str:
    """Get README text with optional caching."""
    cache = get_repo_cache() if use_cache else None
    repo_full_name = f"{owner}/{repo}"
    
    # Try cache first
    if cache:
        cached = cache.get_readme(repo_full_name)
        if cached:
            return cached[:max_chars]
    
    try:
        data = gh_get(f"{GH_API}/repos/{owner}/{repo}/readme", token)
        content = data.get("content","")
        if content:
            import base64
            txt = base64.b64decode(content).decode("utf-8", errors="ignore")
            
            # Cache the result
            if cache:
                cache.cache_readme(repo_full_name, txt)
            
            return txt[:max_chars]
    except Exception:
        pass
    return ""

def has_ci(owner: str, repo: str, token: str) -> bool:
    try:
        gh_get(f"{GH_API}/repos/{owner}/{repo}/contents/.github/workflows", token)
        return True
    except Exception:
        return False

def has_tests(owner: str, repo: str, token: str) -> bool:
    """Check if repo has tests (uses 2 code_search calls)"""
    q1 = f"repo:{owner}/{repo} path:tests"
    q2 = f"repo:{owner}/{repo} filename:*test*"
    return (search_code(q1, token, 1) > 0) or (search_code(q2, token, 1) > 0)

def has_release(owner: str, repo: str, token: str) -> bool:
    try:
        gh_get(f"{GH_API}/repos/{owner}/{repo}/releases/latest", token)
        return True
    except Exception:
        return False

def has_manifest(owner: str, repo: str, token: str) -> bool:
    """Check if repo has manifest files (uses 1 code_search call)"""
    q = f"repo:{owner}/{repo} filename:pyproject.toml OR filename:package.json OR filename:Cargo.toml OR filename:go.mod"
    return search_code(q, token, 1) > 0

def author_rep(owner: str, token: str) -> float:
    try:
        data = gh_get(f"{GH_API}/users/{owner}", token)
        followers = max(0, int(data.get("followers", 0) or 0))
        import math
        return min(1.0, math.log10(followers + 1) / 3.0)
    except Exception:
        return 0.0

def extract_concepts(text: str, topk: int = 8) -> List[str]:
    text = re.sub(r"[^\w\s\-+#./]", " ", (text or "").lower())
    tokens = [t for t in re.split(r"\s+", text) if t and t not in STOP and not t.isdigit()]
    from collections import Counter
    cnt = Counter(tokens)
    bigrams = Counter()
    for i in range(len(tokens)-1):
        a,b = tokens[i], tokens[i+1]
        if a in STOP or b in STOP: continue
        bigrams[(a,b)] += 1
    phrases = [(" ".join(k), v*1.5) for k,v in bigrams.items() if v>=2]
    phrases += [(k, v) for k,v in cnt.items() if v>=2]
    phrases.sort(key=lambda x: x[1], reverse=True)
    out = []
    for p,_ in phrases:
        if len(out)>=topk: break
        if p not in out: out.append(p[:40])
    return out

def build_queries(topics: List[str], days: int, explore_longtail: bool, max_stars: Optional[int]) -> List[str]:
    date_cut = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    queries = []
    for t in topics:
        t = (t or "").strip()
        if not t:
            continue

        if t in PRESETS:
            # Use preset (already has pushed:>{date})
            base_core = PRESETS[t].format(date=date_cut).strip()
        else:
            # Use pushed: for activity-based search (more results than created:)
            # Wrap multi-word topics in quotes for phrase search
            topic_term = f'"{t}"' if ' ' in t else t
            base_core = f"pushed:>{date_cut} {topic_term} in:name,description,readme".strip()

        if explore_longtail:
            # Long-tail: only ceiling + quality signals (no floor to avoid contradiction)
            cap = max_stars if max_stars is not None else 20
            q = f"{base_core} stars:<{cap} forks:<2 fork:false archived:false has:license"
        else:
            # Standard: NO stars floor - let scoring do the filtering
            q = f"{base_core} has:license"

        queries.append(q)
    return queries

def discover(params: Dict[str, Any]) -> Dict[str, Any]:
    token = params["token"]
    topics = params["topics"]
    days = int(params.get("days", 21))
    # FIX: Gestisce sia lista che stringa per le licenze
    licenses_raw = params.get("licenses", "MIT,Apache-2.0,BSD-3-Clause")
    if isinstance(licenses_raw, list):
        licenses = set(s.strip() for s in licenses_raw if s.strip())
    else:
        licenses = set(s.strip() for s in licenses_raw.split(",") if s.strip())
    max_per_q = int(params.get("max", 12))
    explore_longtail = bool(params.get("explore_longtail", False))
    max_stars = params.get("max_stars")
    max_stars = int(max_stars) if max_stars is not None else None
    min_health = float(params.get("min_health", 0.0))
    require_ci = bool(params.get("require_ci", False))
    require_tests = bool(params.get("require_tests", False))
    authorsig = bool(params.get("authorsig", False))
    embed_provider = params.get("embed_provider")  # None/openai/sbert
    embed_model = params.get("embed_model", "text-embedding-3-small")
    embed_max_chars = int(params.get("embed_max_chars", 8000))
    goal = params.get("goal")
    weights = {
        "novelty": float(params.get("w_novelty", 0.40)),
        "health": float(params.get("w_health", 0.25)),
        "relevance": float(params.get("w_relevance", 0.20)),
        "author": float(params.get("w_author", 0.05)),
        "diversity": float(params.get("w_diversity", 0.10)),
    }

    queries = build_queries(topics, days, explore_longtail, max_stars)
    
    # DEBUG: Print generated queries
    print(f"\n[DEBUG] Generated {len(queries)} queries:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    print()

    # 1) Aggregate by novelty + license
    agg: Dict[str, Dict[str, Any]] = {}
    for q in queries:
        repos = search_repos(q, max_per_q, token)
        print(f"[DEBUG] Query returned {len(repos)} repos: {q[:60]}...")
        for r in repos:
            key = r["full_name"]
            r["novelty_score"] = novelty_score(r)
            lic = (r.get("license") or "").strip() if r.get("license") else ""
            if licenses and (not lic or lic not in licenses): continue
            if key not in agg or r["novelty_score"] > agg[key]["novelty_score"]:
                agg[key] = r

    candidates = sorted(agg.values(), key=lambda x: x["novelty_score"], reverse=True)
    probe_limit = int(params.get("probe_limit", 24))
    probe = candidates[:min(probe_limit, len(candidates))]

    # 2) Deep probes: topics, readme, health, author rep, concepts
    print(f"\n🔍 Analyzing {len(probe)} repositories...")
    texts, keys = [], []
    for idx, c in enumerate(probe, 1):
        owner, repo = c["full_name"].split("/", 1)
        print(f"[{idx}/{len(probe)}] {owner}/{repo}...", end=" ", flush=True)
        
        c["topics"] = get_topics(owner, repo, token)
        c["readme_excerpt"] = get_readme_text(owner, repo, token, embed_max_chars) if (embed_provider or goal) else ""
        ci = has_ci(owner, repo, token)
        ts = has_tests(owner, repo, token)
        rel = has_release(owner, repo, token)
        man = has_manifest(owner, repo, token)
        
        health = 0.25*(1 if ci else 0) + 0.25*(1 if ts else 0) + 0.25*(1 if rel else 0) + 0.25*(1 if man else 0)
        if require_ci and not ci: health = 0.0
        if require_tests and not ts: health = 0.0
        c["health_score"] = float(health)
        c["_drop"] = c["health_score"] < min_health
        
        print(f"health={health:.2f} ✓")
        
        c["author_rep"] = author_rep(owner, token) if authorsig else 0.0
        c["concepts"] = extract_concepts(c.get("readme_excerpt","") or (c.get("description") or ""), topk=8)
        if embed_provider or goal:
            texts.append((c.get("description") or "") + "\n" + (c.get("readme_excerpt") or ""))
            keys.append(c["full_name"])

    # 3) Embeddings (optional)
    vecs: Dict[str, List[float]] = {}
    goal_vec = None
    if embed_provider and texts:
        if embed_provider == "openai":
            from embeddings import OpenAIEmbedder as E
        else:
            from embeddings import SBertEmbedder as E
        emb = E(embed_model)
        enc = emb.embed(texts)
        vecs = {k:v for k,v in zip(keys, enc)}
    if goal and embed_provider:
        if embed_provider == "openai":
            from embeddings import OpenAIEmbedder as E
        else:
            from embeddings import SBertEmbedder as E
        goal_vec = E(embed_model).embed([goal])[0]

    def cosine(a, b):
        import math
        if not a or not b or len(a)!=len(b): return 0.0
        dot = sum(x*y for x,y in zip(a,b))
        na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
        if na==0 or nb==0: return 0.0
        return dot/(na*nb)

    for c in probe:
        rel = 0.0
        if goal_vec is not None and c["full_name"] in vecs:
            rel = cosine(vecs[c["full_name"]], goal_vec)
        c["relevance"] = float(rel)

    pool = [c for c in probe if not c.get("_drop")]
    selected: List[Dict[str, Any]] = []
    selected_vecs: List[List[float]] = []

    def score_item(it, diversity_bonus):
        return (weights["novelty"]*it.get("novelty_score",0.0) +
                weights["health"] *it.get("health_score",0.0)  +
                weights["relevance"]*it.get("relevance",0.0)   +
                weights["author"]  *it.get("author_rep",0.0)  +
                weights["diversity"]*diversity_bonus)

    while len(selected) < 6 and pool:
        best, best_s = None, -1
        for cand in pool:
            div = 0.0
            if selected_vecs and cand["full_name"] in vecs:
                sims = []
                for v in selected_vecs:
                    sims.append(cosine(vecs[cand["full_name"]], v))
                avg_sim = sum(sims)/len(sims) if sims else 0.0
                div = max(0.0, 1.0 - avg_sim)
            elif not selected_vecs:
                div = 1.0
            s = score_item(cand, div)
            cand["_score"] = s
            if s > best_s:
                best, best_s = cand, s
        if not best: break
        selected.append(best)
        if best["full_name"] in vecs:
            selected_vecs.append(vecs[best["full_name"]])
        pool.remove(best)
        if len(selected) >= 6: break

    if len(selected) < 3:
        selected = sorted([c for c in candidates if c in probe], key=lambda x: x["novelty_score"], reverse=True)[:3]

    sources = [{
        "name": s["full_name"],
        "url": s["html_url"],
        "license": s.get("license") or "N/A",
        "role": f"module ({s.get('language') or 'NA'})",
        "novelty_score": round(float(s.get("novelty_score", 0.0)), 4),
        "relevance": round(float(s.get("relevance", 0.0)), 4),
        "health_score": round(float(s.get("health_score", 0.0)), 4),
        "author_rep": round(float(s.get("author_rep", 0.0)), 4),
        "concepts": s.get("concepts", [])[:8],
        "gem_score": round(float(s.get("_score", 0.0)), 4),
    } for s in selected]

    nodes = [f"[{i+1}] {s['name']}" for i, s in enumerate(sources)]
    architecture_ascii = f"{'  →  '.join(nodes)}\n            ↓\n        [ Orchestrator ]"
    seed_commands = [
        "mkdir -p app/{core,modules,scripts}",
        "echo '# Out-of-scale seed' > README.md",
        "python -m venv .venv && source .venv/bin/activate || .venv\\Scripts\\activate",
        "pip install -U uv pip wheel"
    ]
    project_tree = ["app/","app/core/","app/modules/","app/scripts/bootstrap.sh","README.md"]
    why_it_works = [
        "Novelty + Health + Author signals + Semantic relevance elevate hidden gems.",
        "Diversity bonus avoids conceptual duplicates when embeddings are enabled.",
        "Permissive licensing keeps integration safe and fast."
    ]

    blueprint = {
        "title": "GitRecombo — Out‑of‑Scale Blueprint",
        "summary": "Recombination of recent GitHub innovations with long-tail exploration, health/reputation signals, and optional semantic relevance.",
        "sources": sources,
        "architecture_ascii": architecture_ascii,
        "seed_commands": seed_commands,
        "project_tree": project_tree,
        "why_it_works": why_it_works,
        "metrics": {
            "topics": topics, "days": days, "explore_longtail": explore_longtail,
            "probe_limit": probe_limit, "candidates": len(candidates), "probed": len(probe),
            "selected": len(selected), "weights": weights
        }
    }
    return blueprint
