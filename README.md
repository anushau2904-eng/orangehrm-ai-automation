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

## Copilot test orchestration

The workspace includes a **Playwright Test Orchestrator** custom agent in
`.github/agents/`. To try it, open this project in VS Code, open Copilot Chat,
select **Playwright Test Orchestrator** from the agent picker, and describe the
test you want in natural language. If the agent is not listed, confirm that
workspace custom agents are enabled and reload the project.

The orchestrator is configured to coordinate this workflow:

1. **Planner** creates a structured plan from the request.
2. **Generator** uses that plan to implement the requested test changes.
3. **Focused pytest run** executes only the requested test or tests.
4. **Healer, if needed** receives actual failure details and proposes a focused
   correction when the test fails.
5. **One focused rerun** verifies the correction. The orchestrator stops after
   this single healing-and-rerun cycle.

VS Code may request permission before the agent invokes subagents, edits files,
or executes pytest. Review each request and approve only actions within the
intended test scope. Do not provide credentials in chat or allow secrets to be
included in failure evidence.

The agent definition and its workflow instructions are implemented. Planner,
Generator, and Healer subagent invocations have each been exercised
individually, but the complete workflow being coordinated automatically by
this configured Orchestrator remains unverified. Agent discovery, permissions,
file editing, and focused terminal execution may still depend on the active
VS Code setup. Do not assume that the workflow runs fully automatically. A
test is successful only when an actual pytest execution reports a pass; a
generated or corrected test alone is not verified.

If orchestration is unavailable or stops because of missing tools, permissions,
or incomplete evidence, use the manual handoff workflow below.

## Manual test-generation workflow (fallback)

The Planner, Generator, Pytest runner, and Healer work through a manual
handoff. The user passes each stage's output to the next.

1. **Planner** — Give the Planner the testing requirement. It identifies
   scenarios and produces a complete structured plan with objectives,
   preconditions, test data, ordered steps, expected results, and relevant UI
   elements or locators when known. It labels observed UI details separately
   from assumptions and unknowns. Pass its complete response verbatim to the
   Generator.
2. **Generator** — Give the Generator the Planner's complete plan. It identifies
   essential gaps instead of inventing requirements, then creates or updates
   tests following this project's Python, Playwright, pytest, Page Object, and
   fixture patterns. Its handoff identifies the test file, provides the code or
   change summary, and states the focused pytest command, prerequisites, and
   known dependencies. The Generator does not run pytest unless explicitly
   requested.
3. **Pytest runner** — The user or orchestrator runs the Generator's focused
   command from the project root. For example, if the generated test is
   `tests/test_example.py`:

   ```powershell
   pytest tests/test_example.py
   ```

   Capture the command, exit code, and relevant output. If it fails, provide
   that evidence to the Healer. Redact credentials and other secrets.
4. **Healer** — Give the Healer the failing test path, exact pytest command,
   exit code, relevant traceback and assertion output, and browser or
   application evidence when available. The Healer diagnoses the likely root
   cause before making the smallest appropriate correction, preserving test
   intent, meaningful assertions, Page Objects, fixtures, and project
   structure. If the evidence is insufficient, provide the missing information
   rather than asking the Healer to guess.
5. **Verification** — The Healer returns the correction and exact focused pytest
   command to the user or orchestrator. The runner reruns that command once
   after the Healer's correction. This is the only permitted Healer
   correction-and-rerun cycle for a request. If the rerun still fails, stop and
   report the remaining failure; do not start another recovery cycle. Report
   success only after a rerun confirms the corrected test passes; a code change
   alone does not verify a fix.

Use these terms precisely: a **generated** test has been produced from a plan;
a **corrected** test has had a change made in response to failure evidence; a
**verified** test has passed a pytest run after its latest generation or
correction. Do not describe a generated or corrected test as verified until
the corresponding test run confirms it.
