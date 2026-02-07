#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA API SERVER
System of Systems - Verified Computation Service

Endpoints:
    POST /api/query      - Process query through 9-stage pipeline
    POST /api/verify     - Verify a claim/statement
    POST /api/calculate  - Newton-verified calculation
    GET  /api/ledger     - Get provenance ledger
    GET  /api/stats      - System statistics
    GET  /api/health     - Health check
    
The constraint IS the instruction.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "adan_portable"))

from developer.forge import (
    Pipeline, PipelineResult, 
    Regime, RegimeType,
    TrustLabel, TrustLattice,
    NinaKnowledge, get_nina_knowledge
)

# Import Ollama status check
try:
    from developer.forge.ollama import get_nina_ollama
    ollama = get_nina_ollama()
except ImportError:
    ollama = None

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Nina",
    description="Newton Intelligence & Natural Assistant - Verified Computation Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline for each regime
pipelines: Dict[str, Pipeline] = {
    "factual": Pipeline(Regime.from_type(RegimeType.FACTUAL)),
    "mathematical": Pipeline(Regime.from_type(RegimeType.MATHEMATICAL)),
    "conversational": Pipeline(Regime.from_type(RegimeType.CONVERSATIONAL)),
}

# Knowledge system
knowledge = get_nina_knowledge()

# Stats
start_time = time.time()
query_count = 0
verify_count = 0
calc_count = 0


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    query: str
    regime: str = "factual"

class VerifyRequest(BaseModel):
    statement: str
    regime: str = "factual"

class CalculateRequest(BaseModel):
    expression: str

class QueryResponse(BaseModel):
    success: bool
    value: Any
    trust_label: str
    trace: List[Dict[str, Any]]
    bounds: Dict[str, Any]
    ledger_proof: Optional[Dict[str, Any]]
    elapsed_ms: float
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI."""
    ui_path = Path(__file__).parent / "app" / "index.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding='utf-8'))
    return HTMLResponse("<h1>Nina</h1><p>UI not found. Check /app/index.html</p>")


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the 9-stage verified pipeline.
    
    Returns:
        Answer = (v, π, trust-label, bounds-report, ledger-proof)
    """
    global query_count
    query_count += 1
    
    start = time.time()
    
    # Get appropriate pipeline
    regime = request.regime.lower()
    if regime not in pipelines:
        regime = "factual"
    
    pipeline = pipelines[regime]
    
    # Process through pipeline
    result = pipeline.process(request.query)
    
    elapsed = (time.time() - start) * 1000
    
    return QueryResponse(
        success=result.success,
        value=result.value,
        trust_label=result.trust_label.name,
        trace=result.trace.to_list(),
        bounds=result.bounds_report.to_dict(),
        ledger_proof=result.ledger_proof.to_dict() if result.ledger_proof else None,
        elapsed_ms=round(elapsed, 3),
        error=result.error
    )


@app.post("/api/verify")
async def verify_statement(request: VerifyRequest):
    """Verify a statement/claim."""
    global verify_count
    verify_count += 1
    
    start = time.time()
    
    # Use factual pipeline for verification
    pipeline = pipelines.get(request.regime, pipelines["factual"])
    
    # Wrap as verification query
    query = f"Verify: {request.statement}"
    result = pipeline.process(query)
    
    elapsed = (time.time() - start) * 1000
    
    return {
        "verified": result.value if isinstance(result.value, bool) else False,
        "trust_label": result.trust_label.name,
        "confidence": 1.0 if result.value else 0.0,
        "trace": result.trace.to_list(),
        "elapsed_ms": round(elapsed, 3),
        "error": result.error
    }


@app.post("/api/calculate")
async def calculate(request: CalculateRequest):
    """Newton-verified calculation."""
    global calc_count
    calc_count += 1
    
    start = time.time()
    
    # Use mathematical pipeline
    pipeline = pipelines["mathematical"]
    
    # Wrap as calculation query
    query = f"Calculate {request.expression}"
    result = pipeline.process(query)
    
    elapsed = (time.time() - start) * 1000
    
    return {
        "result": result.value,
        "expression": request.expression,
        "trust_label": result.trust_label.name,
        "verified": result.success and result.trust_label.name in ["TRUSTED", "VERIFIED"],
        "bounds": result.bounds_report.to_dict(),
        "elapsed_ms": round(elapsed, 3),
        "error": result.error
    }


@app.get("/api/ledger")
async def get_ledger(regime: str = "factual", limit: int = 50):
    """Get provenance ledger entries."""
    pipeline = pipelines.get(regime, pipelines["factual"])
    entries = pipeline.get_ledger()[-limit:]
    
    return {
        "regime": regime,
        "entries": entries,
        "count": len(entries),
        "total": len(pipeline.get_ledger())
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    uptime = time.time() - start_time
    
    kb_stats = knowledge.get_stats() if knowledge else {}
    ollama_status = ollama.get_status() if ollama else {"available": False}
    
    return {
        "uptime_seconds": round(uptime, 1),
        "queries": query_count,
        "verifications": verify_count,
        "calculations": calc_count,
        "total_requests": query_count + verify_count + calc_count,
        "knowledge": kb_stats,
        "ollama": ollama_status,
        "pipelines": list(pipelines.keys()),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health")
async def health():
    """Health check."""
    ollama_status = ollama.get_status() if ollama else {"available": False}
    
    return {
        "status": "healthy",
        "service": "nina",
        "version": "1.0.0",
        "knowledge_available": knowledge.is_available if knowledge else False,
        "ollama_available": ollama_status.get("available", False),
        "ollama_model": ollama_status.get("model", "none"),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/regimes")
async def list_regimes():
    """List available regimes."""
    return {
        "regimes": [
            {
                "name": name,
                "type": p.regime.regime_type.value,
                "description": p.regime.description,
                "ambiguity_tolerance": p.regime.ambiguity_tolerance,
                "distortion_threshold": p.regime.distortion_threshold
            }
            for name, p in pipelines.items()
        ]
    }


# Mount static files
static_path = Path(__file__).parent / "app" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ═══════════════════════════════════════════════════════════════════════════
    
    ███╗   ██╗██╗███╗   ██╗ █████╗ 
    ████╗  ██║██║████╗  ██║██╔══██╗
    ██╔██╗ ██║██║██╔██╗ ██║███████║
    ██║╚██╗██║██║██║╚██╗██║██╔══██║
    ██║ ╚████║██║██║ ╚████║██║  ██║
    ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
    
    Newton Intelligence & Natural Assistant
    Verified Computation Service
    
    ═══════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
