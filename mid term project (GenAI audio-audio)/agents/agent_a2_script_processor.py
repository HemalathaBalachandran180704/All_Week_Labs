# from utils.transcriber import get_transcript
# from utils.filler_remover import remove_fillers
# from utils.polisher import polish_text

# class AgentA2ScriptProcessor:
#     def __init__(self):
#         pass  # No API key needed now

#     def process_youtube(self, video_id):
#         raw_text = get_transcript(video_id)      # works with video ID
#         no_fillers = remove_fillers(raw_text)
#         polished = polish_text(no_fillers)
#         return polished



from utils.transcriber import get_transcript
from utils.filler_remover import remove_fillers

def polish_text_with_gemini(raw_text: str) -> str:
    if not raw_text or not raw_text.strip():
        return ""
    try:
        from google import genai
        client = genai.Client(api_key="AIzaSyCa7Oxs0QgpxkFgQZtYX9iuS53-uPPiZaA")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"polish this raw transcript in a single line keeping it context aware and not dropping any sentences. "
                f"Output should only be the corrected script, nothing else. Raw transcript: {raw_text}"
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"[Gemini failed: {e}]"

class AgentA2ScriptProcessor:
    def __init__(self):
        pass  # No API key needed in constructor

    def process_youtube(self, youtube_url: str):
        raw_text = get_transcript(youtube_url)      # Accept full link now
        no_fillers = remove_fillers(raw_text)
        polished = polish_text_with_gemini(no_fillers)  # Use Gemini
        return polished
