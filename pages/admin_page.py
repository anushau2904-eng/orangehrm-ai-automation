import re
from playwright.sync_api import Page

class AdminPage:
    def __init__(self,page):
        self.page = page
        self.admin_link = page.get_by_role("link", name="Admin")
        self.btn_add = page.get_by_role("button", name=re.compile(r"Add$"))


    def open_add_user(self):
        self.admin_link.click()
        self.btn_add.click()