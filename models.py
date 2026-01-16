from datetime import datetime

class Chat:
    def __init__(self, chat_id, user, title, created_at=None):
        self.chat_id = chat_id
        self.user = user
        self.title = title
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "user": self.user,
            "title": self.title,
            "created_at": self.created_at
        }


class Message:
    def __init__(self, message_id, chat_id, role, content, created_at=None):
        self.message_id = message_id
        self.chat_id = chat_id
        self.role = role          # "user" or "assistant"
        self.content = content
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at
        }
