import os
import time
import json
import requests
from datetime import datetime

# CONFIGURATION
API_KEY = "6d0250430525a180f1a43e07b93c9c4d"
# Update these with your actual platform UIDs
SQUAD = [
    {"uid": "2292013299", "label": "You", "platform": "PC"},
    {"uid": "1111111111", "label": "Friend One", "platform": "PC"}
]
JSON_FILE = "history.json"

def fetch_stats():
    scores = {}
    for p in SQUAD:
        url = f"https://api.apexlegendsstatus.com/bridge?version=5&platform={p['platform']}&uid={p['uid']}&auth={API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            scores[p['uid']] = int(data['global']['rank']['rankScore'])
        except Exception:
            scores[p['uid']] = 0  # Fallback to 0 if API fails
    return scores

def run_sync():
    new_scores = fetch_stats()
    history = json.load(open(JSON_FILE)) if os.path.exists(JSON_FILE) else []
    
    # Check if scores changed
    if not history or history[-1]['scores'] != new_scores:
        history.append({"timestamp": datetime.now().strftime("%H:%M"), "scores": new_scores})
        with open(JSON_FILE, "w") as f:
            json.dump(history, f, indent=2)
        
        # Git automated push
        os.system('git add history.json && git commit -m "Auto-update RP" && git push')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushed new data to GitHub.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No changes detected.")

while True:
    run_sync()
    time.sleep(60) # 1 minute interval