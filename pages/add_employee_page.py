import re

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError


class AddEmployeePage:
    def __init__(self, page: Page):
        self.page = page
        self.first_name = page.get_by_role("textbox", name="First Name")
        self.middle_name = page.get_by_role("textbox", name="Middle Name")
        self.last_name = page.get_by_role("textbox", name="Last Name")
        self.employee_id = page.locator(".oxd-input-group").filter(
            has_text=re.compile(r"^Employee Id$")
        ).locator("input")
        self.employee_id_duplicate_error: Locator = page.get_by_text(
            "Employee Id already exists", exact=True
        )
        self.create_login_details = page.get_by_role("checkbox")
        self.save_button = page.get_by_role("button", name="Save")

    def fill_employee_name(
        self, first_name: str, middle_name: str, last_name: str
    ) -> None:
        self.first_name.fill(first_name)
        self.middle_name.fill(middle_name)
        self.last_name.fill(last_name)

    def get_employee_id(self) -> str:
        return self.employee_id.input_value()

    def set_employee_id(self, employee_id: str) -> None:
        self.employee_id.fill(employee_id)

    def has_duplicate_employee_id_error(self) -> bool:
        try:
            self.employee_id_duplicate_error.wait_for(
                state="visible", timeout=1500
            )
        except PlaywrightTimeoutError:
            return False
        return True

    def save_employee(self) -> None:
        self.save_button.click()
