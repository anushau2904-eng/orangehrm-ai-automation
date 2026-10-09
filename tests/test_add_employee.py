
import re
from uuid import uuid4

from playwright.sync_api import Page, expect

from config.credentials import get_orangehrm_credentials
from pages.add_employee_page import AddEmployeePage
from pages.login_page import LoginPage
from pages.pim_page import PIMPage
from services.employee_service import EmployeeService
from utils.json_reader import JsonReader


def test_admin_can_add_employee(page: Page) -> None:
    username, password = get_orangehrm_credentials()

    # Read employee test data from JSON
    test_data = JsonReader.read_json("employee_data.json")

    first_name = test_data["first_name"]
    middle_name = test_data["middle_name"]
    last_name = f"{test_data['last_name']}{uuid4().hex[:5]}"

    # Login
    login_page = LoginPage(page)
    login_page.login(username, password)

    # Navigate to PIM -> Add Employee
    pim_page = PIMPage(page)
    pim_page.open_add_employee()

    # Fill employee details
    add_employee_page = AddEmployeePage(page)

    expect(
        add_employee_page.create_login_details
    ).not_to_be_checked()

    add_employee_page.fill_employee_name(
        first_name,
        middle_name,
        last_name,
    )

    # Capture OrangeHRM-generated Employee ID
    employee_id = add_employee_page.get_employee_id()

    assert employee_id, (
        "The Add Employee form did not generate an Employee Id"
    )

    # Save employee
    add_employee_page.save_employee()

    # Handle intermittent duplicate Employee ID
    if add_employee_page.has_duplicate_employee_id_error():
        employee_id = EmployeeService.generate_unused_employee_id(
            page
        )

        add_employee_page.set_employee_id(employee_id)
        add_employee_page.save_employee()

    # Verify Personal Details page is displayed
    expect(page).to_have_url(
        re.compile(
            r"https://opensource-demo\.orangehrmlive\.com/"
            r"web/index\.php/pim/viewPersonalDetails/"
            r"empNumber/\d+$"
        )
    )

    expect(
        page.get_by_role(
            "heading",
            name="Personal Details",
            exact=True,
        )
    ).to_be_visible()

    # Navigate to Employee List
    pim_page.open_employee_list()

    # Search using the final Employee ID
    pim_page.search_employee_by_id(employee_id)

    employee_row = pim_page.employee_row(employee_id)

    # Verify employee was created
    expect(employee_row).to_have_count(1)
    expect(employee_row).to_contain_text(employee_id)
    expect(employee_row).to_contain_text(first_name)
    expect(employee_row).to_contain_text(middle_name)
    expect(employee_row).to_contain_text(last_name)
