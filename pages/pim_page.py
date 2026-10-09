import re

from playwright.sync_api import Locator, Page


class PIMPage:
    def __init__(self, page: Page):
        self.page = page
        self.pim_link = page.get_by_role("link", name="PIM")
        self.add_employee_tab = page.get_by_role("link", name="Add Employee")
        self.employee_list_tab = page.get_by_role("link", name="Employee List")
        self.employee_id_filter = page.locator(".oxd-input-group").filter(
            has_text=re.compile(r"^Employee Id$")
        ).locator("input")
        self.search_button = page.get_by_role("button", name="Search")

    def open_add_employee(self) -> None:
        self.pim_link.click()
        self.add_employee_tab.click()

    def open_employee_list(self) -> None:
        self.employee_list_tab.click()

    def search_employee_by_id(self, employee_id: str) -> None:
        self.employee_id_filter.fill(employee_id)
        self.search_button.click()

    def employee_row(self, employee_id: str) -> Locator:
        employee_id_cell = self.page.get_by_role(
            "cell", name=employee_id, exact=True
        )
        return self.page.locator(".oxd-table-card").filter(has=employee_id_cell)
