from requests import Session, Response
from constants.constants import (REGISTER_ENDPOINT, AUTH_BASE_URL, LOGIN_ENDPOINT,
                                  LOGOUT_ENDPOINT, REFRESH_TOKENS_ENDPOINT, CONFIRM_EMAIL_ENDPOINT)
from custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    """
    Класс для работы с аутентификацией.
    """
    def __init__(self, session: Session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def register_user(self, user_data: dict, expected_status=201) -> Response:
        """
        Регистрация нового пользователя
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        :return Response
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data: dict, expected_status=200) -> Response:
        """
        Авторизация пользователя.
        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        :return Response
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def logout_user(self, expected_status=200) -> Response:
        """
        Выход из учётной записи
        :param expected_status: Ожидаемый статус-код
        :return: Response
        """
        return self.send_request(
            method="GET",
            endpoint=LOGOUT_ENDPOINT,
            expected_status=expected_status
        )

    def refresh_tokens(self, expected_status=200) -> Response:
        """
        Обновление токенов
        :param expected_status: Ожидаемый статус-код
        :return: Response
        """
        return self.send_request(
            method="GET",
            endpoint=REFRESH_TOKENS_ENDPOINT,
            expected_status=expected_status
        )

    def confirm_email(self, token, expected_status=200) -> Response:
        """
        Подтверждение email
        :param token: Токен подтверждения
        :param expected_status: Ожидаемый статус-код
        :return: Response
        """
        return self.send_request(
            method="GET",
            endpoint=f"{CONFIRM_EMAIL_ENDPOINT}?token={token}",
            expected_status=expected_status
        )

    def authenticate(self, user_creds: tuple):
        """
        Аутентификация и сохранение токена в сессии
        :param user_creds: Кортеж (email, password)
        """
        login_data = {
            "email": user_creds[0],
            "password": user_creds[1]
        }
        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")
        token = response["accessToken"]
        self._update_session_headers(self.session, **{"authorization": f"Bearer {token}"})
