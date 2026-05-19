import smtplib
from email.message import EmailMessage

from fastapi import HTTPException, status

from .config import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)


def send_password_reset_email(to_email: str, reset_link: str, expires_minutes: int) -> None:
    """Send a password reset email using SMTP."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD or not SMTP_FROM_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP email configuration is missing",
        )

    message = EmailMessage()
    message["Subject"] = "Reset your Cardly password"
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = to_email
    message.set_content(
        "\n".join(
            [
                "You requested to reset your Cardly password.",
                "",
                f"Open this link to choose a new password: {reset_link}",
                "",
                f"This link expires in {expires_minutes} minutes.",
                "If you did not request this, you can ignore this email.",
            ]
        )
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
    except smtplib.SMTPException as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email",
        ) from exc
