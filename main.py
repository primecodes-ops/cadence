from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
from collections import Counter
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
    access_token = result["access_token"]

    # Returns user's top tracks
    top_tracks_response = httpx.get(
        "https://api.spotify.com/v1/me/top/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    top_tracks = top_tracks_response.json()

    # Returns user's top artists
    top_artists_response = httpx.get(
        "https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    top_artists = top_artists_response.json()
    # return top_tracks

    # Decade breakdown
    # Flat-list of all track decades and the most dominance decade
    decades_list = [
        f"{int(item['album']['release_date'][0:4]) // 10 * 10}s"
        for item in top_tracks["items"]
    ]

    decades = Counter(decades_list)
    top_decade = decades.most_common(1)

    return top_decade
