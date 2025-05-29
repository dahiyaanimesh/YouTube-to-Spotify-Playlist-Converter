import re
import logging
import ssl
import time
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import Config
import httplib2

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service class for YouTube API operations."""
    
    def __init__(self):
        self.youtube = None
        self.config = Config()
    
    def authenticate(self, use_oauth=False, request=None):
        """
        Authenticate with YouTube API with SSL error handling.
        
        Args:
            use_oauth (bool): Whether to use OAuth 2.0 (False = API key only)
            request: Flask request object for web-based OAuth flow
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        max_retries = 3
        for attempt in range(max_retries):
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
                        
                        # Build service with SSL handling
                        http = httplib2.Http(timeout=30)
                        self.youtube = build('youtube', 'v3', credentials=credentials, http=http)
                        return True
                else:
                    # Simple API key authentication for read-only operations
                    api_key = self.config.YOUTUBE_API_KEY
                    if not api_key:
                        logger.error("YouTube API key not configured")
                        return False
                    
                    # Build service with SSL error handling
                    http = httplib2.Http(timeout=30)
                    self.youtube = build('youtube', 'v3', developerKey=api_key, http=http)
                    logger.info("YouTube service initialized with API key")
                    return True
                    
            except (ssl.SSLError, OSError) as e:
                logger.warning(f"SSL/Network error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                    continue
                else:
                    logger.error(f"YouTube authentication failed after {max_retries} attempts due to SSL/network issues")
                    return False
            except Exception as e:
                logger.error(f"YouTube authentication failed: {str(e)}")
                return False
        
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
        Get basic information about a playlist with SSL error handling and fallback.
        
        Args:
            playlist_id (str): YouTube playlist ID
            
        Returns:
            dict: Playlist information
        """
        if not self.youtube:
            raise Exception("YouTube service not authenticated")
        
        try:
            # Use the fallback mechanism for SSL error handling
            response = self._execute_with_fallback(
                lambda: self.youtube.playlists().list(
                    part="snippet,contentDetails",
                    id=playlist_id
                )
            )
            
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
        except Exception as e:
            logger.error(f"Error fetching playlist info: {str(e)}")
            raise Exception(f"Failed to fetch playlist info: {str(e)}")
    
    def get_playlist_videos(self, playlist_id, max_results=None):
        """
        Fetch all videos from a YouTube playlist with pagination and SSL error handling.
        
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
        max_retries = 3
        
        try:
            while True:
                # Retry logic for each page request
                for attempt in range(max_retries):
                    try:
                        request = self.youtube.playlistItems().list(
                            part="snippet,contentDetails",
                            playlistId=playlist_id,
                            maxResults=min(50, max_results - total_fetched if max_results else 50),
                            pageToken=next_page_token
                        )
                        response = request.execute()
                        break  # Success, exit retry loop
                        
                    except (ssl.SSLError, OSError) as e:
                        logger.warning(f"SSL/Network error on attempt {attempt + 1} for playlist videos: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            raise Exception(f"Failed to fetch playlist videos after {max_retries} attempts due to SSL/network issues: {str(e)}")
                
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
        except Exception as e:
            logger.error(f"Error fetching playlist videos: {str(e)}")
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

    def _create_fallback_service(self):
        """Create a fallback YouTube service with alternative SSL settings."""
        try:
            api_key = self.config.YOUTUBE_API_KEY
            if not api_key:
                return None
            
            # Try with more permissive SSL settings
            import ssl
            import httplib2
            
            # Create HTTP client with relaxed SSL verification
            http = httplib2.Http(
                timeout=60,
                disable_ssl_certificate_validation=True  # More permissive for troubleshooting
            )
            
            # Build service with the alternative HTTP client
            youtube_fallback = build('youtube', 'v3', developerKey=api_key, http=http)
            logger.info("Created fallback YouTube service with relaxed SSL settings")
            return youtube_fallback
            
        except Exception as e:
            logger.warning(f"Failed to create fallback service: {e}")
            return None

    def _execute_with_fallback(self, request_func, *args, **kwargs):
        """Execute a YouTube API request with fallback on SSL errors."""
        max_retries = 3
        
        # First try with the main service
        for attempt in range(max_retries):
            try:
                request = request_func(*args, **kwargs)
                return request.execute()
                
            except (ssl.SSLError, OSError) as e:
                logger.warning(f"SSL/Network error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    logger.warning("Main service failed, trying fallback service...")
                    break
            except Exception as e:
                # For non-SSL errors, don't retry
                raise e
        
        # If main service fails, try fallback service
        fallback_service = self._create_fallback_service()
        if fallback_service:
            try:
                # Replace the service temporarily for this request
                original_service = self.youtube
                self.youtube = fallback_service
                request = request_func(*args, **kwargs)
                result = request.execute()
                self.youtube = original_service  # Restore original service
                logger.info("Fallback service succeeded")
                return result
            except Exception as e:
                self.youtube = original_service  # Restore original service
                logger.error(f"Fallback service also failed: {e}")
                raise e
        
        raise Exception("Both main and fallback services failed due to SSL/network issues") 