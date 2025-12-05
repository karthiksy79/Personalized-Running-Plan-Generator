#2
# --- Cell B: Flask server and Strava OAuth via ngrok ---


!pip install flask pyngrok requests --quiet

import json, requests, os
from flask import Flask, request, render_template_string
from pyngrok import ngrok

# --- Your Strava app credentials ---
STRAVA_CLIENT_ID = "123456"
STRAVA_CLIENT_SECRET = "abcde"
REDIRECT_PATH = "/oauth_callback"

app = Flask(__name__)

# --- Start ngrok tunnel ---
public_url = ngrok.connect(5000).public_url
print(f"🌍 Public URL: {public_url}")

# --- Redirect URI to add in Strava App settings ---
REDIRECT_URI = f"{public_url}{REDIRECT_PATH}"
print(f"📍 Redirect URI for Strava App: {REDIRECT_URI}")

# --- Authorization link for users ---
auth_link = (
    f"https://www.strava.com/oauth/authorize?"
    f"client_id={STRAVA_CLIENT_ID}&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&approval_prompt=force&scope=activity:read_all"
)
print(f"🔗 Authorize here: {auth_link}")

# -------------------------------------------------------------
#  Flask routes
# -------------------------------------------------------------

@app.route(REDIRECT_PATH)
def oauth_callback():
    """Handle OAuth token exchange and prompt for age input."""
    code = request.args.get("code")
    if not code:
        return "❌ Missing authorization code", 400

    # Exchange authorization code for tokens
    token_resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    ).json()

    if "access_token" not in token_resp:
        return f"❌ Error: {token_resp}"

    athlete = token_resp.get("athlete", {})
    athlete_id = athlete.get("id")
    access_token = token_resp["access_token"]
    refresh_token = token_resp["refresh_token"]
    expires_at = token_resp["expires_at"]

    # Try to get weight directly from athlete profile
    weight = athlete.get("weight")

    # --- Render HTML form for manual age input ---
    html_form = f"""
    <h2>Welcome, {athlete.get('firstname', 'Runner')}!</h2>
    <p>Your Strava ID: <b>{athlete_id}</b></p>
    <p>Detected Weight: <b>{weight or 'Not provided'}</b> kg</p>
    <form action="/save_age" method="POST">
        <input type="hidden" name="athlete_id" value="{athlete_id}">
        <input type="hidden" name="access_token" value="{access_token}">
        <input type="hidden" name="refresh_token" value="{refresh_token}">
        <input type="hidden" name="expires_at" value="{expires_at}">
        <input type="hidden" name="weight" value="{weight or ''}">
        <label>Enter your age (in years):</label>
        <input type="number" name="age" required min="10" max="100">
        <button type="submit">Submit and Save</button>
    </form>
    """
    return render_template_string(html_form)


@app.route("/save_age", methods=["POST"])
def save_age():
    """Save user’s age and tokens to tokens.json (safe append)."""
    athlete_id = request.form.get("athlete_id")
    access_token = request.form.get("access_token")
    refresh_token = request.form.get("refresh_token")
    expires_at = request.form.get("expires_at")
    age = int(request.form.get("age"))
    weight = request.form.get("weight")
    weight = float(weight) if weight else None

    # --- Load or create tokens.json safely ---
    try:
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tokens = {}

    # --- Append or update this athlete ---
    tokens[str(athlete_id)] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "age": age,
        "weight": weight,
    }

    # --- Write safely ---
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)

    return f"""
    <h2>✅ Data Saved Successfully!</h2>
    <p>Age: <b>{age}</b> years</p>
    <p>Weight: <b>{weight or 'Not provided'}</b> kg</p>
    <p>Tokens saved for athlete ID <b>{athlete_id}</b>.</p>
    <p>You can close this tab now.</p>
    """
    
#  Run Flask app via ngrok

app.run(port=5000)
