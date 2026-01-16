from passlib.context import CryptContext
from database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_user(username: str, password: str):
    db = get_db()
    cursor = db.cursor()

    hashed = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        db.commit()
        return True
    except:
        return False
    finally:
        db.close()

def authenticate_user(username: str, password: str):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    db.close()

    if not row:
        return False

    return verify_password(password, row[0])
