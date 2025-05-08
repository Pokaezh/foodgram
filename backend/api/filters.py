from rest_framework import filters as drf_filters
from django_filters import rest_framework as filters
from food.models import Ingredient, Recipe, Tag



class NameFilter(drf_filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']