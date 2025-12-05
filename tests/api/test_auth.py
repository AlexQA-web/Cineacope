import pytest
from faker import Faker

from conftest import common_user
from models.base_models import RegisterUserResponse


faker = Faker()

@pytest.mark.api
class TestRegisterPositive:
    """Позитивные тесты регистрации"""

    @pytest.mark.regression
    @pytest.mark.smoke
    def test_register_user_with_valid_data(self, api_manager, registration_user_data):
        """ Регистрация с валидными данными """
        response = api_manager.auth_api.register_user(user_data=registration_user_data)
        response_data = RegisterUserResponse(**response.json())

        assert response_data.email == registration_user_data["email"], "Email не совпадает"

    @pytest.mark.regression
    def test_register_user_with_cyrillic_fullname(self, api_manager, registration_user_data):
        """ Регистрация с кириллицей в ФИО """
        registration_user_data["fullName"] = "Иван Иванович Иванов"
        response = api_manager.auth_api.register_user(user_data=registration_user_data)
        response_data = RegisterUserResponse(**response.json())

        assert response_data.fullName == registration_user_data["fullName"]

@pytest.mark.api
class TestRegisterNegative:
    """ Негативные тесты регистрации """
    @pytest.mark.slow
    def test_register_user_with_existing_email(self, api_manager, creation_user_data):
        """ Регистрация с уже существующим мылом """
        response = api_manager.auth_api.register_user(user_data=creation_user_data, expected_status=404)

    def test_register_user_with_invalid_email_format(self, registration_user_data, api_manager):
        """ Некорректный формат мылом """
        registration_user_data["email"] = "invalid_email"
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_with_empty_email(self, registration_user_data, api_manager):
        """ Пустое мыло """
        registration_user_data["email"] = ""
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_with_empty_fullname(self, registration_user_data, api_manager):
        """ Пустое ФИО """
        registration_user_data["fullName"] = ""
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_with_empty_password(self, registration_user_data, api_manager):
        """ Пустой пароль """
        registration_user_data["password"] = ""
        registration_user_data["passwordRepeat"] = ""
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_with_mismatched_passwords(self, registration_user_data, api_manager):
        """ Пароли не совпадают """
        registration_user_data["passwordRepeat"] = "DifferentPassword123"
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_with_short_password(self, registration_user_data, api_manager):
        """ Слишком короткий пароль """
        short_pass = "Aa1"
        registration_user_data["password"] = short_pass
        registration_user_data["passwordRepeat"] = short_pass
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_without_uppercase(self, registration_user_data, api_manager):
        """ Пароль без заглавных букв """
        new_pass = "password123"
        registration_user_data["password"] = new_pass
        registration_user_data["passwordRepeat"] = new_pass
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_without_digits(self, registration_user_data, api_manager):
        """ Пароль без цифр """
        new_pass = "PasswordAbc"
        registration_user_data["password"] = new_pass
        registration_user_data["passwordRepeat"] = new_pass
        api_manager.auth_api.register_user(registration_user_data, expected_status=400)

    def test_register_user_with_sql_injection_attempt(self, registration_user_data, api_manager):
        """Попытка инъекции в мыло"""
        registration_user_data["email"] = "admin'--@test.com"
        response = api_manager.auth_api.register_user(registration_user_data, expected_status=400).json()

        assert "Некорректный email" in response["message"]

    def test_register_user_without_password_repeat(self, registration_user_data, api_manager):
        """ Отсутствие поля passwordRepeat """
        data = registration_user_data.pop("passwordRepeat")
        api_manager.auth_api.register_user(data, expected_status=400)




