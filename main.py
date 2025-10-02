# api/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def telemetry_handler(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold_ms = payload.get("threshold_ms", 180)
    
    # Assume telemetry.json is bundled with deployment
    import os, json
    telemetry_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
    with open(telemetry_path, "r") as f:
        data = json.load(f)
    
    region_metrics = {}
    for region in regions:
        region_records = [rec for rec in data if rec["region"] == region]
        if not region_records:
            continue
        
        latencies = [rec["latency_ms"] for rec in region_records]
        uptimes = [rec.get("uptime", 1.0) for rec in region_records]
        breaches = sum(l > threshold_ms for l in latencies)
        
        region_metrics[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(breaches),
        }
    
    return JSONResponse(region_metrics)
