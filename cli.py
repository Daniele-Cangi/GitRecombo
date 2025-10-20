from __future__ import annotations
import os, sys, json, argparse

# Fix imports for direct execution
try:
    from .discover import discover
    from .llm import load_schema, openai_recombine, ensure_valid
except ImportError:
    from discover import discover
    from llm import load_schema, openai_recombine, ensure_valid

from jinja2 import Template

# Carica variabili d'ambiente da file .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass  # dotenv non installato, usa variabili d'ambiente normali

def write_html(blueprint: dict, out_html: str):
    tpl_path = os.path.join(os.path.dirname(__file__), "templates", "onepage.html.j2")
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl = Template(f.read())
    html = tpl.render(**{
        "title": blueprint.get("title","GitRecombo Blueprint"),
        "summary": blueprint.get("summary",""),
        "sources": blueprint.get("sources", []),
        "architecture_ascii": blueprint.get("architecture_ascii",""),
        "seed_commands": blueprint.get("seed_commands", []),
        "project_tree": blueprint.get("project_tree", []),
        "why_it_works": blueprint.get("why_it_works", []),
    })
    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f: f.write(html)

def parse_topics(s: str):
    return [t.strip() for t in s.split(",") if t.strip()]

def main():
    ap = argparse.ArgumentParser(prog="gitrecombo", description="GitRecombo CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # discover
    d = sub.add_parser("discover", help="Run deterministic discovery")
    d.add_argument("--topics", required=True, help="comma-separated topics or presets")
    d.add_argument("--days", type=int, default=21)
    d.add_argument("--licenses", default="MIT,Apache-2.0,BSD-3-Clause")
    d.add_argument("--max", type=int, default=12)
    d.add_argument("--explore-longtail", action="store_true")
    d.add_argument("--max-stars", type=int)
    d.add_argument("--min-health", type=float, default=0.0)
    d.add_argument("--require-ci", action="store_true")
    d.add_argument("--require-tests", action="store_true")
    d.add_argument("--authorsig", action="store_true")
    d.add_argument("--probe-limit", type=int, default=24)

    d.add_argument("--embed-provider", choices=["openai","sbert"])
    d.add_argument("--embed-model", default="text-embedding-3-small")
    d.add_argument("--embed-max-chars", type=int, default=8000)
    d.add_argument("--goal")

    d.add_argument("--w-novelty", type=float, default=0.40)
    d.add_argument("--w-health", type=float, default=0.25)
    d.add_argument("--w-relevance", type=float, default=0.20)
    d.add_argument("--w-diversity", type=float, default=0.10)
    d.add_argument("--w-author", type=float, default=0.05)

    d.add_argument("--json")
    d.add_argument("--html")
    d.add_argument("--token", help="GitHub token (or env GITHUB_TOKEN)")

    # recombine
    r = sub.add_parser("recombine", help="LLM recombination to Futures Kit")
    r.add_argument("--goal", required=True)
    r.add_argument("--sources", required=True, help="path to blueprint.json (or sources JSON)")
    r.add_argument("--schema", default=os.path.join(os.path.dirname(__file__), "schemas", "futures_kit.schema.json"))
    r.add_argument("--prompt", default=os.path.join(os.path.dirname(__file__), "prompts", "futures_recombiner.prompt.txt"))
    r.add_argument("--model", default="gpt-4.1-mini")
    r.add_argument("--out", required=True)

    # run end-to-end
    e = sub.add_parser("run", help="discover + recombine")
    for arg in d._actions[1:]:  # copy discover args except help
        if arg.option_strings: e.add_argument(*arg.option_strings, **{k:getattr(arg, k) for k in ["dest","type","default"] if hasattr(arg,k)})
    e.add_argument("--model", default="gpt-4.1-mini")
    e.add_argument("--out", required=True)

    args = ap.parse_args()

    if args.cmd in ["discover","run"]:
        token = args.token or os.environ.get("GITHUB_TOKEN")
        if not token:
            print("[ERR] Missing token. Set --token or env GITHUB_TOKEN.", file=sys.stderr); sys.exit(2)
        params = vars(args).copy()
        params["token"] = token
        params["topics"] = parse_topics(args.topics)
        bp = discover(params)
        if args.json:
            os.makedirs(os.path.dirname(args.json), exist_ok=True)
            with open(args.json, "w", encoding="utf-8") as f: json.dump(bp, f, ensure_ascii=False, indent=2)
            print(f"[OK] blueprint → {args.json}")
        else:
            print(json.dumps(bp, ensure_ascii=False, indent=2))
        if args.html:
            write_html(bp, args.html)
            print(f"[OK] one‑page HTML → {args.html}")

        if args.cmd == "discover":
            return

        # for run: cascade to recombine
        sources = bp["sources"]
        schema = load_schema(os.path.join(os.path.dirname(__file__), "schemas", "futures_kit.schema.json"))
        out = openai_recombine(goal=args.goal, sources=sources, prompt_path=os.path.join(os.path.dirname(__file__), "prompts", "futures_recombiner.prompt.txt"), schema=schema, model=args.model)
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[OK] futures kit → {args.out}")

    elif args.cmd == "recombine":
        # read sources from blueprint.json or plain list
        with open(args.sources, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if "sources" in obj and isinstance(obj["sources"], list):
            sources = obj["sources"]
        else:
            sources = obj
        schema = load_schema(args.schema)
        out = openai_recombine(goal=args.goal, sources=sources, prompt_path=args.prompt, schema=schema, model=args.model)
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[OK] futures kit → {args.out}")
