# Employee Onboarding Workflow Automation

Automates the manual employee onboarding process by generating personalized welcome emails, updating the onboarding tracker, and notifying HR.

## Workflow

```text
New Employee Record
        ↓
Generate Welcome Email
        ↓
Send Welcome Email
        ↓
Update Onboarding Tracker
        ↓
Notify HR
```

## Manual vs Automated

**Manual**

* HR adds a new employee.
* Copies the welcome email template.
* Updates employee details manually.
* Sends the email.
* Updates the onboarding tracker.

**Automated**

* Detects new employee records.
* Generates personalized welcome emails.
* Sends the welcome email.
* Updates the onboarding tracker.
* Sends an HR summary.

## Project Structure

```text
main.py
config.py

services/
  data_source.py
  email_service.py
  notification_service.py

templates/
  welcome_email.html
  hr_notification.html

data/
  employees.csv

outputs/
screenshots/
```

## Features

* Automated onboarding workflow
* Personalized HTML welcome emails
* Automated onboarding tracker updates
* HR notification summary
* Demo mode using CSV
* Safe to rerun without processing completed employees

## Tech Stack

* Python
* Jinja2
* CSV
* HTML
* SMTP (optional for live mode)

## Run

```bash
pip install -r requirements.txt
python main.py
```

The automation reads pending employees from `employees.csv`, generates welcome emails, updates the onboarding tracker, and creates an HR summary.

## Future Enhancements

* Google Sheets integration
* Real email delivery
* Slack notifications
* Scheduled execution
* Dashboard for onboarding status
