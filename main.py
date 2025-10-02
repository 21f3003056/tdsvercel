from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data at startup
with open("q-vercel-latency.json") as f:
    data = json.load(f)

@app.post("/api/latency")
async def get_latency_metrics(req: Request):
    body = await req.json()
    regions = set(body["regions"])
    threshold = body["threshold_ms"]

    result = {}
    for region in regions:
        region_data = [r for r in data if r["region"] == region]
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]
        breaches = sum(l > threshold for l in latencies)
        if latencies and uptimes:
            result[region] = {
                "avg_latency": float(np.mean(latencies)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "avg_uptime": float(np.mean(uptimes)),
                "breaches": breaches
            }
        else:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
    return result
