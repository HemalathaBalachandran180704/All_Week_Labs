import re

FILLER_WORDS = [
    "uh", "uhh", "um", "umm", "you know", "so", "ohhh", "like", "actually", "basically", "right"
]

def remove_fillers(text):
    """Remove filler words and extra spaces."""
    pattern = r"\b(" + "|".join(FILLER_WORDS) + r")\b"
    cleaned_text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    # Remove multiple spaces
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    return cleaned_text
