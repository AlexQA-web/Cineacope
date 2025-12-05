import pytest
import requests

from conftest import api_manager, super_admin, common_user
from utils.data_generator import DataGenerator
from constants.constants import MOVIES_ENDPOINT

@pytest.mark.api
class TestMoviesAPIPositive:

    @pytest.mark.smoke
    def test_create_movie(self, super_admin, movie_data):
        """ Создаем фильм под super_admin"""
        response = super_admin.api.movies_api.create_movie(movie_data, expected_status=201)
        data = response.json()

        assert data["name"] == movie_data["name"]
        assert "id" in data

    @pytest.mark.slow
    @pytest.mark.regression
    @pytest.mark.parametrize("role_name", ["super_admin", "common_user"])
    def test_get_movie_by_id(self, role_name, request, created_movie):
        """ Получаем данные о фильме под super_admin """
        role = request.getfixturevalue(role_name)
        movie_id, created_data, _ = created_movie

        response = role.api.movies_api.get_movie_by_id(movie_id, expected_status=200)
        data = response.json()

        assert data["id"] == movie_id
        assert data["name"] == created_data["name"]

    #TODO В тесте на /update хорошо бы проверить саму сущность фильма через /get, а не только response проверять
    @pytest.mark.slow
    @pytest.mark.regression
    def test_update_movie(self, super_admin, created_movie):
        movie_id, _, _ = created_movie
        updated = {"name": "Updated name"}

        response = super_admin.api.movies_api.update_movie(movie_id, updated, expected_status=200)
        data = response.json()
        assert data["name"] == "Updated name"
        # TODO Добавлена проверка по GET
        get_response = super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=200)
        get_data = get_response.json()
        assert data["id"] == movie_id
        assert data["name"] == get_data["name"]

    def test_create_movie_without_required_field(self, super_admin, movie_data):
        bad_data = movie_data.copy()
        bad_data.pop("name")  # обязательное поле

        super_admin.api.movies_api.create_movie(
            bad_data,
            expected_status=400
        )

    @pytest.mark.regression
    def test_get_movies_with_filter_by_name(self, super_admin, created_movie):
        _, created_data, _ = created_movie
        # TODO Исправил с filters на params
        response = super_admin.api.movies_api.get_movies(
            params={"name": created_data["name"]},
            expected_status= 200
        )
        data = response.json()
        movies = data["movies"]

        assert isinstance(movies, list)
        assert len(movies) > 0

    #TODO Сделать позитивный тест на /delete
    @pytest.mark.regression
    def test_delete_movie(self, super_admin, created_movie):
        movie_id, _, _ = created_movie

        super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)
        get_response = super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert get_response.json()["error"] == "Not Found"

@pytest.mark.api
class TestMoviesNegative:

    def test_get_movies_unauthorized(self, requester_movies):
        response = requester_movies.send_request(
            method="GET",
            endpoint= MOVIES_ENDPOINT,
            data=DataGenerator.query_params(),
            expected_status=200
        )

        data = response.json()
        assert "movies" in data
        assert isinstance(data["movies"], list)

    def test_create_movie_unauthorized(self, requester_movies, movie_data):

        response = requester_movies.send_request(
            method="POST",
            endpoint= MOVIES_ENDPOINT,
            data=movie_data,
            expected_status=401
        )
        data = response.json()
        assert "message" in data
        assert data["message"] == "Unauthorized"

    def test_create_movie_with_empty_name(self, super_admin, movie_data):
        bad_data = movie_data.copy()
        bad_data["name"] = ""

        response = super_admin.api.movies_api.create_movie(
            bad_data,
            expected_status=400,
        )
        data = response.json()

        assert "message" in data
        assert data["message"] == ['name should not be empty']

    def test_create_movie_with_invalid_price_type(self, super_admin, movie_data):
        bad_data = movie_data.copy()
        bad_data["price"] = "not a number"

        response = super_admin.api.movies_api.create_movie(
            bad_data,
            expected_status=400,
        )
        data = response.json()

        assert "message" in data
        assert data["message"] == ['Поле price должно быть числом']

    def test_get_movie_not_found(self, super_admin):
        non_existing_id = 999999

        response = super_admin.api.movies_api.get_movie_by_id(
            non_existing_id,
            expected_status=404,
        )
        data = response.json()
        assert data["message"] == "Фильм не найден"
        assert data.get("statusCode") == 404

    @pytest.mark.slow
    def test_create_movie(self, common_user, movie_data):
        common_user.api.movies_api.create_movie(movie_data, expected_status=403).json()