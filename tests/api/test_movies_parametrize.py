import pytest

@pytest.mark.api
class TestMoviesFilters:
    """ Параметризированные тесты фильтрации фильмов """

    @pytest.mark.regression
    @pytest.mark.parametrize("page_size,page", [
        (5, 1),
        (10, 1),
        (20, 2),
    ])
    def test_get_movies_pagination(self, super_admin, page_size, page):
        """ Тест постраничного списка фильмов """
        params = {"pageSize": page_size, "page": page}
        response = super_admin.api.movies_api.get_movies(params=params).json()

        assert response["page"] == page

    @pytest.mark.regression
    @pytest.mark.parametrize("min_price,max_price", [
        (1, 100),
        (100, 500),
        (500, 1000),
        (1, 1000),
    ])
    def test_get_movies_price_range(self, super_admin, min_price, max_price):
        """ Тест фильтров по диапазону цен """
        params = {"minPrice": min_price, "maxPrice": max_price}
        response = super_admin.api.movies_api.get_movies(params=params).json()

        for movie in response["movies"]:
            assert min_price <= movie["price"] <= max_price

    @pytest.mark.parametrize("location", ["MSK", "SPB"])
    def test_get_movies_by_location(self, super_admin, location):
        """ Тест фильтров по локации """
        params = {"locations": location}
        response = super_admin.api.movies_api.get_movies(params=params).json()

        for movie in response["movies"]:
            assert movie["location"] == location

    @pytest.mark.regression
    @pytest.mark.parametrize("min_price,max_price,location,published,genre_id", [
        (100, 500, "MSK", True, 1),
        (200, 800, "SPB", True, 2),
        (1, 1000, "MSK", True, 5),
    ])
    def test_get_movies_combined_filters(self, super_admin, min_price, max_price, location, published, genre_id):
        """ Тест для нескольких фильтров """
        params = {
            "minPrice": min_price,
            "maxPrice": max_price,
            "locations": location,
            "published": published,
            "genreId": genre_id
        }
        response = super_admin.api.movies_api.get_movies(params=params).json()

        for movie in response["movies"]:
            assert min_price <= movie["price"] <= max_price
            assert movie["location"] == location
            assert movie["published"] == published
            assert movie["genreId"] == genre_id
