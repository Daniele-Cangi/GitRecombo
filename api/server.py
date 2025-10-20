from __future__ import annotations
import os, json
from fastapi import FastAPI, Body, UploadFile, File
from pydantic import BaseModel, Field
from ..discover import discover
from ..llm import load_schema, openai_recombine

# Carica variabili d'ambiente da file .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass  # dotenv non installato, usa variabili d'ambiente normali

app = FastAPI(title="GitRecombo API")

class DiscoverReq(BaseModel):
    topics: list[str] = Field(..., example=["vector-rust","mamba","gpu-kernel"])
    days: int = 21
    licenses: str = "MIT,Apache-2.0,BSD-3-Clause"
    max: int = 12
    explore_longtail: bool = False
    max_stars: int | None = None
    min_health: float = 0.0
    require_ci: bool = False
    require_tests: bool = False
    authorsig: bool = False
    probe_limit: int = 24
    embed_provider: str | None = None
    embed_model: str = "text-embedding-3-small"
    embed_max_chars: int = 8000
    goal: str | None = None
    w_novelty: float = 0.40
    w_health: float = 0.25
    w_relevance: float = 0.20
    w_diversity: float = 0.10
    w_author: float = 0.05
    token: str | None = None

class RecombineReq(BaseModel):
    goal: str
    sources: list[dict]
    model: str = "gpt-4.1-mini"

@app.post("/discover")
def api_discover(req: DiscoverReq):
    token = req.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        return {"error":"Missing token. Provide in body.token or env GITHUB_TOKEN."}
    params = req.dict()
    params["token"] = token
    bp = discover(params)
    return bp

@app.post("/recombine")
def api_recombine(req: RecombineReq):
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", "futures_kit.schema.json")
    out = openai_recombine(goal=req.goal, sources=req.sources, prompt_path=os.path.join(os.path.dirname(__file__), "..", "prompts", "futures_recombiner.prompt.txt"), schema=load_schema(schema_path), model=req.model)
    return out

@app.post("/run")
def api_run(req: DiscoverReq, goal: str = Body(...), model: str = Body("gpt-4.1-mini")):
    token = req.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        return {"error":"Missing token. Provide in body.token or env GITHUB_TOKEN."}
    params = req.dict()
    params["token"] = token
    bp = discover(params)
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", "futures_kit.schema.json")
    out = openai_recombine(goal=goal, sources=bp["sources"], prompt_path=os.path.join(os.path.dirname(__file__), "..", "prompts", "futures_recombiner.prompt.txt"), schema=load_schema(schema_path), model=model)
    return {"blueprint": bp, "futures": out}
