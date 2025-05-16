from io import StringIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import NameFilter, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import DeleteAndUdateOnlyAuthor
from api.serializers import (AvatarSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeDetailSerializer, ShoppingCartSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserCreateSerializer, UserSerializer,
                             UserSubscribeSerializer)
from food.models import (CookUser, Favorite, Follow, Ingredient, Recipe,
                         RecipeIngredient, ShoppingCart, Tag)

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
        permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Добавление и удаление аватара"""
        user = request.user
        if request.method == "PUT":
            if "avatar" not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == "DELETE":
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(
                {"detail": "Аватар не найден."},
                status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        permission_classes=[IsAuthenticated],)
    def subscribe(self, request, id=None):
        """Подписка и отписка на пользователей"""

        author = get_object_or_404(CookUser, id=id)

        if request.method == "POST":
            serializer = SubscriptionSerializer(
                data={"user": request.user.id, "following": author.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not request.user.following.filter(following=author).exists():
            return Response(
                {"errors": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Follow.objects.get(user=request.user, following=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def subscriptions(self, request):
        """Просмотр подписок"""
        if request.user.is_authenticated:
            queryset = User.objects.filter(followers__user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscribeSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscribeSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


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
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return RecipeCreateSerializer
        return RecipeDetailSerializer

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAuthenticated()]
        elif self.action == "favorite":
            return [IsAuthenticated()]
        elif self.action == "shopping_cart":
            return [IsAuthenticated()]
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [DeleteAndUdateOnlyAuthor()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)

        detail_serializer = RecipeDetailSerializer(
            recipe, context={"request": request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        detail_serializer = RecipeDetailSerializer(
            recipe, context={"request": request}
        )
        return Response(detail_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="get-link")
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

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()

        if request.method == "POST":
            # Добавление в избранное
            favorite, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe)
            favorite_serializer = FavoriteSerializer(
                favorite, context={"request": request})
            if created:
                return Response(
                    favorite_serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"status": "already in favorites"},
                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            # Удаление из избранного
            try:
                favorite = Favorite.objects.get(
                    user=request.user, recipe=recipe)
                favorite.delete()
                return Response(
                    {"status": "removed from favorites"},
                    status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {"status": "not in favorites"},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из корзины."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        shopping_cart_item = user.shopping_user.filter(recipe=recipe).first()

        if request.method == "POST":
            if shopping_cart_item:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            shopping_cart_item = ShoppingCart.objects.create(
                user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(shopping_cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            if not shopping_cart_item:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            shopping_cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивает список ингредиентов из корзины."""
        ingredients = self._get_shopping_cart_ingredients(request.user)
        if not ingredients:
            return Response(
                {"error": "Корзина пуста."},
                status=status.HTTP_400_BAD_REQUEST)
        return self._generate_shopping_cart_response(ingredients)

    def _get_shopping_cart_ingredients(self, user):
        """Получает список ингредиентов для списка покупок."""
        return (
            RecipeIngredient.objects.filter(recipe__shopping_recipe__user=user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )

    def _generate_shopping_cart_response(self, ingredients):
        """Создаёт список покупок."""
        shopping_list = StringIO()
        shopping_list.write("Список покупок:\n\n")
        for ingredient in ingredients:
            shopping_list.write(
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}\n"
            )

        response = HttpResponse(
            shopping_list.getvalue(),
            content_type="text/plain")
        response[
            "Content-Disposition"] = "attachment; filename='shopping_list.txt'"
        return response


@api_view(["GET"])
@permission_classes([AllowAny])
def recipe_short_link(request, hash):
    """Возвращает рецепт по короткой ссылке."""
    recipe = get_object_or_404(Recipe, short_link=hash)
    return redirect(f"/recipes/{recipe.id}/")
