from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

data_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(data_path) as f:
    data = json.load(f)

@app.post("/")
async def latency_metrics(req: Request):
    body = await req.json()
    regions = set(body["regions"])
    threshold = body["threshold_ms"]
    result = {}
    for region in regions:
        rows = [r for r in data if r["region"] == region]
        lats = [r["latency_ms"] for r in rows]
        ups = [r["uptime_pct"] for r in rows]
        result[region] = {
            "avg_latency": float(np.mean(lats)) if lats else None,
            "p95_latency": float(np.percentile(lats, 95)) if lats else None,
            "avg_uptime": float(np.mean(ups)) if ups else None,
            "breaches": sum(l > threshold for l in lats)
        }
    return result
