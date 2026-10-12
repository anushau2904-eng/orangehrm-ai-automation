import re

from config.credentials import get_orangehrm_credentials
from pages.login_page import LoginPage
from playwright.sync_api import expect


def test_login(page):
    username, password = get_orangehrm_credentials()
    login_page = LoginPage(page)
    login_page.login(username, password)
    expect(page).to_have_url(re.compile(r"https://opensource-demo\.orangehrmlive\.com/web/index\.php/dashboard/index"
            )
        )


def test_login_rejects_invalid_credentials(page):
    login_page = LoginPage(page)
    login_page.login("invalid_user", "invalid_password")

    alert = page.get_by_role("alert")
    expect(alert).to_contain_text("Invalid credentials")
    expect(page).to_have_url(
        re.compile(
            r"https://opensource-demo\.orangehrmlive\.com/web/index\.php/auth/login"
        )
    )