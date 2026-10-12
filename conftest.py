import hashlib
import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parent


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None:
        return

    screenshot_dir = PROJECT_ROOT / "reports" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid).strip("._")[:100]
    suffix = hashlib.sha1(item.nodeid.encode("utf-8")).hexdigest()[:8]
    screenshot_path = screenshot_dir / f"{safe_name or 'test'}_{suffix}.png"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception as exc:
        report.sections.append(
            ("Failure screenshot", f"Capture failed: {type(exc).__name__}: {exc}")
        )
    else:
        report.sections.append(
            (
                "Failure screenshot",
                f"Saved to {screenshot_path.relative_to(PROJECT_ROOT)}",
            )
        )


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()