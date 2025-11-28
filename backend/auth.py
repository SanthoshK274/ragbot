
import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from models import User
from db import SessionLocal
from dotenv import load_dotenv
import threading

load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')

# Helper to send OTP email asynchronously
def send_otp_email(email, otp):
    def _send():
        msg = MIMEText(f"Your RAGBot verification code is: {otp}")
        msg['Subject'] = 'RAGBot 2FA Verification'
        msg['From'] = SMTP_USER
        msg['To'] = email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [email], msg.as_string())
        except Exception as e:
            print(f"[ERROR] Failed to send OTP email: {e}")
    threading.Thread(target=_send, daemon=True).start()


# Helper to generate OTP
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# User registration
def register_user(email, password):
    db: Session = SessionLocal()
    if db.query(User).filter_by(email=email).first():
        db.close()
        return False, 'Email already registered.'
    password_hash = generate_password_hash(password)
    otp = generate_otp()
    user = User(email=email, password_hash=password_hash, is_verified=False, otp=otp)
    db.add(user)
    db.commit()
    db.close()
    send_otp_email(email, otp)
    return True, 'User registered. OTP sent.'

# User login
def login_user(email, password):
    db: Session = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        db.close()
        return False, 'Invalid credentials.'
    otp = generate_otp()
    user.otp = otp
    db.commit()
    db.close()
    send_otp_email(email, otp)
    return True, 'OTP sent to email.'

# Verify OTP
def verify_otp(email, otp):
    db: Session = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    print(f"[DEBUG] Verifying OTP for email: {email}")
    if user:
        print(f"[DEBUG] User found. DB OTP: {user.otp}, Provided OTP: {otp}")
        if user.otp == otp:
            user.is_verified = True
            user.otp = None
            db.commit()
            print(f"[DEBUG] OTP verified. is_verified set to {user.is_verified}")
            db.close()
            return True, '2FA verified.'
        else:
            print(f"[DEBUG] OTP mismatch.")
    else:
        print(f"[DEBUG] No user found for email: {email}")
    db.close()
    return False, 'Invalid OTP.'
