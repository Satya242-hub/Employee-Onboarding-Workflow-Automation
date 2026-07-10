"""
Email service: renders Jinja2 templates and sends via SMTP (live) or
writes rendered .html files to outputs/ (demo).
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


class EmailService:
    def __init__(self, settings):
        self.settings = settings
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

    def render(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

    def send(self, to_email: str, subject: str, html_body: str, filename_hint: str = "email"):
        if self.settings.is_demo:
            out_path = Path(self.settings.output_dir) / f"{filename_hint}.html"
            out_path.write_text(html_body, encoding="utf-8")
            print(f"[DEMO] Would send to {to_email!r} | Subject: {subject!r}")
            print(f"[DEMO] Rendered email saved to {out_path}")
            return {"status": "demo_sent", "path": str(out_path)}

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.settings.sender_name} <{self.settings.smtp_user}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
            server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.sendmail(self.settings.smtp_user, [to_email], msg.as_string())

        return {"status": "sent"}
