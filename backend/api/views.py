from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly

from food.models import CookUser
from api.serializers import UserSerializer, UserCreateSerializer


class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = CookUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = CookUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
