import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_document_email(recipient_email: str, pdf_bytes: bytes, filename: str = "Personal_Wishes_Document.pdf") -> tuple[bool, str]:
        if not settings.EMAIL_USERNAME or not settings.EMAIL_PASSWORD:
            logger.warning("Email credentials missing in configuration.")
            return False, "Email service is not configured. Please set EMAIL_USERNAME and EMAIL_PASSWORD in .env."

        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM or settings.EMAIL_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = "Your Draft Personal Wishes Document"

        body = """Hello,

Please find attached your generated Personal Wishes Document draft.

Disclaimer:
FICTIONAL DOCUMENT — NOT LEGAL ADVICE. This document is produced for demonstration purposes.

Best regards,
Document Intake Assistant Team
"""
        msg.attach(MIMEText(body, 'plain'))

        # Attach PDF
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(pdf_attachment)

        # Attempt 1: Standard STARTTLS (Port 587 or configured port)
        try:
            logger.info(f"Attempting SMTP connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=20)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True, f"Email successfully sent to {recipient_email}"
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"SMTP Auth error: {auth_err}")
            return False, "Authentication failed: Gmail requires a 16-character App Password (from myaccount.google.com/apppasswords) instead of your standard password."
        except Exception as e1:
            logger.warning(f"Port {settings.EMAIL_PORT} STARTTLS failed ({e1}). Attempting SMTP_SSL on Port 465...")

            # Attempt 2: Fallback to SSL (Port 465)
            try:
                server_ssl = smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, timeout=20)
                server_ssl.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
                server_ssl.send_message(msg)
                server_ssl.quit()
                return True, f"Email successfully sent to {recipient_email}"
            except smtplib.SMTPAuthenticationError as auth_err:
                return False, "Authentication failed: Gmail requires a 16-character App Password (from myaccount.google.com/apppasswords)."
            except Exception as e2:
                logger.error(f"Fallback SMTP_SSL also failed: {e2}")
                return False, f"Failed to send email: {str(e2)}. Please ensure Gmail App Password is configured."
