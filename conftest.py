from datetime import datetime
import requests
import pytest
from sqlalchemy.orm import Session
from api_clients.api_manager import ApiManager
from constants.constants import AUTH_BASE_URL, REGISTER_ENDPOINT, MOVIES_BASE_URL
from constants.roles import Roles
from custom_requester.custom_requester import CustomRequester
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
from entities.user import User
from models.base_models import TestUser
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator

@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )

@pytest.fixture
def registration_user_data():
    """Данные для регистрации пользователя """
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value],
    }

@pytest.fixture
def registered_user(test_user, requester_auth):
    """Всегда новая регистрация """
    response = requester_auth.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )

    response_data = response.json()
    user_data = test_user.model_dump()
    user_data["id"] = response_data["id"]
    user_data["roles"] = response_data.get("roles", ["USER"])

    return user_data


@pytest.fixture
def requester_auth():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=AUTH_BASE_URL)

@pytest.fixture
def requester_movies():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=MOVIES_BASE_URL)

@pytest.fixture
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)

@pytest.fixture
def movie_data():
    """
    Фикстура создания данных для создания фильма
    """
    return {
        "name": DataGenerator.generate_movie_name(),
        "imageUrl": DataGenerator.generate_movie_image_url(),
        "price": DataGenerator.generate_movie_price(),
        "description": DataGenerator.generate_movie_description(),
        "location": DataGenerator.generate_movie_location(),
        "published": DataGenerator.generate_movie_published(),
        "genreId": DataGenerator.generate_movie_genre_id(), # тут рандом 1..5
        "rating": 1
    }
@pytest.fixture
def movie_data_db():
    """
    Фикстура создания данных для создания фильма
    """
    return {
        "name": DataGenerator.generate_movie_name(),
        "image_url": DataGenerator.generate_movie_image_url(),
        "price": DataGenerator.generate_movie_price(),
        "description": DataGenerator.generate_movie_description(),
        "location": DataGenerator.generate_movie_location(),
        "published": DataGenerator.generate_movie_published(),
        "genre_id": DataGenerator.generate_movie_genre_id(), # тут рандом 1..5
        "rating": 1,
        "created_at": datetime.now()
    }

@pytest.fixture
def created_movie(super_admin, movie_data):
    """Фикстура для создания фильма и его дальнейшего удаления"""
    response = super_admin.api.movies_api.create_movie(movie_data)
    data = response.json()
    movie_id = data["id"]

    yield movie_id, data, movie_data
    #Делаю попытку удалить фильм, после создания.
    try:
        super_admin.api.movies_api.delete_movie(movie_id)
    except ValueError:
        pass  # Если фильм уж удален методом делит то ошибки не будет. Тест пройдёт, наверное.

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def creation_user_data(test_user):
    creation_user = test_user.model_copy(update={
        "verified": True,
        "banned": False,
    })
    return creation_user

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def user_id(api_manager, common_user):
    login_data = {"email": common_user.email, "password": common_user.password}
    response = api_manager.auth_api.login_user(login_data).json()

    return response["user"]["id"]

@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)