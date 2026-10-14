import os
import sys
import requests

def send_alert(message):
    # Reads webhook from environment per security rules
    webhook_url = os.getenv("SLACK_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL environment variable missing.")
        sys.exit(1)

    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("ChatOps alert sent successfully.")
    except Exception as e:
        print(f"Failed to send alert: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chatops_bot.py 'Your alert message here'")
        sys.exit(1)
    send_alert(sys.argv[1])