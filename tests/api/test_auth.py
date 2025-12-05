import pytest
from faker import Faker
from api_clients.api_manager import ApiManager
from conftest import creation_user_data
from utils.data_generator import DataGenerator

faker = Faker()


class TestRegisterPositive:
    """Позитивные тесты регистрации"""

    def test_register_user_with_valid_data(self, super_admin, creation_user_data):
        """ Регистрация с валидными данными """
        response = super_admin.api.auth_api.register_user(creation_user_data, expected_status=201)
        response_data = response.json()

        assert response_data["email"] == creation_user_data["email"]
        assert "id" in response_data
        assert "USER" in response_data["roles"]

    def test_register_user_returns_correct_structure(self, super_admin, creation_user_data):
        """ Проверка структуры ответа при регистрации """
        response = super_admin.api.auth_api.register_user(creation_user_data, expected_status=201).json()

        assert "id" in response
        assert "email" in response
        assert "fullName" in response
        assert "roles" in response
        assert "verified" in response
        assert "createdAt" in response
        assert "banned" in response

    def test_register_user_with_cyrillic_fullname(self, super_admin, creation_user_data):
        """ Регистрация с кириллицей в ФИО """
        creation_user_data["fullName"] = "Иван Иванович Иванов"
        response = super_admin.api.auth_api.register_user(creation_user_data, expected_status=201).json()

        assert response["fullName"] == "Иван Иванович Иванов"


class TestRegisterNegative:
    """ Негативные тесты регистрации """

    def test_register_user_with_existing_email(self, common_user, creation_user_data):
        """ Регистрация с уже существующим email """
        common_user.api.auth_api.register_user(creation_user_data, expected_status=409)

    def test_register_user_with_invalid_email_format(self, test_user, api_manager):
        """ Некорректный формат email """
        test_user["email"] = "invalid_email"
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_with_empty_email(self, test_user, api_manager):
        """ Пустой email """
        test_user["email"] = ""
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_with_empty_fullname(self, test_user, api_manager):
        """ Пустое ФИО """
        test_user["fullName"] = ""
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_with_empty_password(self, test_user, api_manager):
        """ Пустой пароль """
        test_user["password"] = ""
        test_user["passwordRepeat"] = ""
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_with_mismatched_passwords(self, test_user, api_manager):
        """ Пароли не совпадают """
        test_user["passwordRepeat"] = "DifferentPassword123"
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_with_short_password(self, test_user, api_manager):
        """ Слишком короткий пароль """
        short_pass = "Aa1"
        test_user["password"] = short_pass
        test_user["passwordRepeat"] = short_pass
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_without_uppercase(self, test_user, api_manager):
        """ Пароль без заглавных букв """
        new_pass = "password123"
        test_user["password"] = new_pass
        test_user["passwordRepeat"] = new_pass
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_without_digits(self, test_user, api_manager):
        """ Пароль без цифр """
        new_pass = "PasswordAbc"
        test_user["password"] = new_pass
        test_user["passwordRepeat"] = new_pass
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_register_user_with_sql_injection_attempt(self, test_user, api_manager):
        """Попытка SQL-инъекции в email"""
        test_user["email"] = "admin'--@test.com"
        response = api_manager.auth_api.register_user(test_user, expected_status=400).json()

        assert "Некорректный email" in response["message"]

    def test_register_user_without_password_repeat(self, test_user, api_manager):
        """ Отсутствие поля passwordRepeat """
        test_user.pop("passwordRepeat", None)
        api_manager.auth_api.register_user(test_user, expected_status=400)




