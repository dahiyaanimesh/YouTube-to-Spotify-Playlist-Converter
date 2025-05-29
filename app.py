import os
import logging
from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify
from config.settings import config, Config
from services.youtube_service import YouTubeService
from services.spotify_service import SpotifyService
from utils.helpers import validate_youtube_url, generate_playlist_name, extract_artist_from_title

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Validate configuration
    try:
        Config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Initialize services
    youtube_service = YouTubeService()
    spotify_service = SpotifyService()
    
    @app.route('/')
    def index():
        """Home page."""
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        """Initiate Spotify OAuth flow."""
        try:
            auth_url = spotify_service.get_authorization_url()
            return redirect(auth_url)
        except Exception as e:
            logger.error(f"Spotify login error: {e}")
            flash('Failed to initiate Spotify login. Please try again.', 'error')
            return redirect(url_for('index'))
    
    @app.route('/callback')
    def callback():
        """Handle OAuth callback from Spotify."""
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.warning(f"OAuth error: {error}")
            flash('Authorization denied. Please try again.', 'error')
            return redirect(url_for('index'))
        
        if not code:
            flash('No authorization code received.', 'error')
            return redirect(url_for('index'))
        
        try:
            if spotify_service.get_access_token(code):
                user = spotify_service.get_current_user()
                session['spotify_user_id'] = user['id']
                session['spotify_user_name'] = user.get('display_name', user['id'])
                flash(f'Successfully logged in as {session["spotify_user_name"]}!', 'success')
            else:
                flash('Failed to authenticate with Spotify.', 'error')
        except Exception as e:
            logger.error(f"Callback error: {e}")
            flash('Authentication failed. Please try again.', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/logout')
    def logout():
        """Logout user."""
        session.clear()
        flash('Successfully logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/transfer', methods=['POST'])
    def transfer():
        """Transfer YouTube playlist to Spotify."""
        logger.info("=== TRANSFER REQUEST STARTED ===")
        
        # Check if user is authenticated
        logger.info(f"Session contents: {dict(session)}")
        if 'spotify_user_id' not in session:
            logger.warning("User not authenticated - redirecting to login")
            flash('Please login to Spotify first.', 'error')
            return redirect(url_for('index'))
        
        logger.info(f"User authenticated: {session.get('spotify_user_name')}")
        
        playlist_url = request.form.get('playlist_url', '').strip()
        custom_name = request.form.get('playlist_name', '').strip()
        
        logger.info(f"Playlist URL: {playlist_url}")
        logger.info(f"Custom name: {custom_name}")
        
        # Validate input
        if not playlist_url:
            logger.warning("No playlist URL provided")
            flash('Please provide a YouTube playlist URL.', 'error')
            return redirect(url_for('index'))
        
        if not validate_youtube_url(playlist_url):
            logger.warning(f"Invalid YouTube URL: {playlist_url}")
            flash('Invalid YouTube playlist URL.', 'error')
            return redirect(url_for('index'))
        
        logger.info("URL validation passed")
        
        try:
            # Extract playlist ID
            playlist_id = youtube_service.extract_playlist_id(playlist_url)
            logger.info(f"Extracted playlist ID: {playlist_id}")
            
            # Authenticate YouTube with API key (simpler for read-only access)
            if not youtube_service.authenticate():
                logger.error("YouTube authentication failed")
                flash('Failed to authenticate with YouTube. Please check your API configuration.', 'error')
                return redirect(url_for('index'))
            
            logger.info("YouTube authentication successful")
            
            # Get playlist info
            playlist_info = youtube_service.get_playlist_info(playlist_id)
            logger.info(f"Processing playlist: {playlist_info['title']} ({playlist_info['item_count']} items)")
            
            # Get videos
            videos = youtube_service.get_playlist_videos(playlist_id)
            logger.info(f"Retrieved {len(videos)} videos")
            
            if not videos:
                logger.warning("No videos found in playlist")
                flash('No videos found in the playlist.', 'warning')
                return redirect(url_for('index'))
            
            # Re-authenticate Spotify service using cached token
            auth_manager = spotify_service.get_auth_manager()
            token_info = auth_manager.cache_handler.get_cached_token()
            
            if token_info:
                logger.info("Using cached Spotify token")
                # Check if token needs refresh and refresh if necessary
                if auth_manager.is_token_expired(token_info):
                    logger.info("Token expired, refreshing...")
                    token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                
                import spotipy
                spotify_service.sp = spotipy.Spotify(auth_manager=auth_manager)
            else:
                logger.error("No cached Spotify token found")
                flash('Spotify session expired. Please login again.', 'error')
                return redirect(url_for('login'))
            
            # Create Spotify playlist
            playlist_name = custom_name or generate_playlist_name(playlist_info['title'])
            logger.info(f"Creating Spotify playlist: {playlist_name}")
            
            spotify_playlist = spotify_service.create_playlist(
                session['spotify_user_id'],
                playlist_name,
                description=f"Converted from YouTube playlist: {playlist_info['title']}"
            )
            logger.info(f"Created Spotify playlist: {spotify_playlist['id']}")
            
            # Search for tracks and collect results
            found_tracks = []
            failed_tracks = []
            
            logger.info("Starting track search...")
            for i, video in enumerate(videos):
                video_title = video['snippet']['title']
                channel_title = video['snippet']['channelTitle']
                
                logger.debug(f"Processing {i+1}/{len(videos)}: {video_title}")
                
                # Try to extract artist from title
                clean_title, artist = extract_artist_from_title(video_title)
                
                # Search on Spotify
                track_id = spotify_service.search_track(
                    clean_title, 
                    artist or channel_title
                )
                
                if track_id:
                    found_tracks.append(track_id)
                    logger.debug(f"Found: {video_title}")
                else:
                    failed_tracks.append(video_title)
                    logger.debug(f"Not found: {video_title}")
            
            logger.info(f"Track search complete: {len(found_tracks)} found, {len(failed_tracks)} failed")
            
            # Add tracks to playlist
            if found_tracks:
                logger.info("Adding tracks to Spotify playlist...")
                success = spotify_service.add_tracks_to_playlist(
                    spotify_playlist['id'], 
                    found_tracks
                )
                
                if success:
                    logger.info("Playlist creation successful!")
                    # Prepare results
                    results = {
                        'playlist_name': playlist_name,
                        'playlist_url': spotify_playlist['url'],
                        'total_videos': len(videos),
                        'found_tracks': len(found_tracks),
                        'failed_tracks': failed_tracks,
                        'success_rate': (len(found_tracks) / len(videos)) * 100
                    }
                    
                    return render_template('result.html', results=results)
                else:
                    logger.error("Failed to add tracks to playlist")
                    flash('Failed to add tracks to Spotify playlist.', 'error')
            else:
                logger.warning("No tracks found on Spotify")
                flash('No tracks could be found on Spotify.', 'warning')
                
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'An error occurred during conversion: {str(e)}', 'error')
        
        logger.info("=== TRANSFER REQUEST ENDED ===")
        return redirect(url_for('index'))
    
    @app.route('/status')
    def status():
        """API endpoint for application status."""
        # Check YouTube API availability
        youtube_available = False
        try:
            if Config.YOUTUBE_API_KEY and Config.YOUTUBE_API_KEY != 'your_youtube_api_key_here':
                # Test authentication
                test_yt = YouTubeService()
                youtube_available = test_yt.authenticate()
        except:
            youtube_available = False
            
        return jsonify({
            'status': 'healthy',
            'services': {
                'youtube': youtube_available,
                'spotify': spotify_service.sp is not None
            },
            'user_authenticated': 'spotify_user_id' in session
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG']) 