from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Returns: 'ta', 'en', or 'mixed'
    """
    try:
        lang = detect(text)
    except:
        return "mixed"

    # Tamil Unicode range check
    tamil_chars = sum(1 for ch in text if '\u0B80' <= ch <= '\u0BFF')
    ratio = tamil_chars / max(len(text), 1)

    if ratio > 0.3:
        return "ta"
    if lang == "en":
        return "en"
    return "mixed"
