import json
import time
import random
from datetime import datetime, timezone
import requests

LOGSTASH_URL = "http://localhost:5080"
NUM_RECORDS = 50

promotion_types = ["none", "percentage", "bundle", "clearance"]

def generate_record():
    base_price = round(random.uniform(500, 2000), 2)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        "client_ip": f"10.42.0.{random.randint(1, 255)}",
        "input_features": {
            "Base_Price": base_price,
            "Competitor_Price": round(base_price * random.uniform(0.9, 1.1), 2),
            "Inventory_Level": random.randint(0, 500),
            "Units_Sold_Past_7D": random.randint(0, 1000),
            "Promotion_Type": random.choice(promotion_types),
            "Discount_Pct": round(random.uniform(0, 30), 1),
            "Seasonal_Trend": round(random.uniform(0.8, 1.5), 2)
        },
        "predicted_price": round(base_price * random.uniform(0.85, 1.15), 2),
        "latency_ms": round(random.uniform(5.0, 45.0), 1),
        "http_status": 200
    }

def main():
    print(f"Seeding {NUM_RECORDS} predictions to {LOGSTASH_URL}...")
    for i in range(NUM_RECORDS):
        record = generate_record()
        try:
            response = requests.post(LOGSTASH_URL, json=record)
            if response.status_code == 200:
                print(f"[{i+1}/{NUM_RECORDS}] Successfully sent record.")
            else:
                print(f"[{i+1}/{NUM_RECORDS}] Failed with status: {response.status_code}")
        except Exception as e:
            print(f"Connection error: {e}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()