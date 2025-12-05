from constants.constants import AUTH_BASE_URL
from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    """
    Класс для работы с API пользователей.
    """

    def __init__(self, session):
        super().__init__(session=session,base_url=AUTH_BASE_URL)
        self.session = session

    def get_user(self, user_locator, expected_status=200):
        """
        Получение данных о пользователе
        :param expected_status:
        :param user_locator: id or email пользователя
        :return: Response
        """
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_locator}",
            expected_status= expected_status
        )

    def create_user(self, user_data, expected_status=201):
        """
        Создание пользователя
        :param user_data: данные пользователя
        :param expected_status: Ожидаемый статус-код
        :return: Response
        """
        return self.send_request(
            method="POST",
            endpoint="/user",
            data=user_data,
            expected_status=expected_status
        )

    def delete_user(self, user_locator, expected_status=200):
        """
        Удаление пользователя.
        :param user_locator: id or email пользователя
        :param expected_status: Ожидаемый статус-код.
        :return:
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_locator}",
            expected_status=expected_status
        )

    # Добавить в api_clients/user_api.py
    def edit_user(self, user_id, user_data, expected_status=200):
        """
        Изменение данных пользователя
        :param user_id: ID пользователя
        :param user_data: Данные для обновления (roles, verified, banned)
        :param expected_status: Ожидаемый статус-код
        :return: Response
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"/user/{user_id}",
            data=user_data,
            expected_status=expected_status
        )
