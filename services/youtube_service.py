import re
import logging
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import Config

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service class for YouTube API operations."""
    
    def __init__(self):
        self.youtube = None
        self.config = Config()
    
    def authenticate(self, use_oauth=False, request=None):
        """
        Authenticate with YouTube API.
        
        Args:
            use_oauth (bool): Whether to use OAuth 2.0 (False = API key only)
            request: Flask request object for web-based OAuth flow
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            if use_oauth:
                # OAuth 2.0 flow for write operations
                flow = Flow.from_client_secrets_file(
                    self.config.GOOGLE_CLIENT_SECRETS_FILE,
                    scopes=self.config.YOUTUBE_SCOPES
                )
                
                if request:
                    # Web-based OAuth flow
                    flow.redirect_uri = request.url_root + 'youtube/callback'
                    authorization_url, _ = flow.authorization_url(prompt='consent')
                    return authorization_url
                else:
                    # Local OAuth flow (for development/testing)
                    flow.redirect_uri = 'http://localhost:8080'
                    flow.run_local_server(port=8080)
                    credentials = flow.credentials
                    
                    self.youtube = build('youtube', 'v3', credentials=credentials)
                    return True
            else:
                # Simple API key authentication for read-only operations
                api_key = self.config.YOUTUBE_API_KEY
                if not api_key:
                    logger.error("YouTube API key not configured")
                    return False
                
                self.youtube = build('youtube', 'v3', developerKey=api_key)
                logger.info("YouTube service initialized with API key")
                return True
                
        except Exception as e:
            logger.error(f"YouTube authentication failed: {str(e)}")
            return False
    
    def build_service_from_credentials(self, credentials):
        """Build YouTube service from existing credentials."""
        try:
            self.youtube = build('youtube', 'v3', credentials=credentials)
            return True
        except Exception as e:
            logger.error(f"Failed to build YouTube service: {str(e)}")
            return False
    
    def extract_playlist_id(self, playlist_url):
        """
        Extract playlist ID from YouTube URL.
        
        Args:
            playlist_url (str): YouTube playlist URL
            
        Returns:
            str: Playlist ID
            
        Raises:
            ValueError: If URL is invalid
        """
        if not playlist_url:
            raise ValueError("Playlist URL cannot be empty")
        
        # Pattern for YouTube playlist URLs
        patterns = [
            r"list=([a-zA-Z0-9_-]+)",  # Standard format
            r"playlist\?list=([a-zA-Z0-9_-]+)",  # Alternative format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, playlist_url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid YouTube playlist URL")
    
    def get_playlist_info(self, playlist_id):
        """
        Get basic information about a playlist.
        
        Args:
            playlist_id (str): YouTube playlist ID
            
        Returns:
            dict: Playlist information
        """
        if not self.youtube:
            raise Exception("YouTube service not authenticated")
        
        try:
            request = self.youtube.playlists().list(
                part="snippet,contentDetails",
                id=playlist_id
            )
            response = request.execute()
            
            if not response['items']:
                raise ValueError("Playlist not found")
            
            playlist = response['items'][0]
            return {
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'description': playlist['snippet']['description'],
                'item_count': playlist['contentDetails']['itemCount'],
                'channel_title': playlist['snippet']['channelTitle']
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise Exception(f"Failed to fetch playlist info: {str(e)}")
    
    def get_playlist_videos(self, playlist_id, max_results=None):
        """
        Fetch all videos from a YouTube playlist with pagination.
        
        Args:
            playlist_id (str): YouTube playlist ID
            max_results (int): Maximum number of videos to fetch (None for all)
            
        Returns:
            list: List of video items
        """
        if not self.youtube:
            raise Exception("YouTube service not authenticated")
        
        videos = []
        next_page_token = None
        total_fetched = 0
        
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - total_fetched if max_results else 50),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Filter out deleted/private videos
                valid_videos = [
                    item for item in response['items']
                    if item['snippet']['title'] != 'Deleted video' and
                       item['snippet']['title'] != 'Private video'
                ]
                
                videos.extend(valid_videos)
                total_fetched += len(valid_videos)
                
                next_page_token = response.get('nextPageToken')
                
                # Break if no more pages or reached max_results
                if not next_page_token or (max_results and total_fetched >= max_results):
                    break
            
            logger.info(f"Fetched {len(videos)} videos from playlist {playlist_id}")
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise Exception(f"Failed to fetch playlist videos: {str(e)}")
    
    def get_video_details(self, video_id):
        """
        Get detailed information about a specific video.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video details
        """
        if not self.youtube:
            raise Exception("YouTube service not authenticated")
        
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return None
            
            video = response['items'][0]
            return {
                'id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'channel_title': video['snippet']['channelTitle'],
                'duration': video['contentDetails']['duration'],
                'tags': video['snippet'].get('tags', [])
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return None 