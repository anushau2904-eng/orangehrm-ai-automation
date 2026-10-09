# OrangeHRM AI Automation

Python browser-automation tests for OrangeHRM, built with Playwright and pytest.
The suite covers login, employee creation, and user creation flows against the
OrangeHRM demo application.

## Prerequisites

- Python 3.10 or later
- Node.js and npm, for the Playwright MCP server configured in this project
- A desktop session: the pytest browser fixture launches Chromium with a visible
  window (`headless=False`)
- OrangeHRM login credentials supplied locally through environment variables

## Setup

Create and activate a virtual environment, then install the Python dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install the Chromium browser used by Playwright:

```powershell
playwright install chromium
```

Configure local OrangeHRM credentials by copying the example file and editing
the copy:

```powershell
Copy-Item .env.example .env
```

Set `ORANGEHRM_USERNAME` and `ORANGEHRM_PASSWORD` in `.env`. Replace the
placeholders with credentials for your test environment. Do not commit `.env`;
it is excluded by `.gitignore`.

## Run tests

Run the complete test suite:

```powershell
pytest
```

Run only the employee-service pagination unit tests:

```powershell
pytest tests/test_employee_service_pagination.py
```

These pagination tests use stubbed API responses, so they do not launch a
browser or require OrangeHRM credentials. The complete suite launches visible
Chromium and uses the locally configured credentials.
