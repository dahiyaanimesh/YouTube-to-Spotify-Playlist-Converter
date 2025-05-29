import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def clean_title(title: str) -> str:
    """
    Clean up video/song titles for better matching.
    
    Args:
        title (str): Original title
        
    Returns:
        str: Cleaned title
    """
    if not title:
        return ""
    
    # Remove common patterns
    patterns_to_remove = [
        r'\(.*Official.*\)',  # Remove official tags
        r'\(.*Music.*Video.*\)',  # Remove music video tags
        r'\(.*Audio.*\)',  # Remove audio tags
        r'\(.*Lyric.*\)',  # Remove lyric tags
        r'\[.*\]',  # Remove anything in square brackets
        r'\|.*',  # Remove everything after pipe
        r'HD$',  # Remove HD at the end
        r'HQ$',  # Remove HQ at the end
        r'\d{4}',  # Remove years
        r'feat\..*',  # Remove featuring artists
        r'ft\..*',  # Remove featuring artists
        r'featuring.*',  # Remove featuring artists
    ]
    
    cleaned = title
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remove extra whitespace and clean up
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Remove common words that don't help with matching
    words_to_remove = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    words = cleaned.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove or len(words) <= 3]
    
    result = ' '.join(filtered_words)
    logger.debug(f"Cleaned title: '{title}' -> '{result}'")
    return result

def extract_artist_from_title(title: str) -> tuple:
    """
    Try to extract artist name from video title.
    
    Args:
        title (str): Video title
        
    Returns:
        tuple: (cleaned_title, artist_name)
    """
    # Common patterns for artist - song format
    patterns = [
        r'^(.+?)\s*-\s*(.+)$',  # Artist - Song
        r'^(.+?)\s*:\s*(.+)$',  # Artist : Song
        r'^(.+?)\s*by\s*(.+)$',  # Song by Artist
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title, re.IGNORECASE)
        if match:
            part1, part2 = match.groups()
            
            # Heuristic: shorter part is usually the artist
            if len(part1) < len(part2):
                return clean_title(part2), clean_title(part1)
            else:
                return clean_title(part1), clean_title(part2)
    
    # If no pattern matches, return the title without artist
    return clean_title(title), None

def calculate_match_confidence(youtube_title: str, spotify_title: str, spotify_artist: str = None) -> float:
    """
    Calculate confidence score for track matching.
    
    Args:
        youtube_title (str): Original YouTube title
        spotify_title (str): Spotify track title
        spotify_artist (str): Spotify artist name
        
    Returns:
        float: Confidence score (0.0 to 1.0)
    """
    if not youtube_title or not spotify_title:
        return 0.0
    
    # Clean titles for comparison
    yt_clean = clean_title(youtube_title).lower()
    sp_clean = spotify_title.lower()
    
    # Word-based matching
    yt_words = set(yt_clean.split())
    sp_words = set(sp_clean.split())
    
    if not yt_words or not sp_words:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(yt_words.intersection(sp_words))
    union = len(yt_words.union(sp_words))
    jaccard_score = intersection / union if union > 0 else 0.0
    
    # Bonus for artist name appearing in YouTube title
    artist_bonus = 0.0
    if spotify_artist:
        artist_clean = spotify_artist.lower()
        if artist_clean in yt_clean:
            artist_bonus = 0.2
    
    # Penalty for significant length difference
    length_penalty = 0.0
    length_ratio = min(len(yt_clean), len(sp_clean)) / max(len(yt_clean), len(sp_clean))
    if length_ratio < 0.5:
        length_penalty = 0.1
    
    confidence = jaccard_score + artist_bonus - length_penalty
    return min(1.0, max(0.0, confidence))

def format_duration(duration_str: str) -> str:
    """
    Format ISO 8601 duration to human readable format.
    
    Args:
        duration_str (str): ISO 8601 duration (e.g., "PT3M45S")
        
    Returns:
        str: Formatted duration (e.g., "3:45")
    """
    if not duration_str:
        return "Unknown"
    
    # Parse ISO 8601 duration
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return duration_str
    
    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def validate_youtube_url(url: str) -> bool:
    """
    Validate YouTube playlist URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid YouTube playlist URL
    """
    if not url:
        return False
    
    youtube_patterns = [
        r'youtube\.com/playlist\?list=',
        r'youtube\.com/watch\?.*list=',
        r'youtu\.be/.*list=',
        r'm\.youtube\.com/playlist\?list='
    ]
    
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)

def generate_playlist_name(youtube_title: str = None) -> str:
    """
    Generate a Spotify playlist name based on YouTube playlist title.
    
    Args:
        youtube_title (str): Original YouTube playlist title
        
    Returns:
        str: Generated playlist name
    """
    if youtube_title:
        # Clean up the title
        cleaned = re.sub(r'[^\w\s-]', '', youtube_title)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Limit length
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."
        
        return f"{cleaned} (from YouTube)"
    
    return "Converted from YouTube"

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst (List[Any]): List to chunk
        chunk_size (int): Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for cross-platform compatibility.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:252] + "..."
    
    return sanitized or "untitled" 