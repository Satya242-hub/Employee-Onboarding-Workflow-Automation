"""
Employee Onboarding Email Automation
=====================================

Flow:
  New employee record (pending) -> Generate welcome email -> Send welcome
  email -> Update onboarding tracker -> Notify HR

Run:
  python main.py                # demo mode, uses data/employees.csv
  MODE=live python main.py      # live mode, uses Google Sheets + SMTP

This script is idempotent: employees already marked "sent" are skipped,
so it's safe to run on a schedule (cron / Cloud Scheduler / GitHub Actions).
"""
from datetime import datetime, timezone

from config import settings
from services.data_source import get_data_source
from services.email_service import EmailService


def run():
    print(f"--- Onboarding automation run started ({settings.mode.upper()} mode) ---")

    data_source = get_data_source(settings)
    email_service = EmailService(settings)

    pending = data_source.get_pending_employees()
    if not pending:
        print("No pending employees found. Nothing to do.")
        return

    print(f"Found {len(pending)} pending employee(s).")
    processed = []

    for employee in pending:
        print(f"\nProcessing {employee['full_name']} ({employee['employee_id']})...")

        # 1. Generate welcome email
        html = email_service.render("welcome_email.html", {
            **employee,
            "sender_name": settings.sender_name,
        })
        subject = f"Welcome to the team, {employee['preferred_name'] or employee['full_name']}!"

        # 2. Send welcome email
        result = email_service.send(
            to_email=employee["email"],
            subject=subject,
            html_body=html,
            filename_hint=f"welcome_{employee['employee_id']}",
        )
        print(f"  Email: {result['status']}")

        # 3. Update onboarding tracker
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        data_source.mark_sent(employee["employee_id"], timestamp)
        print(f"  Tracker updated: onboarding_status=sent at {timestamp}")

        processed.append(employee)

    # 4. Notify HR with a run summary
    hr_html = email_service.render("hr_notification.html", {
        "run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "count": len(processed),
        "employees": processed,
    })
    email_service.send(
        to_email=settings.hr_notify_email,
        subject=f"Onboarding automation: {len(processed)} welcome email(s) sent",
        html_body=hr_html,
        filename_hint="hr_notification_summary",
    )
    print(f"\nHR notified at {settings.hr_notify_email}.")
    print(f"--- Run complete: {len(processed)} employee(s) processed ---")


if __name__ == "__main__":
    run()
