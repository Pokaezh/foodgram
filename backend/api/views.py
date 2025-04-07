from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model


from food.models import CookUser
from api.serializers import UserSerializer, UserCreateSerializer
from api.permissions import DeleteAndUdateOnlyAuthor



User = get_user_model()

class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = CookUser.objects.all()
    serializer_class = UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CookUser.objects.all()
    serializer_class = UserSerializer

    # def get_permissions(self):
    #         # Если метод - POST, разрешаем доступ всем
    #     if self.request.method == 'POST':
    #         self.permission_classes = [IsAuthenticatedOrReadOnly]
    #     return super().get_permissions()

    def create(self, request):
        # Логика для создания пользователя
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def get_serializer_class(self):
        """Получить класс сериализатора."""
        if self.action in ("list", "retrieve", "me",):
            return UserSerializer

        return super().get_serializer_class()

    @action(
        methods=("GET",),
        detail=False,
        url_path="me",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Запрос пользователем своего профиля."""
        serializer = UserSerializer(request.user, context={"request": request})

        return Response(serializer.data)

    def update_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    # def get_permissions(self):
    #     if self.action == "me":
    #         self.permission_classes = [IsAuthenticated]
    #     return super().get_permissions()

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

