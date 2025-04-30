from rest_framework import filters as drf_filters
from django_filters import rest_framework as filters
from food.models import Recipe


class NameFilter(drf_filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='icontains')
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']