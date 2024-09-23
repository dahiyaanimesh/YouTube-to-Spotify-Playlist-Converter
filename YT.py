import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth

# YouTube OAuth setup
CLIENT_SECRETS_FILE = "E:\Projects\Playlists-change\client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Spotify credentials
SPOTIPY_CLIENT_ID = "ab1ca2eff3a84bc3a6635e1bc81e2bc8"
SPOTIPY_CLIENT_SECRET = "0ce39cc16b3b4385b30575547b5fdf4d"
SPOTIPY_REDIRECT_URI = "http://localhost:8080"

# Step 1: Authenticate to YouTube API
def authenticate_youtube_api():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

# Step 2: Extract playlist ID from the URL
def extract_playlist_id(playlist_url):
    match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube playlist URL")

# Step 3: Fetch all videos from the YouTube playlist (with pagination for large playlists)
def get_youtube_playlist_videos(youtube, playlist_id):
    videos = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        videos += response['items']
        request = youtube.playlistItems().list_next(request, response)
    return videos

# Clean up video titles for better matching
def clean_title(title):
    # Remove common patterns like "(Official Video)", "(Official Music Video)", etc.
    title = re.sub(r'\(.*Official.*\)', '', title)  # Remove official tags
    title = re.sub(r'\[.*\]', '', title)  # Remove anything in brackets
    title = re.sub(r'\s+', ' ', title).strip()  # Remove extra whitespace
    return title

# Step 4: Authenticate to Spotify API
def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope="playlist-modify-public"))
    return sp

# Step 5: Search for the track on Spotify
def search_spotify_track(sp, track_name):
    result = sp.search(q=track_name, type='track', limit=1)
    tracks = result['tracks']['items']
    if tracks:
        return tracks[0]['id']  # Return the Spotify track ID
    return None

# Step 6: Create a new Spotify playlist and return its URL
def create_spotify_playlist(sp, user_id, playlist_name):
    playlist = sp.user_playlist_create(user_id, playlist_name)
    playlist_url = playlist['external_urls']['spotify']  # Get the URL of the playlist
    print(f"Playlist created: {playlist_url}")
    return playlist['id']


# Step 7: Add tracks to the Spotify playlist
def add_tracks_to_spotify_playlist(sp, playlist_id, track_ids):
    sp.playlist_add_items(playlist_id, track_ids)

# Main flow
if __name__ == '__main__':
    # YouTube Authentication
    youtube = authenticate_youtube_api()

    # Get YouTube playlist URL from the user
    playlist_url = input("Enter YouTube playlist URL: ")

    # Extract playlist ID
    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print(e)
        exit()

    # Fetch YouTube playlist videos
    print("Fetching YouTube playlist videos...")
    videos = get_youtube_playlist_videos(youtube, playlist_id)

    # Spotify Authentication
    sp = authenticate_spotify()
    spotify_user_id = sp.me()['id']  # Get the current Spotify user's ID

    # Ask user for the Spotify playlist name
    playlist_name = input("Enter a name for your new Spotify playlist: ")

    # Create a new Spotify playlist
    spotify_playlist_id = create_spotify_playlist(sp, spotify_user_id, playlist_name)

    # Prepare list of track IDs for Spotify
    track_ids = []
    failed_tracks = []  # To log tracks that were not found on Spotify

    print("Searching for tracks on Spotify and adding them to your playlist...")
    for video in videos:
        original_title = video['snippet']['title']
        clean_video_title = clean_title(original_title)
        print(f"Searching for: {clean_video_title}")
        spotify_track_id = search_spotify_track(sp, clean_video_title)
        if spotify_track_id:
            track_ids.append(spotify_track_id)
        else:
            failed_tracks.append(original_title)  # Log the track that wasn't found

    # Add found tracks to the Spotify playlist
    if track_ids:
        add_tracks_to_spotify_playlist(sp, spotify_playlist_id, track_ids)
        print(f"Added {len(track_ids)} tracks to your Spotify playlist.")
    else:
        print("No tracks were found on Spotify.")

    # Log tracks that weren't found on Spotify
    if failed_tracks:
        print("\nThe following tracks couldn't be found on Spotify:")
        for failed_track in failed_tracks:
            print(f"- {failed_track}")
