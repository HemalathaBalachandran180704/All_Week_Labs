# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import TextFormatter

# def get_transcript(video_id):
#     """Return transcript text from YouTube video using video ID."""
#     try:
#         # Create an API instance
#         ytt_api = YouTubeTranscriptApi()
#         transcript_list = ytt_api.fetch(video_id)

#         # Format transcript as plain text
#         formatter = TextFormatter()
#         plain_text = formatter.format_transcript(transcript_list)

#         return plain_text
#     except Exception as e:
#         raise RuntimeError(f"Transcript error: {e}")




# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import TextFormatter
# import re

# def extract_video_id(youtube_url: str) -> str:
#     """Extract video ID from full YouTube URL."""
#     pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
#     match = re.search(pattern, youtube_url)
#     if not match:
#         raise ValueError("Invalid YouTube URL")
#     return match.group(1)

# def get_transcript(youtube_url: str) -> str:
#     """Return transcript text from YouTube video using the video ID."""
#     video_id = extract_video_id(youtube_url)
#     try:
#         ytt_api = YouTubeTranscriptApi()
#         transcript_list = ytt_api.fetch(video_id)
#         formatter = TextFormatter()
#         plain_text = formatter.format_transcript(transcript_list)
#         return plain_text
#     except Exception as e:
#         raise RuntimeError(f"Transcript error: {e}")



from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from full YouTube URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)

def get_transcript(youtube_url: str) -> str:
    """Return transcript text from YouTube video using the video ID."""
    video_id = extract_video_id(youtube_url)
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id)
        formatter = TextFormatter()
        plain_text = formatter.format_transcript(transcript_list)
        return plain_text
    except Exception as e:
        raise RuntimeError(f"Transcript error: {e}")
