# Импорт модуля json для работы с JSON-данными (сериализация/десериализация)
import json
# Импорт библиотеки requests для выполнения HTTP-запросов
import requests
# Импорт модуля logging для логирования событий и отладки
import logging
# Импорт модуля os для работы с операционной системой (переменные окружения, пути)
import os

from pydantic import BaseModel

from constants.constants import GREEN, RESET, RED


class CustomRequester:
    """
    Кастомный реквестер для стандартизации и упрощения отправки HTTP-запросов.
    """
    # Атрибут класса (общий для всех экземпляров) - базовые заголовки HTTP-запросов
    base_headers = {
        # Указываем, что отправляем JSON-данные в теле запроса
        "Content-Type": "application/json",
        # Указываем, что ожидаем получить JSON-данные в ответе
        "Accept": "application/json"
    }

    # Конструктор класса - вызывается при создании нового объекта CustomRequester
    def __init__(self, session, base_url):
        """
        Инициализация кастомного реквестера.
        :param session: Объект requests.Session.
        :param base_url: Базовый URL API.
        """
        # Сохраняем переданный объект сессии requests в атрибут экземпляра (для переиспользования соединения и cookies)
        self.session = session
        # Сохраняем базовый URL API (например, "https://api.example.com") в атрибут экземпляра
        self.base_url = base_url
        # Создаём копию базовых заголовков для этого экземпляра (чтобы изменения не влияли на другие экземпляры)
        self.headers = self.base_headers.copy()
        # Получаем объект логгера с именем текущего модуля (для записи логов)
        self.logger = logging.getLogger(__name__)
        # Устанавливаем уровень логирования INFO (будут записываться сообщения уровня INFO и выше)
        self.logger.setLevel(logging.INFO)

    # Метод для отправки HTTP-запросов с автоматической проверкой статус-кода и логированием
    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, need_logging=True):
        """
        Универсальный метод для отправки запросов.
        :param params:
        :param method: HTTP метод (GET, POST, PUT, DELETE и т.д.).
        :param endpoint: Эндпоинт (например, "/login").
        :param data: Тело запроса (JSON-данные).
        :param expected_status: Ожидаемый статус-код (по умолчанию 200).
        :param need_logging: Флаг для логирования (по умолчанию True).
        :return: Объект ответа requests.Response.
        """
        url = f"{self.base_url}{endpoint}"
        if isinstance(data, BaseModel):
            data = json.loads(data.model_dump_json(exclude_unset=True))
        response = self.session.request(method, url, json=data, params=params)
        if need_logging:
            self.log_request_and_response(response)
        if response.status_code != expected_status:
            raise ValueError(f"Unexpected status code: {response.status_code}. Expected: {expected_status}")
        return response

    # Приватный метод (начинается с _) для обновления заголовков сессии

    def _update_session_headers(self, session, **kwargs):
        """
        Обновление заголовков сессии.
        :param session: Объект requests.Session, предоставленный API-классом.
        :param kwargs: Дополнительные заголовки.
        """
        self.headers.update(kwargs)  # Обновляем базовые заголовки
        session.headers.update(self.headers)  # Обновляем заголовки в текущей сессии

    def log_request_and_response(self, response):
        """
        Логгирование запросов и ответов. Настройки логгирования описаны в pytest.ini
        Преобразует вывод в curl-like (-H хэдэеры), (-d тело)

        :param response: Объект response получаемый из метода "send_request"
        """
        try:
            request = response.request
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text
            if not is_success:
                self.logger.info(f"\tRESPONSE:"
                                 f"\nSTATUS_CODE: {RED}{response_status}{RESET}"
                                 f"\nDATA: {RED}{response_data}{RESET}")
        except Exception as e:
            self.logger.info(f"\nLogging went wrong: {type(e)} - {e}")
