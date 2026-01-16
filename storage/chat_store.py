import json
import os
import uuid
from datetime import datetime

DATA_DIR = "storage/data"

os.makedirs(DATA_DIR, exist_ok=True)

def _user_file(user):
    return os.path.join(DATA_DIR, f"{user}.json")


def load_user_chats(user):
    file = _user_file(user)
    if not os.path.exists(file):
        return []

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_chats(user, chats):
    with open(_user_file(user), "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)


def create_new_chat(user):
    chats = load_user_chats(user)

    chat = {
        "id": str(uuid.uuid4()),
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().isoformat()
    }

    chats.insert(0, chat)
    save_user_chats(user, chats)
    return chat


def load_messages(chat_id):
    for user_file in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, user_file), "r", encoding="utf-8") as f:
            chats = json.load(f)
            for chat in chats:
                if chat["id"] == chat_id:
                    return chat["messages"]
    return []


def add_message(user, chat_id, role, content):
    chats = load_user_chats(user)

    for chat in chats:
        if chat["id"] == chat_id:
            chat["messages"].append({
                "role": role,
                "content": content,
                "time": datetime.now().isoformat()
            })
            break

    save_user_chats(user, chats)
