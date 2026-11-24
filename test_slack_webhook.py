"""
test_slack_webhook.py - Quick diagnostic script to verify Slack webhook connectivity.
"""

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

def run_slack_test():
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()

    print("\n" + "=" * 60)
    print(" SLACK WEBHOOK CONNECTIVITY TEST")
    print("=" * 60)

    if not webhook_url or "XXXX" in webhook_url:
        print("\n❌ No valid SLACK_WEBHOOK_URL found in ops-brain-spike/.env")
        print("\nTo fix:")
        print("1. Open (or create) ops-brain-spike/.env")
        print("2. Add: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/REAL/WEBHOOK")
        print("3. Re-run: python ops-brain-spike/test_slack_webhook.py")
        return 1

    print(f"Connecting to: {webhook_url[:35]}...")

    test_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 Just Sortd - Slack Connection Verified!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Your Slack webhook is *LIVE and connected* to Ops Brain.\nReady to dispatch task approvals and slip cascade alerts."
                }
            }
        ]
    }

    try:
        resp = requests.post(webhook_url, json=test_payload, timeout=8)
        if resp.status_code == 200:
            print("\n✅ SUCCESS! Check your Slack channel — the test card has landed.")
            return 0
        else:
            print(f"\n❌ Slack returned HTTP {resp.status_code}: {resp.text}")
            return 1
    except Exception as e:
        print(f"\n❌ Network error sending to Slack: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_slack_test())
