from rest_framework import filters as drf_filters
from django_filters import rest_framework as filters
from food.models import Recipe


class NameFilter(drf_filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='icontains')

    class Meta:
        model = Recipe
        fields = ['tags', 'author']