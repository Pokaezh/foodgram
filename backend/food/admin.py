from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from food.models import CookUser, Ingredient

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
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")