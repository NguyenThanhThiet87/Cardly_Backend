import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_PASSWORD_TOKEN_EXPIRE_MINUTES", 30))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
RESET_PASSWORD_URL = os.getenv("RESET_PASSWORD_URL", f"{FRONTEND_URL.rstrip('/')}/reset-password")

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Token expiry durations
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
RESET_PASSWORD_TOKEN_EXPIRE = timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)

# Bcrypt settings
BCRYPT_LOG_ROUNDS = 12
