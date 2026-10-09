import re
import secrets
from typing import Any
from uuid import uuid4

from playwright.sync_api import Page, expect

from config.credentials import get_orangehrm_credentials


def _fetch_all_pages(page: Page, resource: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    limit = 50
    total = 1

    while offset < total:
        response = page.request.get(
            f"https://opensource-demo.orangehrmlive.com/web/index.php/api/v2/{resource}",
            params={"limit": limit, "offset": offset},
        )
        if not response.ok:
            raise AssertionError(
                f"Failed to fetch {resource}: HTTP {response.status}"
            )
        result = response.json()
        batch = result["data"]
        total = result["meta"]["total"]
        records.extend(batch)
        if not batch and len(records) < total:
            raise AssertionError(
                f"Pagination for {resource} stopped at {len(records)} of {total} records"
            )
        offset += len(batch)

    return records


def test_admin_can_add_user(page: Page) -> None:
    orangehrm_username, orangehrm_password = get_orangehrm_credentials()
    username = f"e2e_user_{uuid4().hex[:12]}"
    password = f"E2e!{secrets.token_hex(12)}9"

    page.goto("https://opensource-demo.orangehrmlive.com")

    page.get_by_role("textbox", name="Username").fill(orangehrm_username)
    page.get_by_role("textbox", name="Password").fill(orangehrm_password)
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(
        re.compile(
            r"https://opensource-demo\.orangehrmlive\.com/web/index\.php/dashboard/index"
        )
    )

    employees = _fetch_all_pages(page, "pim/employees")
    system_users = _fetch_all_pages(page, "admin/users")
    assigned_emp_numbers = {
        user_employee["empNumber"]
        for user in system_users
        if not user.get("deleted", False)
        for user_employee in [user.get("employee") or {}]
        if user_employee.get("empNumber") is not None
    }
    employee_id_counts: dict[str, int] = {}
    for employee in employees:
        employee_id = employee.get("employeeId")
        if employee_id:
            key = str(employee_id)
            employee_id_counts[key] = employee_id_counts.get(key, 0) + 1

    employee = next(
        (
            candidate
            for candidate in employees
            if candidate.get("terminationId") is None
            and candidate.get("empNumber") not in assigned_emp_numbers
            and candidate.get("employeeId")
            and employee_id_counts.get(str(candidate["employeeId"])) == 1
        ),
        None,
    )
    assert employee is not None, (
        "No active employee with a unique employee ID is available "
        "without an existing System User account"
    )
    employee_id = str(employee["employeeId"])
    employee_name = " ".join(
        part
        for part in (
            employee.get("firstName"),
            employee.get("middleName"),
            employee.get("lastName"),
        )
        if part
    )
    assert employee_name, f"Employee {employee_id} has no displayable name"
    employee_table_name = " ".join(
        part
        for part in (employee.get("firstName"), employee.get("lastName"))
        if part
    )

    page.get_by_role("link", name="Admin").click()
    page.get_by_role("button", name=re.compile(r"Add$")).click()
    expect(page.get_by_role("heading", name="Add User")).to_be_visible()

    page.locator(".oxd-input-group").filter(has_text="User Role").locator(
        ".oxd-select-text"
    ).click()
    page.get_by_role("option", name="ESS", exact=True).click()

    employee_search = page.get_by_role("textbox", name="Type for hints...")
    employee_search.fill(employee_id)
    employee_option = page.get_by_role("option", name=employee_name, exact=True)
    expect(employee_option).to_be_visible()
    expect(employee_option).to_have_count(1)
    employee_option.click()

    page.locator(".oxd-input-group").filter(has_text="Status").locator(
        ".oxd-select-text"
    ).click()
    page.get_by_role("option", name="Enabled", exact=True).click()

    page.locator(".oxd-input-group").filter(has_text="Username").locator(
        "input"
    ).fill(username)
    page.locator(".oxd-input-group").filter(
        has_text=re.compile(r"^Password$")
    ).locator("input").fill(password)
    page.locator(".oxd-input-group").filter(
        has_text=re.compile(r"^Confirm Password$")
    ).locator("input").fill(password)

    page.get_by_role("button", name="Save").click()

    page.get_by_role("link", name="Admin").click()
    page.locator(".oxd-input-group").filter(
        has_text=re.compile(r"^Username$")
    ).locator("input").fill(username)
    page.get_by_role("button", name="Search").click()

    user_row = page.get_by_role("row").filter(has_text=username)
    expect(user_row).to_have_count(1)
    expect(user_row).to_contain_text("ESS")
    expect(user_row).to_contain_text(employee_table_name)
    expect(user_row).to_contain_text("Enabled")
