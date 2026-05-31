import os
import time
import json
import requests
from datetime import datetime

# CONFIGURATION
API_KEY = "6d0250430525a180f1a43e07b93c9c4d"
SQUAD = [
    {"uid": "2292013299", "label": "You", "platform": "PC"},
    {"uid": "1011944913282", "label": "Saywhat", "platform": "PC"},
    {"uid": "1012860147038", "label": "Talon", "platform": "PC"},
    {"uid": "1011877813719", "label": "Anubis", "platform": "PC"},
    {"uid": "2433485727", "label": "trevor", "platform": "PC"},       # Added trevor
    {"uid": "1004525474326", "label": "mamapunk", "platform": "PC"}   # Added mamapunk
]
JSON_FILE = "history.json"

def fetch_stats():
    scores = {}
    for p in SQUAD:
        url = f"https://api.apexlegendsstatus.com/bridge?version=5&platform={p['platform']}&uid={p['uid']}&auth={API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'global' in data and 'rank' in data['global']:
                scores[p['uid']] = int(data['global']['rank']['rankScore'])
        except Exception as e:
            print(f"Error fetching {p['label']}: {e}")
            pass 
    return scores

def run_sync():
    os.system('git stash && git pull origin master --rebase && git stash pop')
    
    new_scores = fetch_stats()
    
    if not new_scores:
        return

    history = []
    if os.path.exists(JSON_FILE) and os.path.getsize(JSON_FILE) > 0:
        try:
            with open(JSON_FILE, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    
    if not history or history[-1]['scores'] != new_scores:
        history.append({"timestamp": datetime.now().strftime("%m/%d %H:%M"), "scores": new_scores})
        with open(JSON_FILE, "w") as f:
            json.dump(history, f, indent=2)
        
        os.system('git add history.json && git commit -m "Auto-update RP" && git push origin master')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sync complete.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No changes.")

if __name__ == "__main__":
    print("Starting Apex Tracker...")
    while True:
        run_sync()
        time.sleep(60)