from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserViewSet, recipe_short_link)

v1_router = DefaultRouter()
v1_router.register(r"users", UserViewSet, basename="users")
v1_router.register("tags", TagViewSet, basename="tags")
v1_router.register("ingredients", IngredientViewSet, basename="ingredients")
v1_router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(v1_router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path("r/<str:hash>/", recipe_short_link, name="recipe_short_link"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
