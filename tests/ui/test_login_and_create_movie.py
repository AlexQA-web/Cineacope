import time
import allure
import pytest
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from models.page_object_models import CinescopeLoginPage, CinescopeProfilePage, CinescopeMainPage, AdminPanelPage, \
    CreateMoviePage

load_dotenv()

SUPER_ADMIN_USERNAME = os.getenv('SUPER_ADMIN_USERNAME')
SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD')

@allure.epic("Тестирование UI")
@allure.feature("Тестирование логина и создание фильма из Админ панели")
@pytest.mark.ui
class TestLoginPage:
    @allure.title("Проведение успешного входа в систему")
    def test_login_by_admin_and_create_movie(self, email=SUPER_ADMIN_USERNAME, password=SUPER_ADMIN_PASSWORD):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            current_page = CinescopeLoginPage(page)

            current_page.open()
            current_page.login(email, password)
            time.sleep(2)

            current_page = CinescopeMainPage(page)

            current_page.click_profile_button()
            time.sleep(2)

            current_page = CinescopeProfilePage(page)
            current_page.click_admin_panel_button()
            time.sleep(2)

            current_page = AdminPanelPage(page)
            current_page.click_element(current_page.movies)
            current_page.click_element(current_page.movie_add_button)
            time.sleep(2)

            current_page = CreateMoviePage(page)
            current_page.add_new_movie()

            # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
            time.sleep(5)
            browser.close()
