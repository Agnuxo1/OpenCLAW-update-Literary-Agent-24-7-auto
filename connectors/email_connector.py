"""
Email Connector — Zoho SMTP/IMAP Integration
=============================================
Sends notifications, status reports, and collaboration requests via email.
"""

import imaplib
import smtplib
import email
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from datetime import datetime

logger = logging.getLogger("OpenCLAW.Email")


class EmailConnector:
    """Send and receive emails via Zoho."""

    def __init__(self, address: str, password: str,
                 smtp_host: str = "smtp.zoho.eu", smtp_port: int = 465,
                 imap_host: str = "imap.zoho.eu", imap_port: int = 993):
        self.address = address
        self.password = password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.imap_host = imap_host
        self.imap_port = imap_port

    def send(self, to: str, subject: str, body: str,
             html: bool = False) -> bool:
        """Send an email."""
        try:
            msg = MIMEMultipart("alternative") if html else MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self.address
            msg["To"] = to

            if html:
                msg.attach(MIMEText(body, "plain"))
                msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.address, self.password)
                server.sendmail(self.address, [to], msg.as_string())

            logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_status_report(self, admin_email: str, report: str) -> bool:
        """Send agent status report to admin."""
        subject = f"[OpenCLAW] Agent Status - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        return self.send(admin_email, subject, report)

    def send_boot_notification(self, admin_email: str) -> bool:
        """Notify admin that the agent has started."""
        subject = "[OpenCLAW] Agent System ONLINE"
        body = (
            f"OpenCLAW Autonomous Agent started successfully.\n"
            f"Time: {datetime.now().isoformat()}\n"
            f"Status: All systems operational.\n\n"
            f"The agent will publish research, engage with collaborators, "
            f"and self-optimize on a continuous cycle.\n"
        )
        return self.send(admin_email, subject, body)

    def check_inbox(self, folder: str = "INBOX", limit: int = 10) -> List[Dict]:
        """Check recent emails in inbox."""
        messages = []
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port) as mail:
                mail.login(self.address, self.password)
                mail.select(folder)

                _, data = mail.search(None, "ALL")
                ids = data[0].split()

                for num in ids[-limit:]:
                    _, msg_data = mail.fetch(num, "(RFC822)")
                    raw = msg_data[0][1]
                    msg = email.message_from_bytes(raw)

                    messages.append({
                        "from": msg.get("From", ""),
                        "subject": msg.get("Subject", ""),
                        "date": msg.get("Date", ""),
                        "body": self._extract_body(msg),
                    })

        except Exception as e:
            logger.error(f"Failed to check inbox: {e}")

        return messages

    @staticmethod
    def _extract_body(msg) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        return part.get_payload(decode=True).decode("utf-8", errors="replace")
                    except Exception:
                        pass
        else:
            try:
                return msg.get_payload(decode=True).decode("utf-8", errors="replace")
            except Exception:
                pass
        return ""
