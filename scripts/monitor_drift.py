import argparse
import requests
import statistics
import sys
import os

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200/pricing-logs-*/_search")
MIN_SAMPLE_SIZE = 30
SIGMA_MULTIPLIER = 2.0

def fetch_prices(hours):
    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": f"now-{hours}h",
                    "lte": "now"
                }
            }
        },
        "size": 10000,
        "_source": ["predicted_price"]
    }
    try:
        response = requests.post(ES_URL, json=query, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        hits = response.json().get("hits", {}).get("hits", [])
        return [hit["_source"]["predicted_price"] for hit in hits]
    except Exception as e:
        print(f"Error querying Elasticsearch: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Monitor pricing drift")
    parser.add_argument("--dry-run", action="store_true", help="Run without triggering webhooks")
    args = parser.parse_args()

    print("Fetching trailing 24h baseline data...")
    baseline_prices = fetch_prices(24)
    
    if len(baseline_prices) < MIN_SAMPLE_SIZE:
        print(f"Insufficient baseline data ({len(baseline_prices)} < {MIN_SAMPLE_SIZE}). Exiting.")
        sys.exit(0)

    mu = statistics.mean(baseline_prices)
    sigma = statistics.stdev(baseline_prices) if len(baseline_prices) > 1 else 0

    print(f"Baseline (24h) - Mu: {mu:.2f}, Sigma: {sigma:.2f}")

    print("Fetching trailing 6h current window data...")
    current_prices = fetch_prices(6)
    
    if len(current_prices) < MIN_SAMPLE_SIZE:
        print(f"Insufficient current window data ({len(current_prices)} < {MIN_SAMPLE_SIZE}). Exiting.")
        sys.exit(0)

    current_mean = statistics.mean(current_prices)
    print(f"Current Window (6h) - Mean: {current_mean:.2f}")

    drift = abs(current_mean - mu)
    threshold = SIGMA_MULTIPLIER * sigma

    if drift > threshold:
        print(f"🚨 DRIFT DETECTED! Shift ({drift:.2f}) exceeds threshold ({threshold:.2f})")
        if args.dry_run:
            print("[Dry Run] Skipping Jenkins retrain webhook.")
        else:
            jenkins_url = os.getenv("JENKINS_URL")
            jenkins_token = os.getenv("JENKINS_RETRAIN_TOKEN")
            if jenkins_url and jenkins_token:
                print("Triggering Jenkins retrain pipeline...")
                try:
                    requests.post(f"{jenkins_url}?token={jenkins_token}")
                except Exception as e:
                    print(f"Failed to trigger Jenkins: {e}")
            else:
                print("Warning: Jenkins webhook URL or Token not set in environment.")

            import subprocess
            subprocess.run([sys.executable, "scripts/chatops_bot.py", f"🚨 DRIFT DETECTED: Price shift {drift:.2f} exceeded threshold {threshold:.2f}. Triggering Jenkins retrain pipeline!"])
    else:
        print("Status: Stable. No drift detected.")
if __name__ == "__main__":
    main()