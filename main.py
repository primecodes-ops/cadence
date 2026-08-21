from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

app = FastAPI()


@app.get("/login")
def login():
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-top-read user-read-recently-played",
    }

    query_string = urlencode(params)

    redirect_url = f"https://accounts.spotify.com/authorize?{query_string}"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/callback")
def callback(code: str):
    response = httpx.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    result = response.json()
    return result
