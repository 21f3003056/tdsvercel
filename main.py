from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data (store q-vercel-latency.json next to your main.py)
with open("q-vercel-latency.json") as f:
    data = json.load(f)

@app.post("/api/latency")
async def get_latency_metrics(req: Request):
    body = await req.json()
    regions = set(body["regions"])
    threshold = body["threshold_ms"]

    # filter only requested regions
    filtered = [r for r in data if r["region"] in regions]

    # Get metrics for each requested region
    result = {}
    for region in regions:
        region_data = [r for r in filtered if r["region"] == region]
        latency = [r["latency_ms"] for r in region_data]
        uptime = [r["uptime_pct"] for r in region_data]
        breaches = sum(l > threshold for l in latency)

        result[region] = {
            "avg_latency": float(np.mean(latency)),
            "p95_latency": float(np.percentile(latency, 95)),
            "avg_uptime": float(np.mean(uptime)),
            "breaches": breaches,
        }
    return result
