from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


def send_email(subject, message):

    sender = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    recipient = current_app.config.get("FARM_NOTIFICATION_EMAIL")

    if not sender:
        print("EMAIL ERROR: MAIL_USERNAME is not configured.")
        return False

    if not password:
        print("EMAIL ERROR: MAIL_PASSWORD is not configured.")
        return False

    if not recipient:
        print("EMAIL ERROR: FARM_NOTIFICATION_EMAIL is not configured.")
        return False

    try:
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[recipient]
        )

        msg.body = message

        mail.send(msg)

        print(
            f"EMAIL SENT SUCCESSFULLY TO: {recipient}"
        )

        return True

    except Exception as error:

        print(f"EMAIL ERROR: {error}")

        return False