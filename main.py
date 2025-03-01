import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
from scraper import get_input_date, get_saturday_date, get_top_music
from datetime import date


# initialize Flask App
app = Flask(__name__)

# set the name of the session cookie
app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"

# set the secret key
app.secret_key = "your app secret key"
client_id = "your spotify client id"
client_secret = "your spotify client secret"
user_id = "your spotify user id"

# set the key for the token info in the session dictionary
TOKEN_INFO = "token_info"


@app.route("/")
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)


@app.route("/redirect")
def redirect_page():
    session.clear()
    code = request.args.get("code")
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("main"))


@app.route("/main")
def main():
    input_date = get_input_date()
    saturday_date = get_saturday_date(
        date(input_date.year, input_date.month, input_date.day)
    )
    top_music = get_top_music(saturday_date)
    track_uris: list = []

    token = get_token()
    sp = spotipy.Spotify(auth=token["access_token"])

    playlist_id = create_playlist(
        sp,
        f"{saturday_date} Top 100 Music on Billboard",
        "Generated by Musical Time Machine",
    )

    for track in top_music:
        track_info = f"{track.title} {track.artist}"
        track_uris.append(search_track(sp, track_info))

    sp.user_playlist_add_tracks(user_id, playlist_id, track_uris, None)

    return "Musical Time Machine Successfully Created!"


def create_playlist(sp, name: str, desc: str) -> str:
    playlist = sp.user_playlist_create(user_id, name, description=desc)
    return playlist["id"]


def search_track(sp, search_query: str) -> str:
    results = sp.search(q=f"{search_query}", type="track")
    return results["tracks"]["items"][0]["uri"]


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for("login", _external=False))

    now = int(time.time())
    if token_info["expires_at"] - now < 60:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info["refresh_token"])

    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for("redirect_page", _external=True),
        scope=[
            "user-read-private",
            "playlist-modify-public",
            "playlist-modify-private",
        ],
    )


if __name__ == "__main__":
    app.run(debug=True)
