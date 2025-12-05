# Импорт модуля json для работы с JSON-данными (сериализация/десериализация)
import json
# Импорт библиотеки requests для выполнения HTTP-запросов
import requests
# Импорт модуля logging для логирования событий и отладки
import logging
# Импорт модуля os для работы с операционной системой (переменные окружения, пути)
import os


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
        response = self.session.request(method, url, json=data, params=params, headers=self.headers)
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


    def log_request_and_response(self, response): # Метод для детального логирования HTTP-запросов и ответов в формате curl
        """
        Логирование запросов и ответов.
        :param response: Объект ответа requests.Response.
        """
        try:

            request = response.request # Извлекаем объект запроса из ответа (response.request содержит информацию об отправленном запросе)

            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            # Формируем строку с заголовками запроса в формате curl (-H 'header: value')
            # Перебираем все заголовки из request.headers (словарь), соединяем через перенос строки с обратным слэшем
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            # Получаем полное имя теста из переменной окружения PYTEST_CURRENT_TEST, убираем " (call)" из конца
            # Добавляем префикс "pytest " для формирования команды запуска теста
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"


            body = "" # Инициализируем пустую строку для тела запроса

            if hasattr(request, 'body') and request.body is not None: # Проверяем, есть ли у объекта request атрибут body и не равен ли он None
                if isinstance(request.body, bytes): # Если тело запроса в байтах - декодируем в UTF-8 строку
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else '' # Формируем curl-параметр для тела запроса (-d 'body'), если тело не пустое ('{}')

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}") # Логируем заголовок секции REQUEST с разделителем из знаков "="
            # Логируем информацию о запросе: имя теста зелёным цветом и curl-команду для воспроизведения запроса
            # Включает метод (GET/POST), URL, заголовки и тело запроса
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code  # Извлекаем статус-код из ответа (например, 200, 404, 500)
            is_success = response.ok # Проверяем успешность запроса (response.ok - True для статусов 200-299)
            response_data = response.text # Получаем тело ответа как текст (строку)

            try:
                # Пытаемся распарсить текст ответа как JSON и форматируем с отступами в 4 пробела
                # ensure_ascii=False позволяет корректно отображать кириллицу и другие не-ASCII символы
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:  # Если ответ не является валидным JSON - игнорируем ошибку
                pass  # Оставляем response_data как есть (в виде обычного текста)

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")  # Логируем заголовок секции RESPONSE с разделителем из знаков "="

            if not is_success: # Если запрос не успешен (статус 400+)
                self.logger.info(  # Логируем статус и данные красным цветом (для привлечения внимания к ошибке)
                    f"\tSTATUS_CODE: {RED}{response_status}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:  # Если запрос успешен
                self.logger.info(  # Логируем статус зелёным цветом, а данные - обычным
                    f"\tSTATUS_CODE: {GREEN}{response_status}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n") # Логируем завершающий разделитель из 80 знаков "="
        except Exception as e:  # Перехватываем любые исключения, возникшие при логировании
            self.logger.error(f"\nLogging failed: {type(e)} - {e}") # Логируем сообщение об ошибке с типом исключения и текстом ошибки
