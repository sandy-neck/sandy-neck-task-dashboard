"""
Email sender — wraps Claude's written email in a minimal container and sends it.
No template. Claude writes the email; this just delivers it.
"""
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


class EmailReporter:
    def __init__(self):
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ["SMTP_USERNAME"]
        self.smtp_pass = os.environ["SMTP_PASSWORD"]
        self.recipient = os.environ.get("REPORT_RECIPIENT", "goodvibes@sandyneckprovisions.com")
        self.sender_name = os.environ.get("REPORT_SENDER_NAME", "Alex (Sandy Neck Analytics)")

    def send(self, email_content: dict):
        subject = email_content.get("subject", "daily update")
        body_html = email_content.get("body", "")
        html = self._wrap(body_html)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
        msg["To"] = self.recipient
        msg.attach(MIMEText(html, "html"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(self.smtp_user, self.smtp_pass)
            server.sendmail(self.smtp_user, self.recipient, msg.as_string())

    def _wrap(self, body_html: str) -> str:
        """Minimal wrapper — readable in any email client, looks like a normal email."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background:#ffffff;">
<div style="max-width:620px; margin:0 auto; padding:32px 24px; font-family:{FONT_STACK}; font-size:15px; line-height:1.7; color:#1a1a1a;">
  <div style="font-size:11px; color:#999; letter-spacing:1px; text-transform:uppercase; margin-bottom:24px; padding-bottom:12px; border-bottom:1px solid #eee;">Sandy Neck Provisions · Daily</div>
  {body_html}
</div>
</body>
</html>"""
