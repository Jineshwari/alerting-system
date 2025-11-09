import os
import requests
from dotenv import load_dotenv


load_dotenv()
WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_alert(message):
    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    print("[alerting] Slack Response:", response.status_code, response.text)
