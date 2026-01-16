def detect_intent(text: str) -> str:
    text = text.lower()

    greetings = ["hi", "hello", "vanakkam", "வணக்கம்"]
    poetry = ["kavithai", "கவிதை", "poem"]
    history = ["history", "வரலாறு"]
    explain = ["explain", "explanation", "விளக்கம்"]

    if any(word in text for word in greetings):
        return "greeting"

    if any(word in text for word in poetry):
        return "poetry"

    if any(word in text for word in history):
        return "history"

    if any(word in text for word in explain):
        return "explain"

    return "unknown"
