import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("ALERT_EMAIL")
PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")

def send_email(to, subject, message):
    msg = MIMEText(message)
    msg["From"] = SENDER
    msg["To"] = to
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        server.send_message(msg)

    print("✅ Email Sent to", to)
