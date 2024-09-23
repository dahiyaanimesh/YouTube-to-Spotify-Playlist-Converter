from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google_auth_oauthlib.flow import Flow
import os

app = Flask(__name__)
app.secret_key = 'some_random_secret_key'

# Spotify credentials
SPOTIPY_CLIENT_ID = os.getenv("ab1ca2eff3a84bc3a6635e1bc81e2bc8")
SPOTIPY_CLIENT_SECRET = os.getenv("0ce39cc16b3b4385b30575547b5fdf4d")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# YouTube OAuth settings (use environment variables for security)
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Home route
@app.route('/')
def index():
    return render_template('index.html')  # Create a simple HTML page with a form for the YouTube playlist URL

# Route to handle YouTube OAuth and Spotify integration
@app.route('/transfer', methods=['POST'])
def transfer():
    # You will need to adapt the existing YouTube and Spotify functionality here
    playlist_url = request.form['playlist_url']

    # Implement YouTube authentication
    youtube = authenticate_youtube_api()
    playlist_id = extract_playlist_id(playlist_url)
    videos = get_youtube_playlist_videos(youtube, playlist_id)
    
    # Implement Spotify authentication and track transfer logic
    sp = authenticate_spotify()
    spotify_user_id = sp.me()['id']
    
    playlist_name = "Your Playlist Transfer"
    spotify_playlist_id = create_spotify_playlist(sp, spotify_user_id, playlist_name)
    
    track_ids = []
    for video in videos:
        clean_title = clean_title(video['snippet']['title'])
        spotify_track_id = search_spotify_track(sp, clean_title)
        if spotify_track_id:
            track_ids.append(spotify_track_id)
    
    add_tracks_to_spotify_playlist(sp, spotify_playlist_id, track_ids)

    return f"Playlist created successfully! Check your Spotify account."

if __name__ == '__main__':
    app.run(debug=True)
