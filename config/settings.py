import os
import ssl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    ENV = os.getenv('FLASK_ENV', 'production')
    
    # Spotify API Configuration
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:5000/callback')
    SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'config/client_secret.json')
    YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'YouTube to Spotify Converter')
    DEFAULT_PLAYLIST_NAME = os.getenv('DEFAULT_PLAYLIST_NAME', 'Converted from YouTube')
    MAX_TRACKS_PER_REQUEST = 100  # Spotify API limit
    
    # SSL Configuration for network issues
    SSL_VERIFY = os.getenv('SSL_VERIFY', 'true').lower() == 'true'
    HTTP_TIMEOUT = int(os.getenv('HTTP_TIMEOUT', '30'))
    
    @staticmethod
    def get_ssl_context():
        """Get SSL context for handling SSL/TLS issues."""
        if Config.SSL_VERIFY:
            return ssl.create_default_context()
        else:
            # Create unverified context for development/troubleshooting
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
    
    @staticmethod
    def validate_config():
        """Validate that required configuration is present."""
        required_vars = [
            'SPOTIPY_CLIENT_ID',
            'SPOTIPY_CLIENT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var) == f'your_{var.lower()}_here':
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    ENV = 'testing'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 