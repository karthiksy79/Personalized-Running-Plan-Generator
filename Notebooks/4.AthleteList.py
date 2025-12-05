#4
# Cell D: List Authorized Strava Athletes

import json
import requests

# Load saved tokens
try:
    with open("tokens.json", "r") as f:
        tokens = json.load(f)
except FileNotFoundError:
    print("❌ tokens.json not found. Please authorize athletes first.")
    tokens = {}

if not tokens:
    print("⚠️ No authorized athletes found yet.")
else:
    print("✅ Authorized Athletes:\n")
    for athlete_id, creds in tokens.items():
        access_token = creds.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            # Fetch athlete profile from Strava API
            r = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
            if r.status_code == 200:
                athlete = r.json()
                name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip()
                print(f"🏃‍♂️  {name} (Athlete ID: {athlete_id})")
            elif r.status_code == 401:
                print(f"⚠️ Token expired or invalid for athlete ID {athlete_id}")
            else:
                print(f"❌ Error {r.status_code} for athlete ID {athlete_id}")
        except Exception as e:
            print(f"⚠️ Failed for athlete {athlete_id}: {e}")
