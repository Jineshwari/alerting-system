import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SLACK_WEBHOOK_URL")
print("Loaded URL:", url)

payload = {"text": "✅ Slack webhook test message from Jineshwari!"}
response = requests.post(url, json=payload)

print("Status:", response.status_code, response.text)
