from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class RecipePagination(PageNumberPagination):
    page_size = 10  # Количество объектов на странице по умолчанию
    page_size_query_param = 'limit'  # Количество объектов на странице
    max_page_size = 100  # Максимальное количество объектов на странице
