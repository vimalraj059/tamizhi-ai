def format_response(intent: str, content: str) -> str:
    if intent == "poetry":
        return content.strip()

    if intent == "history":
        return f"📜 தமிழ் வரலாறு:\n\n{content}"

    if intent == "explain":
        return f"🧠 விளக்கம்:\n\n{content}"

    return content
