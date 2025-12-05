import pytest

@pytest.mark.api
class TestDeleteWithRole:
    """ Тесты для удаления фильмов """

    @pytest.mark.slow
    @pytest.mark.parametrize("role_name, expected_status",
                             [("common_user", 403),
                              ("super_admin", 200)
                              ])
    def test_delete_movie_by_role(self, request, role_name, expected_status, created_movie):
        """ Тест для удаления фильмов под разными ролями """
        movie_id, created_data, _ = created_movie
        role = request.getfixturevalue(role_name) # Познакомился с этой конструкцией, без неё хз как делать)
        role.api.movies_api.delete_movie(movie_id, expected_status)

