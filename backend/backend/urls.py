from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter


from api.views import UserViewSet,  UserCreateViewSet


# router = DefaultRouter()
# router.register('users', UserViewSet, basename="users")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('djoser.urls')),
    # path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )