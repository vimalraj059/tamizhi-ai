import os
from groq import Groq
from core.system_prompt import TAMIZHI_SYSTEM_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_tamizhi(user_question: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": TAMIZHI_SYSTEM_PROMPT},
            {"role": "user", "content": user_question}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()
