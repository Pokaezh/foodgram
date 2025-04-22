from rest_framework import filters, status, viewsets
from rest_framework.response import Response 
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend


from food.models import CookUser, Tag, Ingredient, Recipe
from api.serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    AvatarSerializer, 
    TagSerializer, 
    IngredientSerializer, 
    RecipeCreateSerializer, 
    RecipeDetailSerializer
    )
from api.permissions import DeleteAndUdateOnlyAuthor
from api.filters import NameFilter



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


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = (NameFilter, DjangoFilterBackend)
    search_fields = ('^name',)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', ]:
            return RecipeCreateSerializer
        return RecipeDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, 
            context={'request': request}) 
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)

        detail_serializer = RecipeDetailSerializer(
            recipe, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        
        detail_serializer = RecipeDetailSerializer(
            recipe, context={'request': request}
        )
        return Response(detail_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

