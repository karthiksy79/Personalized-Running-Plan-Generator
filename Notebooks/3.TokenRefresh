#3
# --- Cell C: Auto-refresh Strava tokens ---

import os
import json
import requests
from datetime import datetime

def refresh_strava_tokens():
    """Refresh all expired Strava tokens in tokens.json while keeping user info (age, weight)."""
    if not os.path.exists("tokens.json"):
        print("⚠️ No tokens.json found. Please authorize at least one user first.")
        return

    with open("tokens.json", "r") as f:
        try:
            tokens = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ tokens.json is corrupted. Please re-authorize users.")
            return

    updated = False
    for athlete_id, creds in tokens.items():
        try:
            expires_at = float(creds.get("expires_at", 0))
            if expires_at < datetime.now().timestamp():
                print(f"🔄 Refreshing expired token for athlete {athlete_id}...")

                r = requests.post(
                    "https://www.strava.com/oauth/token",
                    data={
                        "client_id": STRAVA_CLIENT_ID,
                        "client_secret": STRAVA_CLIENT_SECRET,
                        "grant_type": "refresh_token",
                        "refresh_token": creds["refresh_token"]
                    },
                    timeout=10
                )

                if r.status_code != 200:
                    print(f"❌ Error refreshing token for {athlete_id}: {r.text}")
                    continue

                new_creds = r.json()

                # Preserve existing user data (age, weight)
                age = creds.get("age")
                weight = creds.get("weight")

                tokens[athlete_id].update({
                    "access_token": new_creds["access_token"],
                    "refresh_token": new_creds["refresh_token"],
                    "expires_at": new_creds["expires_at"],
                    "age": age,
                    "weight": weight
                })
                updated = True
            else:
                remaining = int((expires_at - datetime.now().timestamp()) / 3600)
                print(f"✅ Token for athlete {athlete_id} still valid (~{remaining} h left).")

        except Exception as e:
            print(f"⚠️ Error refreshing token for athlete {athlete_id}: {e}")

    # Save back updated tokens
    if updated:
        with open("tokens.json", "w") as f:
            json.dump(tokens, f, indent=4)
        print("💾 All expired tokens refreshed and saved.")
    else:
        print("✅ No tokens required refreshing.")

#Run automatically before fetching activities

refresh_strava_tokens()
