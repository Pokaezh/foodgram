from rest_framework import status
from rest_framework.response import Response 
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model


from food.models import CookUser
from api.serializers import UserSerializer, UserCreateSerializer, AvatarSerializer
from api.permissions import DeleteAndUdateOnlyAuthor



User = get_user_model()

class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = CookUser.objects.all()
    serializer_class = UserCreateSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = CookUser.objects.all()
    serializer_class = UserSerializer


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

    @action(
           methods=["put", "delete"],
           detail=False,
           url_path="me/avatar",
           permission_classes=[IsAuthenticated],
       )

    def avatar(self, request):
        """Добавление и удаление аватара"""
        user = request.user
        if request.method == "PUT":
            if 'avatar' not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        elif request.method == "DELETE":
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save() 
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response({"detail": "Аватар не найден."}, status=status.HTTP_404_NOT_FOUND) 

