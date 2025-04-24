from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from food.models import CookUser, Ingredient, Tag, Recipe

User = get_user_model()


@admin.register(User)
class CookUserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name", 
        "author", 
        "image", 
        "text", 
        "pub_date", 
        "get_ingredients", 
        "get_tags", 
        "cooking_time")

    def get_ingredients(self, obj):
        return ", ".join([ingredient.name for ingredient in obj.ingredients.all()])
    get_ingredients.short_description = 'Ingredients'

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'


       