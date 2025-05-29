# YouTube to Spotify Playlist Converter

<div align="center">

![App Screenshot](https://via.placeholder.com/800x400/1a202c/ffffff?text=YouTube+to+Spotify+Converter)

*A modern web application that seamlessly converts YouTube playlists to Spotify playlists*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)

</div>

## 📸 Screenshots

### Home Page
![Home Page](https://via.placeholder.com/800x500/1a202c/ffffff?text=Home+Page+-+Convert+Your+Playlists)

### Conversion Results
![Results Page](https://via.placeholder.com/800x500/ffffff/1a202c?text=Conversion+Results+-+Success+Statistics)


## ✨ Features

- 🎵 **Smart Playlist Conversion** - Convert YouTube playlists to Spotify with intelligent track matching
- 🔐 **Secure Authentication** - OAuth 2.0 integration for both YouTube and Spotify
- 🎨 **Modern UI/UX** - Clean, responsive interface with beautiful animations
- 📱 **Mobile Friendly** - Fully responsive design that works on all devices
- ⚡ **Lightning Fast** - Efficient conversion with real-time progress tracking
- 📊 **Detailed Analytics** - Track matching statistics and comprehensive reports
- 🔍 **Advanced Matching** - Smart algorithms to find the best track matches
- 🎯 **High Success Rate** - Optimized matching for maximum conversion accuracy

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

1. **Spotify Developer Account**
   - Create an app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Note down your Client ID and Client Secret
   - Set redirect URI to `http://localhost:5000/callback`

2. **YouTube Data API Access**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create API key credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/youtube-to-spotify-converter.git
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
   ```env
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
   YOUTUBE_API_KEY=your_youtube_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

### Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to `http://localhost:5000`**

3. **Convert your playlist:**
   - Click "Login with Spotify" to authenticate
   - Paste a YouTube playlist URL
   - Optionally customize the playlist name
   - Click "Convert to Spotify"
   - Watch the magic happen! ✨

## 🏗️ Project Structure

```
youtube-to-spotify-converter/
├── 📁 app.py                    # Main Flask application
├── 📁 config/
│   ├── __init__.py
│   ├── settings.py              # Configuration settings
│   └── client_secret.json       # Google OAuth credentials (not in repo)
├── 📁 services/
│   ├── __init__.py
│   ├── youtube_service.py       # YouTube API integration
│   └── spotify_service.py       # Spotify API integration
├── 📁 utils/
│   ├── __init__.py
│   └── helpers.py               # Utility functions
├── 📁 templates/
│   ├── base.html                # Base template
│   ├── index.html               # Home page
│   ├── result.html              # Results page
│   └── error.html               # Error page
├── 📁 static/
│   ├── css/
│   │   └── style.css            # Custom styles
│   └── js/
│       └── main.js              # JavaScript functionality
├── 📁 tests/
│   ├── __init__.py
│   ├── test_youtube_service.py
│   └── test_spotify_service.py
├── 📄 .env.example              # Environment variables template
├── 📄 .gitignore               # Git ignore file
├── 📄 requirements.txt         # Python dependencies
├── 📄 Procfile                 # Heroku deployment
├── 📄 runtime.txt              # Python version for deployment
└── 📄 README.md                # This file
```

## 🚀 Deployment

### Heroku Deployment

1. **Create a Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set SPOTIPY_CLIENT_ID=your_client_id
   heroku config:set SPOTIPY_CLIENT_SECRET=your_client_secret
   heroku config:set SPOTIPY_REDIRECT_URI=https://your-app-name.herokuapp.com/callback
   heroku config:set YOUTUBE_API_KEY=your_youtube_api_key
   heroku config:set FLASK_SECRET_KEY=your_secret_key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Docker Deployment (Optional)

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **APIs:** Spotify Web API, YouTube Data API v3
- **Authentication:** OAuth 2.0
- **Deployment:** Heroku, Docker (optional)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/) - Spotify Web API Python library
- [Google API Python Client](https://github.com/googleapis/google-api-python-client) - YouTube Data API integration
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [Bootstrap](https://getbootstrap.com/) - CSS framework for responsive design



**Made with ❤️ by [Animesh](https://github.com/dahiyaanimesh)**

⭐ Star this repository if you find it helpful!

</div>