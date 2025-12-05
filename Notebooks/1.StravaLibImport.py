#1
# --- Cell A: Import libraries and set up global configs ---
!pip install flask pyngrok requests pandas > /dev/null

from flask import Flask, request,redirect,jsonify, render_template_string
from pyngrok import ngrok
import json, requests, time, pandas as pd
from datetime import datetime, timedelta
import re
import os

STRAVA_CLIENT_ID = "123456" ###Placeholder ID
STRAVA_CLIENT_SECRET = "abcde" ###Placeholder PAssword
REDIRECT_PATH = "/oauth_callback"
ngrok.set_auth_token("xyz123") ###Placeholder Token

# Initialize Flask app
app = Flask(__name__)
print("Libraries Loaded")
