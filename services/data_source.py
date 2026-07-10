"""
Data source layer: fetch new employee records and update onboarding status.

Two backends, same interface:
  - CsvDataSource   (demo mode — no credentials needed)
  - SheetsDataSource (live mode — Google Sheets via service account)

Both expose:
  get_pending_employees() -> list[dict]
  mark_sent(employee_id, timestamp) -> None
"""
import csv
from datetime import datetime
from pathlib import Path


class CsvDataSource:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)

    def _read_all(self):
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _write_all(self, rows, fieldnames):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def get_pending_employees(self):
        rows = self._read_all()
        return [r for r in rows if r.get("onboarding_status", "").strip().lower() == "pending"]

    def mark_sent(self, employee_id: str, timestamp: str = None):
        timestamp = timestamp or datetime.utcnow().isoformat(timespec="seconds") + "Z"
        rows = self._read_all()
        fieldnames = rows[0].keys() if rows else []
        for r in rows:
            if r["employee_id"] == str(employee_id):
                r["onboarding_status"] = "sent"
                r["welcome_email_sent_at"] = timestamp
        self._write_all(rows, fieldnames)


class SheetsDataSource:
    """
    Live-mode backend using Google Sheets API.
    Requires: google-api-python-client, google-auth
    Requires a service account JSON with edit access to the target sheet.
    """

    def __init__(self, sheet_id: str, service_account_json: str, tab_name: str = "Employees"):
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_service_account_file(
            service_account_json,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet_id = sheet_id
        self.tab_name = tab_name

    def _get_values(self):
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.sheet_id, range=self.tab_name)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            return [], []
        header, *rows = values
        return header, rows

    def get_pending_employees(self):
        header, rows = self._get_values()
        status_idx = header.index("onboarding_status")
        records = []
        for row in rows:
            row = row + [""] * (len(header) - len(row))  # pad short rows
            record = dict(zip(header, row))
            if record.get("onboarding_status", "").strip().lower() == "pending":
                records.append(record)
        return records

    def mark_sent(self, employee_id: str, timestamp: str = None):
        timestamp = timestamp or datetime.utcnow().isoformat(timespec="seconds") + "Z"
        header, rows = self._get_values()
        id_idx = header.index("employee_id")
        status_idx = header.index("onboarding_status")
        sent_idx = header.index("welcome_email_sent_at")

        for i, row in enumerate(rows, start=2):  # +2: header row + 1-indexing
            if row and row[0] == str(employee_id):
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=f"{self.tab_name}!{chr(65+status_idx)}{i}",
                    valueInputOption="RAW",
                    body={"values": [["sent"]]},
                ).execute()
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=f"{self.tab_name}!{chr(65+sent_idx)}{i}",
                    valueInputOption="RAW",
                    body={"values": [[timestamp]]},
                ).execute()
                break


def get_data_source(settings):
    if settings.is_demo:
        return CsvDataSource(settings.demo_csv_path)
    return SheetsDataSource(
        settings.google_sheet_id,
        settings.google_service_account_json,
        settings.sheet_tab_name,
    )
