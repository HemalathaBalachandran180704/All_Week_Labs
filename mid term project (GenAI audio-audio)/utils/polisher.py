# import requests

# GEMINI_API_KEY = "AIzaSyCa7Oxs0QgpxkFgQZtYX9iuS53-uPPiZaA"
# GEMINI_ENDPOINT = "https://gemini.googleapis.com/v1beta2/predict"

# def polish_text(text):
#     """Send text to Gemini-2.5-flash model for polishing."""
#     headers = {
#         "Authorization": f"Bearer {GEMINI_API_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "model": "gemini-2.5-flash",
#         "input": text
#     }
#     response = requests.post(GEMINI_ENDPOINT, headers=headers, json=data)
#     if response.status_code != 200:
#         raise RuntimeError(f"Gemini API error: {response.text}")
#     result = response.json()
#     # The polished text should be in 'output_text' or similar field
#     polished_text = result.get("output_text", text)
#     return polished_text



# utils/polisher.py

def polish_text(text: str) -> str:
    """
    Simple local text polishing function.
    Removes extra spaces, trims text, capitalizes first letters of sentences.
    """
    import re

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Capitalize first letter after period
    def capitalize_sentences(match):
        return match.group(1) + match.group(2).upper()

    text = re.sub(r"([\.!?]\s+)([a-z])", capitalize_sentences, text)

    # Capitalize first letter of the text if needed
    if text:
        text = text[0].upper() + text[1:]

    return text
