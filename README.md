# YouTube to Spotify Playlist Converter

A web application that allows users to convert YouTube playlists to Spotify playlists seamlessly.

## Features

- 🎵 Convert YouTube playlists to Spotify playlists
- 🔐 Secure OAuth authentication for both YouTube and Spotify
- 🎨 Clean and modern web interface
- 📱 Responsive design
- ⚡ Fast and efficient playlist conversion
- 📊 Track matching statistics and failed conversions report

## Prerequisites

Before running this application, you need:

1. **Spotify Developer Account**
   - Create an app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Note down your Client ID and Client Secret
   - Set redirect URI to `http://localhost:8080/callback`

2. **Google Cloud Project**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download the client secret JSON file

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd youtube-to-spotify-converter
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:8080/callback
   FLASK_SECRET_KEY=your_secret_key
   GOOGLE_CLIENT_SECRETS_FILE=config/client_secret.json
   ```

5. **Add your Google OAuth credentials**
   - Place your `client_secret.json` file in the `config/` directory

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:5000`

3. **Convert your playlist**
   - Click "Login with Spotify" to authenticate
   - Enter a YouTube playlist URL
   - Click "Convert to Spotify"
   - Your new Spotify playlist will be created!

## Project Structure

```
youtube-to-spotify-converter/
├── app.py                 # Main Flask application
├── config/
│   ├── __init__.py
│   ├── settings.py        # Configuration settings
│   └── client_secret.json # Google OAuth credentials (not in repo)
├── services/
│   ├── __init__.py
│   ├── youtube_service.py # YouTube API integration
│   └── spotify_service.py # Spotify API integration
├── utils/
│   ├── __init__.py
│   └── helpers.py         # Utility functions
├── templates/
│   ├── base.html
│   ├── index.html
│   └── result.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── tests/
│   ├── __init__.py
│   ├── test_youtube_service.py
│   └── test_spotify_service.py
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment
├── runtime.txt          # Python version for deployment
└── README.md            # This file
```

## Deployment

### Heroku

1. **Create a Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set SPOTIPY_CLIENT_ID=your_client_id
   heroku config:set SPOTIPY_CLIENT_SECRET=your_client_secret
   heroku config:set SPOTIPY_REDIRECT_URI=https://your-app-name.herokuapp.com/callback
   heroku config:set FLASK_SECRET_KEY=your_secret_key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/) - Python library for Spotify Web API
- [Google API Python Client](https://github.com/googleapis/google-api-python-client) - YouTube Data API
- [Flask](https://flask.palletsprojects.com/) - Web framework