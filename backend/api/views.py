from rest_framework import filters, status, viewsets, permissions, pagination
from rest_framework.response import Response 
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend


from food.models import CookUser, Tag, Ingredient, Recipe, Favorite, Follow
from api.serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    AvatarSerializer, 
    TagSerializer, 
    IngredientSerializer, 
    RecipeCreateSerializer, 
    RecipeDetailSerializer,
    FavoriteSerializer,
    SubscriptionSerializer
    )
from api.permissions import DeleteAndUdateOnlyAuthor
from api.filters import NameFilter, RecipeFilter
from api.permissions import IsOwner, DeleteAndUdateOnlyAuthor
from api.pagination import RecipePagination



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
    serializer_class = RecipeDetailSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination
# pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAuthenticated()]
        elif self.action == 'favorite':  
            return [IsAuthenticated()]  
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [DeleteAndUdateOnlyAuthor()]
        return super().get_permissions() 
    

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response({
    #         "count": queryset.count(),
    #         "next": self.get_next_link(),
    #         "previous": self.get_previous_link(),
    #         "results": serializer.data
    #     })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)

        detail_serializer = RecipeDetailSerializer(
            recipe, context={'request': request}
        )
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
        
    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, id=pk)

        if not recipe.short_link:
            short_link = str(recipe.id)  
            recipe.short_link = short_link
            recipe.save(update_fields=["short_link"])

        scheme = request.scheme
        host = request.get_host()

        return Response(
            {"short-link": f"{scheme}://{host}/r/{recipe.short_link}"},
            status=status.HTTP_200_OK,
        )
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        
        if request.method == 'POST':
            # Добавление в избранное
            favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            favorite_serializer = FavoriteSerializer(favorite, context={'request': request})
            if created:
                return Response(favorite_serializer.data, status=status.HTTP_201_CREATED)
            return Response({'status': 'already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            # Удаление из избранного
            try:
                favorite = Favorite.objects.get(user=request.user, recipe=recipe)
                favorite.delete()
                return Response({'status': 'removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({'status': 'not in favorites'}, status=status.HTTP_400_BAD_REQUEST)

    # def get_next_link(self):
    #     if self.paginator and self.paginator.get_next_link():
    #         return self.paginator.get_next_link()
    #     return None

    # def get_previous_link(self):
    #     if self.paginator and self.paginator.get_previous_link():
    #         return self.paginator.get_previous_link()
    #     return None

@api_view(["GET"])
@permission_classes([AllowAny])
def recipe_short_link(request, hash):
    """Возвращает рецепт по короткой ссылке."""
    recipe = get_object_or_404(Recipe, short_link=hash)
    return redirect(f"/recipes/{recipe.id}/")

class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        user_to_follow = get_object_or_404(CookUser, id=pk)
        follow, created = Follow.objects.get_or_create(user=request.user, following=user_to_follow)

        if created:
            serializer = SubscriptionSerializer(user_to_follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Already subscribed.'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=True, methods=['delete'], url_path='subscribe')
    def unsubscribe(self, request, pk=None):
        user_to_unfollow = get_object_or_404(CookUser, id=pk)
        try:
            follow = Follow.objects.get(user=request.user, following=user_to_unfollow)
            follow.delete()
            return Response({'detail': 'Successfully unsubscribed.'}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({'detail': 'Not subscribed.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    
    
    def list_subscriptions(self, request):
        # Получение списка пользователей, на которых подписан текущий пользователь
        subscriptions = Follow.objects.filter(user=request.user).select_related('following')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

# class FavoritViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def create(self, request, recipe_id=None):
#         """Добавление рецепта в избранное."""
#         try:
#             recipe = Recipe.objects.get(id=recipe_id)
#         except Recipe.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)

#         if created:
#             serializer = FavoriteSerializer(favorite)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response({"detail": "Рецепт уже добавлен в избранное."}, status=status.HTTP_400_BAD_REQUEST)

#     def list(self, request):
#         """Просмотр списка избранных рецептов."""
#         favorites = Favorite.objects.filter(user=request.user)
#         serializer = FavoriteSerializer(favorites, many=True, context={'request': request})
#         return Response(serializer.data)

#     def destroy(self, request, recipe_id=None):
#         """Удаление рецепта из избранного."""
#         try:
#             favorite = Favorite.objects.get(user=request.user, recipe_id=recipe_id)
#             favorite.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Favorite.DoesNotExist:
#             return Response({"detail": "Рецепт не найден в избранном."}, status=status.HTTP_404_NOT_FOUND)