from typing import Literal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import Settings


class NotificationService:
    @staticmethod
    def send_notification(user_email: str, subject: str, message: str, method: str = "email"):
        """
        Sends an email notification to the user.
        """
        if method == "email":
            try:
                # Set up the email server
                server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
                server.starttls()
                server.login(Settings.SMTP_USERNAME, Settings.SMTP_PASSWORD)

                # Create email message
                msg = MIMEMultipart()
                msg["From"] = Settings.EMAIL_FROM
                msg["To"] = user_email
                msg["Subject"] = subject
                msg.attach(MIMEText(message, "plain"))

                # Send email
                server.sendmail(Settings.EMAIL_FROM, user_email, msg.as_string())
                server.quit()

                print(f"Email sent to {user_email}")
                return {"status": "success", "message": "Email sent successfully"}

            except Exception as e:
                print(f"Error sending email: {str(e)}")
                return {"status": "error", "message": str(e)}

        elif method == "push":
            print(f"Sending Push Notification to {user_email} - Message: {message}")
            return {"status": "success", "message": "Push notification sent"}

        else:
            raise ValueError("Invalid notification method")
