import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# 1. Health Check
response = requests.get(f"{BASE_URL}/")
print("Health Check:", response.json())

# 2. Upload Files
files = [
    ('files', open('data/Elitz_JD.pdf', 'rb')),
    ('files', open('data/Python_dev.pdf', 'rb')),
    ('files', open('data/SrivatsavAuswin.pdf', 'rb')),
]

response = requests.post(f"{BASE_URL}/upload", files=files)
data = response.json()
session_id = data.get('session_id')  # Note: session_id might not be in response, check actual implementation
print(f"\nUploaded! Session ID: {session_id}")

# 3. Analyze
response = requests.post(f"{BASE_URL}/analyze/{session_id}")
results = response.json()
print(f"\nAnalysis Results:")
print(json.dumps(results, indent=2))

# 4. Download Reports
# Ranking Report
response = requests.get(f"{BASE_URL}/download/{session_id}/ranking-report")
with open('downloaded_ranking_report.pdf', 'wb') as f:
    f.write(response.content)
print("\n✅ Downloaded ranking report")

# XAI Report
response = requests.get(f"{BASE_URL}/download/{session_id}/xai-report")
with open('downloaded_xai_report.txt', 'wb') as f:
    f.write(response.content)
print("✅ Downloaded XAI report")

# 5. Cleanup (optional)
# response = requests.delete(f"{BASE_URL}/session/{session_id}")
# print(f"\n🗑️ Deleted session: {response.json()}")
