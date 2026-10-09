import re

from config.credentials import get_orangehrm_credentials
from playwright.sync_api import Page, expect


def test_admin_can_log_in(page: Page) -> None:
    username, password = get_orangehrm_credentials()
    page.goto("https://opensource-demo.orangehrmlive.com")

    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(
        re.compile(
            r"https://opensource-demo\.orangehrmlive\.com/web/index\.php/dashboard/index"
        )
    )
