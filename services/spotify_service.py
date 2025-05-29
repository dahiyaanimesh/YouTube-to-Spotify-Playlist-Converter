import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from config.settings import Config
from utils.helpers import clean_title

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service class for Spotify API operations."""
    
    def __init__(self):
        self.sp = None
        self.config = Config()
    
    def get_auth_manager(self):
        """Get Spotify OAuth manager."""
        return SpotifyOAuth(
            client_id=self.config.SPOTIPY_CLIENT_ID,
            client_secret=self.config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=self.config.SPOTIPY_REDIRECT_URI,
            scope=self.config.SPOTIFY_SCOPE,
            cache_path=".cache"
        )
    
    def authenticate(self):
        """
        Authenticate with Spotify API.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            auth_manager = self.get_auth_manager()
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test the connection
            user = self.sp.current_user()
            logger.info(f"Authenticated as Spotify user: {user['display_name']} ({user['id']})")
            return True
            
        except Exception as e:
            logger.error(f"Spotify authentication failed: {str(e)}")
            return False
    
    def get_authorization_url(self):
        """Get Spotify authorization URL for OAuth flow."""
        auth_manager = self.get_auth_manager()
        return auth_manager.get_authorize_url()
    
    def get_access_token(self, code):
        """Exchange authorization code for access token."""
        try:
            auth_manager = self.get_auth_manager()
            token_info = auth_manager.get_access_token(code)
            self.sp = spotipy.Spotify(auth=token_info['access_token'])
            return True
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            return False
    
    def get_current_user(self):
        """
        Get current user information.
        
        Returns:
            dict: User information
        """
        if not self.sp:
            raise Exception("Spotify service not authenticated")
        
        try:
            return self.sp.current_user()
        except SpotifyException as e:
            logger.error(f"Failed to get current user: {str(e)}")
            raise Exception(f"Failed to get user info: {str(e)}")
    
    def search_track(self, query, artist=None, limit=1):
        """
        Search for a track on Spotify.
        
        Args:
            query (str): Search query (usually song title)
            artist (str): Artist name to improve search accuracy
            limit (int): Number of results to return
            
        Returns:
            str: Spotify track ID if found, None otherwise
        """
        if not self.sp:
            raise Exception("Spotify service not authenticated")
        
        try:
            # Clean the query
            clean_query = clean_title(query)
            
            # Build search query
            search_query = clean_query
            if artist:
                search_query += f" artist:{artist}"
            
            # Search for tracks
            results = self.sp.search(q=search_query, type='track', limit=limit)
            tracks = results['tracks']['items']
            
            if tracks:
                track = tracks[0]
                logger.debug(f"Found track: {track['name']} by {track['artists'][0]['name']}")
                return track['id']
            
            # If no results with artist, try without artist filter
            if artist:
                results = self.sp.search(q=clean_query, type='track', limit=limit)
                tracks = results['tracks']['items']
                if tracks:
                    track = tracks[0]
                    logger.debug(f"Found track (fallback): {track['name']} by {track['artists'][0]['name']}")
                    return track['id']
            
            logger.debug(f"No track found for query: {query}")
            return None
            
        except SpotifyException as e:
            logger.error(f"Spotify search error: {str(e)}")
            return None
    
    def create_playlist(self, user_id, name, description="", public=True):
        """
        Create a new Spotify playlist.
        
        Args:
            user_id (str): Spotify user ID
            name (str): Playlist name
            description (str): Playlist description
            public (bool): Whether playlist should be public
            
        Returns:
            dict: Playlist information including ID and URL
        """
        if not self.sp:
            raise Exception("Spotify service not authenticated")
        
        try:
            playlist = self.sp.user_playlist_create(
                user_id, 
                name, 
                public=public, 
                description=description
            )
            
            logger.info(f"Created playlist: {name} (ID: {playlist['id']})")
            return {
                'id': playlist['id'],
                'name': playlist['name'],
                'url': playlist['external_urls']['spotify'],
                'public': playlist['public']
            }
            
        except SpotifyException as e:
            logger.error(f"Failed to create playlist: {str(e)}")
            raise Exception(f"Failed to create playlist: {str(e)}")
    
    def add_tracks_to_playlist(self, playlist_id, track_ids):
        """
        Add tracks to a Spotify playlist.
        
        Args:
            playlist_id (str): Spotify playlist ID
            track_ids (list): List of Spotify track IDs
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.sp:
            raise Exception("Spotify service not authenticated")
        
        if not track_ids:
            logger.warning("No track IDs provided")
            return True
        
        try:
            # Spotify API allows max 100 tracks per request
            max_tracks = self.config.MAX_TRACKS_PER_REQUEST
            
            for i in range(0, len(track_ids), max_tracks):
                batch = track_ids[i:i + max_tracks]
                track_uris = [f"spotify:track:{track_id}" for track_id in batch]
                
                self.sp.playlist_add_items(playlist_id, track_uris)
                logger.debug(f"Added {len(batch)} tracks to playlist {playlist_id}")
            
            logger.info(f"Successfully added {len(track_ids)} tracks to playlist {playlist_id}")
            return True
            
        except SpotifyException as e:
            logger.error(f"Failed to add tracks to playlist: {str(e)}")
            return False
    
    def get_playlist_info(self, playlist_id):
        """
        Get information about a Spotify playlist.
        
        Args:
            playlist_id (str): Spotify playlist ID
            
        Returns:
            dict: Playlist information
        """
        if not self.sp:
            raise Exception("Spotify service not authenticated")
        
        try:
            playlist = self.sp.playlist(playlist_id)
            return {
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist['description'],
                'url': playlist['external_urls']['spotify'],
                'track_count': playlist['tracks']['total'],
                'public': playlist['public'],
                'owner': playlist['owner']['display_name']
            }
            
        except SpotifyException as e:
            logger.error(f"Failed to get playlist info: {str(e)}")
            return None
    
    def get_user_playlists(self, user_id, limit=50):
        """
        Get user's playlists.
        
        Args:
            user_id (str): Spotify user ID
            limit (int): Maximum number of playlists to return
            
        Returns:
            list: List of playlist information
        """
        if not self.sp:
            raise Exception("Spotify service not authenticated")
        
        try:
            results = self.sp.user_playlists(user_id, limit=limit)
            playlists = []
            
            for playlist in results['items']:
                playlists.append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'track_count': playlist['tracks']['total'],
                    'public': playlist['public'],
                    'url': playlist['external_urls']['spotify']
                })
            
            return playlists
            
        except SpotifyException as e:
            logger.error(f"Failed to get user playlists: {str(e)}")
            return [] 