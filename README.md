# Employee Onboarding Email Automation

Automates the manual "copy template → edit details → send email → update
tracker" onboarding process into a single idempotent script.

## Before → After

**Manual:** HR adds employee → copy email template → edit details by hand →
send welcome email → update onboarding tracker (4 manual, error-prone steps).

**Automated:** New employee record → generate welcome email → send it →
update tracker → notify HR. One command, zero copy-paste.

## Architecture

```
main.py                    orchestrates the pipeline
config.py                  demo vs. live mode config (env-driven)
services/
  data_source.py           CsvDataSource (demo) / SheetsDataSource (live) — same interface
  email_service.py         renders Jinja2 templates, sends via SMTP or writes to disk
templates/
  welcome_email.html       employee-facing welcome email
  hr_notification.html     HR-facing run summary
data/
  employees.csv            demo "database" of employee records
```

The data-source layer is swappable behind one interface
(`get_pending_employees()` / `mark_sent()`), so moving from a CSV to a real
Google Sheet (or any other system of record) doesn't touch the pipeline
logic — only `services/data_source.py`.

## Run it (demo mode — no setup required)

```bash
pip install -r requirements.txt
python main.py
```

This reads `data/employees.csv`, renders and "sends" welcome emails
(saved as `.html` files in `outputs/` instead of actually emailing anyone),
marks each employee as `sent` in the CSV, and writes an HR summary email.
Run it twice — the second run finds nothing pending, proving it's safe to
schedule on a cron.

## Run it for real (live mode)

1. Create a Google Sheet with an `Employees` tab matching the CSV columns.
2. Create a Google Cloud service account with Sheets API access, share the
   sheet with its email, download the JSON key.
3. Copy `.env.example` to `.env` and fill in your Sheet ID, service account
   path, and SMTP credentials (a Gmail **App Password** works well).
4. Install the optional live-mode dependencies:
   ```bash
   pip install google-api-python-client google-auth
   ```
5. Run:
   ```bash
   MODE=live python main.py
   ```

## Design decisions

- **Idempotent by design** — re-running never double-sends, so it's safe to
  run on a schedule instead of needing to be triggered manually.
- **Demo/live parity** — the same orchestration code path runs in both
  modes; only the config and backend implementations differ. This makes the
  project runnable and reviewable without any credentials.
- **Templates, not string formatting** — Jinja2 templates keep email content
  editable by non-engineers and separate from send logic.

## Possible extensions

- Slack notification to HR instead of/alongside email
- Multi-language templates based on `office_location`
- Retry/backoff and a dead-letter log for failed sends
- Trigger via webhook (e.g. from an ATS) instead of polling
