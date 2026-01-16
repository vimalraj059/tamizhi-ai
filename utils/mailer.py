import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("TAMIZHI_EMAIL")
EMAIL_PASSWORD = os.getenv("TAMIZHI_EMAIL_PASSWORD")

def send_welcome_mail(to_email: str, name: str = "Tamizhi User"):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("❌ Email credentials missing")
        return

    msg = EmailMessage()
    msg["Subject"] = "✨ Welcome to Tamizhi – Tamil Intelligence System"
    msg["From"] = formataddr(("Tamizhi AI", EMAIL_ADDRESS))
    msg["To"] = to_email
    msg.set_content(f"""
வணக்கம் {name},

Tamizhi-க்கு உங்களை மனமார வரவேற்கிறோம் 💛

தமிழ் மொழி, வரலாறு, கவிதை, அறிவு – அனைத்திற்கும்
Tamizhi உங்கள் நம்பகமான துணை.

உங்கள் பயணம் இனிமையாக அமைய வாழ்த்துகள்!

– Tamizhi Team
""")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print("✅ Welcome email sent to", to_email)
    except Exception as e:
        print("❌ Mail send failed:", e)
