import os
import time
import json
import requests
import subprocess
from datetime import datetime

# CONFIGURATION
API_KEY = "6d0250430525a180f1a43e07b93c9c4d"
SQUAD = [
    {"uid": "2292013299", "label": "You", "platform": "PC"},
    {"uid": "1011944913282", "label": "Saywhat", "platform": "PC"},
    {"uid": "1012860147038", "label": "Talon", "platform": "PC"},
    {"uid": "1011877813719", "label": "Anubis", "platform": "PC"},
    {"uid": "2433485727", "label": "trevor", "platform": "PC"},
    {"uid": "76561198322670382", "label": "stunninggunner", "platform": "PC"},
    {"uid": "1007818122992", "label": "Zilch", "platform": "PC"},
    {"uid": "1007823821914", "label": "Ryu", "platform": "PC"},
    {"uid": "1004525474326", "label": "mamapunk", "platform": "PC"}
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
        except Exception:
            pass 
    return scores

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_sync():
    run_cmd('git stash && git pull origin master --rebase && git stash pop')
    
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
    
    # --- PER-PLAYER FILTERING ---
    # Find the absolute last known score for EVERY individual player across history
    last_known_scores = {}
    for entry in history:
        for uid, score in entry.get("scores", {}).items():
            last_known_scores[uid] = score

    # Only include players whose scores have ACTUALLY changed compared to their last known score
    filtered_scores = {}
    for uid, current_score in new_scores.items():
        last_score = last_known_scores.get(uid)
        if last_score is None or current_score != last_score:
            filtered_scores[uid] = current_score

    # If at least one player had a score change, save the filtered payload
    if filtered_scores:
        history.append({"timestamp": datetime.now().strftime("%m/%d %H:%M"), "scores": filtered_scores})
        
        with open(JSON_FILE, "w") as f:
            json.dump(history, f, indent=2)
        
        run_cmd('git add history.json && git commit -m "Auto-update RP" && git push origin master')
        print(f"[{datetime.now().strftime('%m/%d %H:%M:%S')}] Sync complete. Logged changes for UIDs: {list(filtered_scores.keys())}")
    else:
        print(f"[{datetime.now().strftime('%m/%d %H:%M:%S')}] No changes.")

if __name__ == "__main__":
    print("Starting Apex Tracker... (Running silently)")
    while True:
        run_sync()
        time.sleep(60)