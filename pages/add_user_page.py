import re

from playwright.sync_api import Page,expect


class AddUserPage:

    def __init__(self, page: Page):
        self.page = page

        self.user_role = page.locator(".oxd-input-group").filter(has_text="User Role"
        ).locator(".oxd-select-text")

        self.employee_search = page.get_by_role("textbox",name="Type for hints...")

        self.status = page.locator(".oxd-input-group").filter(has_text="Status"
        ).locator(".oxd-select-text")

        self.username = page.locator(".oxd-input-group").filter(has_text="Username"
        ).locator("input")

        self.password = page.locator(".oxd-input-group").filter(has_text=re.compile(r"^Password$")
        ).locator("input")

        self.confirm_password = page.locator(".oxd-input-group").filter(has_text=re.compile(r"^Confirm Password$")
        ).locator("input")

        self.save_button = page.get_by_role("button",name="Save")

    def select_user_role(self,role):
        self.user_role.click()
        self.page.get_by_role("option", name=role, exact=True).click()

    def select_emp_name(self,empid,employee_name):
        self.employee_search.fill(empid)
        emp_option = self.page.get_by_role("option", name=employee_name, exact=True)
        expect(emp_option).to_be_visible()
        expect(emp_option).to_have_count(1)
        emp_option.click()


    def select_status(self,status):
        self.status.click()
        self.page.get_by_role("option", name=status, exact=True).click()


    def enter_username(self,username):
        self.username.fill(username)

    def enter_password(self,password):
        self.password.fill(password)
        self.confirm_password.fill(password)

    def save_user(self):
        self.save_button.click()




