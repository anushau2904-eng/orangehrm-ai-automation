from playwright.sync_api import Page
class LoginPage:
    def __init__(self,page:Page):
        self.page = page
        self.input_username = page.get_by_role("textbox", name="Username")
        self.input_password = page.get_by_role("textbox", name="Password")
        self.btn_login = page.get_by_role("button", name="Login")

    def login(self,username,password):
        self.page.goto("https://opensource-demo.orangehrmlive.com")
        self.input_username.fill(username)
        self.input_password.fill(password)
        self.btn_login.click()

       