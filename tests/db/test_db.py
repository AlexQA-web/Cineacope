# Можете сделать рандомный тестовый файл для проверки работы фикстуры
# Так сказать - поиграться
import pytest
from tests.api.test_movie import TestMoviesAPIPositive


@pytest.mark.db
class TestDB:
    def test_db_requests(self, super_admin, db_helper, created_test_user):
        assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
        assert db_helper.user_exists_by_email("api1@gmail.com")

    #TODO Сделать тест на создание фильма в БД, удаление через АПИ и проверка на удаление в БД
    def test_create_movie_db(self, super_admin,db_helper, movie_data_db):
        movie = db_helper.create_movie_in_db(movie_data_db)
        movie_id = movie.id
        fetched_movie = db_helper.get_movie_by_id(movie_id)
        assert fetched_movie.id == movie_id
        created_movie_tuple = (movie_id, {}, None)
        TestMoviesAPIPositive.test_delete_movie(self, super_admin=super_admin, created_movie=created_movie_tuple)
        deleted_movie = db_helper.get_movie_by_id(movie_id)
        assert deleted_movie is None