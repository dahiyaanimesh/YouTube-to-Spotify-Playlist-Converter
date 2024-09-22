import re
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth

# OAuth setup
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def authenticate_youtube_api():
    # OAuth flow to authenticate the app and get credentials
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def extract_playlist_id(playlist_url):
    # Use a regex to extract the playlist ID from the YouTube URL
    match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube playlist URL")

def get_youtube_playlist_videos(youtube, playlist_id):
    # Fetch the playlist items (videos) from the specified playlist ID
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50  # Adjust maxResults if needed
    )
    response = request.execute()
    return response['items']

# Main flow
if __name__ == '__main__':
    # Step 1: Authenticate to YouTube API
    youtube = authenticate_youtube_api()

    # Step 2: Get playlist URL from the user
    playlist_url = input("Enter YouTube playlist URL: ")

    # Step 3: Extract playlist ID from URL
    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print(e)
        exit()

    # Step 4: Fetch playlist videos
    videos = get_youtube_playlist_videos(youtube, playlist_id)

    # Step 5: Print video titles (you can modify this to work with Spotify API next)
    for video in videos:
        title = video['snippet']['title']
        print(f"Video Title: {title}")
