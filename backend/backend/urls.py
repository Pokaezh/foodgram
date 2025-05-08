
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter


from api.views import (
    UserViewSet,  
    UserCreateViewSet, 
    TagViewSet, 
    IngredientViewSet, 
    RecipeViewSet, 
    SubscriptionViewSet, 
    recipe_short_link)



router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("users", SubscriptionViewSet, basename="subscriptions")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path("r/<str:hash>/", recipe_short_link, name="recipe_short_link"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
