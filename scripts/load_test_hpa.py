#!/usr/bin/env python3
"""
HPA Load Generator: Sends concurrent requests to /api/predict to generate CPU load
for Horizontal Pod Autoscaler scaling validation.
"""
import concurrent.futures
import json
import time
import urllib.request
import urllib.error
import ssl

TARGET_URL = "https://pricing-staging.136.81.137.108.sslip.io/api/predict"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PAYLOAD = json.dumps({
    "Base_Price": 120.0,
    "Competitor_Price": 115.0,
    "Inventory_Level": 80,
    "Units_Sold_Past_7D": 150,
    "Discount_Pct": 12.0,
    "Seasonal_Trend": 1.25,
    "Promotion_Type": "percentage"
}).encode()

def send_request():
    try:
        req = urllib.request.Request(
            TARGET_URL,
            data=PAYLOAD,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            return res.status
    except Exception as exc:
        return str(exc)

def run_load(duration_sec=75, concurrency=25):
    print(f"Starting HPA load test against {TARGET_URL} (Duration: {duration_sec}s, Concurrency: {concurrency})...")
    start = time.time()
    total_reqs = 0
    errors = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        while time.time() - start < duration_sec:
            futures = [executor.submit(send_request) for _ in range(concurrency)]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                total_reqs += 1
                if res != 200:
                    errors += 1
            time.sleep(0.05)

    elapsed = time.time() - start
    print(f"Load test finished: {total_reqs} requests in {elapsed:.1f}s ({total_reqs/elapsed:.1f} req/s). Errors: {errors}")

if __name__ == "__main__":
    run_load()
