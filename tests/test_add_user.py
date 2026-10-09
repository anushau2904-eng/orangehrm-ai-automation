import re
import secrets
from uuid import uuid4

from playwright.sync_api import expect

from config.credentials import get_orangehrm_credentials
from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.add_user_page import AddUserPage
from services.employee_service import EmployeeService


def test_add_user(page):
    orangehrm_username, orangehrm_password = get_orangehrm_credentials()

    # Login
    login_page = LoginPage(page)
    login_page.login(orangehrm_username, orangehrm_password)

    # Open Admin → Add User
    admin_page = AdminPage(page)
    admin_page.open_add_user()

    # Find an active employee without an existing System User
    employee = EmployeeService.get_available_employee(page)

    # Generate unique test data
    username = f"e2e_user_{uuid4().hex[:12]}"
    password = f"E2e!{secrets.token_hex(12)}9"

    # Add User
    add_user = AddUserPage(page)

    add_user.select_user_role("ESS")

    add_user.select_emp_name(
        employee["employeeId"],
        employee["employeeName"]
    )

    add_user.select_status("Enabled")

    add_user.enter_username(username)
    add_user.enter_password(password)

    add_user.save_user()

    # Verify created user
    employee_display_name = (
        f"{employee['firstName']} {employee['lastName']}"
    )

    username_search = page.locator(
        ".oxd-input-group"
    ).filter(
        has_text=re.compile(r"^Username$")
    ).locator("input")

    username_search.fill(username)

    page.get_by_role("button", name="Search").click()

    user_row = page.get_by_role("row").filter(
        has_text=username
    )

    expect(user_row).to_have_count(1)
    expect(user_row).to_contain_text("ESS")
    expect(user_row).to_contain_text(employee_display_name)
    expect(user_row).to_contain_text("Enabled")