"""
Configuration for the Onboarding Automation system.

Supports two modes:
- DEMO mode (default): reads/writes a local CSV, "sends" email by rendering
  it to console + an .html file in outputs/. No credentials needed — great
  for demos and interviews.
- LIVE mode: reads/writes a Google Sheet and sends real email via SMTP
  (Gmail App Password or any SMTP provider).

Set MODE=live and fill in the other vars in a .env file to go live.
"""
import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional in demo mode


@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("MODE", "demo")  # "demo" or "live"

    # --- Data source (employee records + tracker) ---
    # demo mode:
    demo_csv_path: str = os.getenv("DEMO_CSV_PATH", "data/employees.csv")
    # live mode (Google Sheets):
    google_sheet_id: str = os.getenv("GOOGLE_SHEET_ID", "")
    google_service_account_json: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    sheet_tab_name: str = os.getenv("SHEET_TAB_NAME", "Employees")

    # --- Email sending ---
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    sender_name: str = os.getenv("SENDER_NAME", "People Team")

    # --- HR notification ---
    hr_notify_email: str = os.getenv("HR_NOTIFY_EMAIL", "hr@example.com")

    # --- Output (demo mode artifacts) ---
    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")

    @property
    def is_demo(self) -> bool:
        return self.mode.lower() != "live"


settings = Settings()
