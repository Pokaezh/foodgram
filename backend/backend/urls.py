from rest_framework import routers

from django.contrib import admin
from django.urls import include, path

from api.views import UserViewSet, UserCreateViewSet

router = routers.DefaultRouter()
#router.register(r'users', UserCreateViewSet, basename='user-create') 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]
