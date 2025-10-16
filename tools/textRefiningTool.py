import logging
import re

# List of common filler words and phrases to remove

FILLER_WORDS = [
    "um", "uh", "so", "actually", "basically",
    "i mean", "right", "well", "okay", "hmm", "ah", "er", "oh", "huh",
    "yeah", "alright", "got it", "maybe", "ok", "nice", "i see"
]
# Optional: common polite/empty phrases that don't affect meaning
POLITE_PHRASES = [
    "please", "thank you", "thank you very much", "kindly", "I think", "I guess", "in my opinion"
]

logger = logging.getLogger(__name__)

def textRefiningTool(text):
    """Tool to refine the text and remove any unnecessary information."""
    try:
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        # 1. Lowercase the text for uniformity
        text = text.lower()

        # 2. Remove filler words
        filler_pattern = r'\b(?:' + '|'.join(re.escape(w) for w in FILLER_WORDS) + r')\b'
        text = re.sub(filler_pattern, '', text, flags=re.IGNORECASE)

        # 3. Remove polite/empty phrases
        polite_pattern = r'\b(?:' + '|'.join(re.escape(word) for word in POLITE_PHRASES) + r')\b'
        text = re.sub(polite_pattern, '', text, flags=re.IGNORECASE)

        # 4. Remove repeated words (like "I I I am going")
        text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)

        # 5. Remove extra spaces and line breaks
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"Error refining transcript: {e}")