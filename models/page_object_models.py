import allure
from playwright.sync_api import Page

from utils.data_generator import DataGenerator


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator: str, text: str):
        self.page.fill(locator, text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str):
        self.page.wait_for_url(url)
        assert self.page.url == url, "Редирект на домашнюю старницу не произошел"

    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

    @allure.step("Ожидание появления или исчезновения элемента: {locator}, state = {state}")
    def wait_for_element(self, locator: str, state: str = "visible"):
        self.page.locator(locator).wait_for(state=state)

    @allure.step("Скриншот текущей страиницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot_path = "screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)  # full_page=True для скриншота всей страницы

        # Прикрепление скриншота к Allure-отчёту
        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect", attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения c текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:
        with allure.step("Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text)
            # Ждем появления элемента
            notification_locator.wait_for(state="visible")
            assert notification_locator.is_visible(), "Уведомление не появилось"

        with allure.step("Проверка исчезновения алерта с текстом: '{text}'"):
            # Ждем, пока алерт исчезнет
            notification_locator.wait_for(state="hidden")
            assert notification_locator.is_visible() == False, "Уведомление не исчезло"

    def click_filter(self, locator, option):
        self.click_element(locator=locator)
        self.click_element(f'span:has-text("{option}")')


class BasePage(PageAction): #Базовая логика доспустимая для всех страниц на сайте
    def __init__(self, page: Page):
        super().__init__(page)
        self.home_url = "https://dev-cinescope.coconutqa.ru/"

        # Общие локаторы для всех страниц на сайте
        self.home_button = 'a[href="/"]:has-text("Cinescope")'
        self.all_movies_button = 'a[href="/movies"]:has-text("Все фильмы")'

    @allure.step("Переход на главную страницу, из шапки сайта")
    def go_to_home_page(self):
        self.click_element(self.home_button)
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки сайта'")
    def go_to_all_movies(self):
        self.click_element(self.all_movies_button)
        self.wait_redirect_for_url(f"{self.home_url}movies")


class CinescopeRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        # Локаторы элементов
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[data-qa-id='register_submit_button']"
        self.sign_button = 'a[href="/login"]:has-text("Войти")'

    # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.click_element(self.register_button)

    def assert_was_redirect_to_login_page(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Подтвердите свою почту")


class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        # Локаторы элементов
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"

        self.login_button = 'button[type="submit"]:has-text("Войти")'
        self.register_button = 'a[href="/register"]:has-text("Зарегистрироваться")'

    # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def assert_alert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")


class CinescopeProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}dashboard"

        self.admin_panel_string = 'a[href="/dashboard"]:has-text("Админ панель")'
        self.exit_button = "button[name='Выход']"

    def click_admin_panel_button(self):
        self.click_element(self.admin_panel_string)


class CinescopeMainPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.profile_button = 'button[type="button"]:has-text("Профиль")'
        self.place_filter = 'button[role="combobox"]:has-text("Место")'
        self.genre_filter = 'button[role="combobox"]:has-text("Жанр")'
        self.sort_filter = 'button[role="combobox"]:has-text("Создано")'


    def click_movie_details(self,movie_id: int):
        self.click_element(f'a[href="/movies/{movie_id}"]')


    def click_profile_button(self):
        self.click_element(self.profile_button)


class AdminPanelPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.movies = 'h3.ml-4:has-text("Фильмы")'
        self.users = 'h3.ml-4:has-text("Пользователи")'
        self.genres = 'h3.ml-4:has-text("Жанры")'
        self.payments = 'h3.ml-4:has-text("Платежи")'
        self.return_to_dashboard = 'a.text-3xl:has-text("Cinescope Admin")'
        self.return_to_main_page = 'a[href="/"]:has-text("Вернуться на главную")'
        self.return_to_profile = 'button:has-text("Профиль")'

        self.movie_published_combobox = 'button[role="combobox"]:has-text("Опубликован")'
        self.movie_create_combobox = 'button[role="combobox"]:has-text("Создано")'
        self.movie_add_button = 'button:has-text("Добавить фильм")'


class CreateMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.name_input = 'input#name'
        self.description_input = 'textarea#description'
        self.price_input = 'input#price'
        self.location_input = 'button#location'
        self.image_url_input = 'input#imageUrl'
        self.genre_button = 'button#genreId'
        self.published_button = 'button#published'
        self.send_button = 'button[type="submit"]:has-text("Отправить")'
        self.close_button = 'button:has(svg):has-text("Close")'


    @allure.step("Заполнение формы создания фильма")
    def add_new_movie(self):
        self.enter_text_to_element(self.name_input, DataGenerator.generate_movie_name())
        self.enter_text_to_element(self.description_input, DataGenerator.generate_movie_description())
        price = DataGenerator.generate_movie_price()
        self.enter_text_to_element(self.price_input, str(price))
        location = DataGenerator.generate_movie_location()  # "MSK" или "SPB"
        self.click_element(self.location_input)  # Открываем combobox
        self.page.get_by_role("option", name=location).click()  # Выбираем опцию
        self.enter_text_to_element(self.image_url_input, DataGenerator.generate_movie_image_url())
        self.click_filter(self.genre_button, option=DataGenerator.generate_movie_genre())
        self.click_element(self.send_button)







