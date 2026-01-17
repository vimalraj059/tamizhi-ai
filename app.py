import os
import uuid

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from gtts import gTTS

# GROQ
from groq import Groq

# Google OAuth
from auth_google import oauth

# DATABASE
from database import (
    create_tables,
    create_chat,
    get_user_chats,
    get_messages,
    save_message,
    get_chat,
    update_chat_title
)

# --------------------------------------------------
# APP INIT
# --------------------------------------------------
app = FastAPI(title="Tamizhi – Tamil Intelligence System")

# --------------------------------------------------
# DB INIT
# --------------------------------------------------
create_tables()

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
# app.add_middleware(
#     SessionMiddleware,
#     secret_key="tamizhi-super-secret"
# )

# --------------------------------------------------
# STATIC & TEMPLATES
# --------------------------------------------------
app.mount("/static", StaticFiles(directory="ui/static"), name="static")
templates = Jinja2Templates(directory="ui/templates")

# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# FIXED ADMIN LOGIN (TEMP)
# --------------------------------------------------
ADMIN_USERNAME = "tamizhi"
ADMIN_PASSWORD = "tamizhi@123"

# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# --------------------------------------------------
# MANUAL LOGIN
# --------------------------------------------------
@app.post("/login")
async def manual_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        res = RedirectResponse("/", status_code=302)
        res.set_cookie("user", username, httponly=True)
        return res

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password"}
    )

# --------------------------------------------------
# GOOGLE LOGIN
# --------------------------------------------------
@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    if not user:
        return RedirectResponse("/login")

    email = user.get("email")
    res = RedirectResponse("/", status_code=302)
    res.set_cookie("user", email, httponly=True)
    return res

# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.cookies.get("user")
    if not user:
        return RedirectResponse("/login")

    chats = get_user_chats(user)
    active_chat_id = chats[0]["id"] if chats else create_chat(user)
    messages = get_messages(active_chat_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "active_chat": {"id": active_chat_id},
            "messages": messages,
            "chats": chats
        }
    )

# --------------------------------------------------
# CREATE NEW CHAT
# --------------------------------------------------
@app.post("/chat/new")
async def new_chat(request: Request):
    user = request.cookies.get("user")
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    chat_id = create_chat(user)
    return {"chat_id": chat_id}

# --------------------------------------------------
# LOAD ALL USER CHATS
# --------------------------------------------------
@app.get("/chats")
async def chats(request: Request):
    user = request.cookies.get("user")
    if not user:
        return []

    rows = get_user_chats(user)
    return [
        {
            "chat_id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]

# --------------------------------------------------
# LOAD CHAT MESSAGES
# --------------------------------------------------
@app.get("/chat/{chat_id}")
async def load_chat(chat_id: int):
    rows = get_messages(chat_id)
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]

# --------------------------------------------------
# RENAME CHAT (MANUAL EDIT)
# --------------------------------------------------
@app.post("/chat/rename")
async def rename_chat(request: Request):
    data = await request.json()
    chat_id = data.get("chat_id")
    title = data.get("title", "").strip()

    if not chat_id or not title:
        return {"status": "error"}

    update_chat_title(chat_id, title)
    return {"status": "ok"}

# --------------------------------------------------
# 🔥 AI CHAT TITLE GENERATOR
# --------------------------------------------------
def generate_chat_title(user_message: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a short, clean chat title. "
                        "Maximum 4 words. No quotes. No emojis."
                    )
                },
                {
                    "role": "user",
                    "content": f"Create a chat title for: {user_message}"
                }
            ],
            timeout=10
        )

        title = completion.choices[0].message.content.strip()
        return title[:50]

    except Exception as e:
        print("❌ TITLE GEN ERROR:", e)
        return user_message[:40]

# --------------------------------------------------
# CHAT API (AI TITLE + SAVE HISTORY)
# --------------------------------------------------
@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "").strip()
    chat_id = data.get("chat_id")

    if not question or not chat_id:
        return {"answer": "Invalid request"}

    # Save user message
    save_message(chat_id, "user", question)

    # 🔥 AI TITLE (ONLY FIRST MESSAGE)
    chat = get_chat(chat_id)
    if chat and chat["title"] == "New Chat":
        smart_title = generate_chat_title(question)
        update_chat_title(chat_id, smart_title)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Tamizhi, a wise, calm Tamil AI assistant. "
                        "Respond naturally in Tamil. "
                        "If user asks in English, reply in Tamil."
                    )
                },
                {"role": "user", "content": question}
            ],
            timeout=15
        )

        answer = completion.choices[0].message.content.strip()

        # Save assistant message
        save_message(chat_id, "assistant", answer)

        return {"answer": answer}

    except Exception as e:
        print("❌ GROQ ERROR:", e)
        return {"answer": "⚠️ Tamizhi தற்போது பதிலளிக்க முடியவில்லை."}

# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
@app.get("/logout")
async def logout():
    res = RedirectResponse("/login", status_code=302)
    res.delete_cookie("user")
    return res

# --------------------------------------------------
# TEXT → VOICE
# --------------------------------------------------
@app.post("/text-to-voice")
async def text_to_voice(request: Request):
    data = await request.json()
    text = data.get("text", "").strip()

    if not text:
        return {"error": "No text provided"}

    audio_id = str(uuid.uuid4())
    mp3_path = f"voice_{audio_id}.mp3"

    tts = gTTS(text=text, lang="ta")
    tts.save(mp3_path)

    return FileResponse(
        mp3_path,
        media_type="audio/mpeg",
        filename="tamizhi_reply.mp3"
    )
