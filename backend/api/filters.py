from django_filters import rest_framework as filters
from food.models import Recipe, Tag
from rest_framework import filters as drf_filters


class NameFilter(drf_filters.SearchFilter):
    search_param = "name"


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["tags", "author", "is_favorited", "is_in_shopping_cart"]

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        request = self.request
        user = request.user

        if user.is_authenticated and value:
            return queryset.filter(shopping_recipe__user=user)
        return queryset
