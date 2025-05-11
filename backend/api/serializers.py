
import base64
from django.core.files.base import ContentFile

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.validators import validate_recipe
from food.models import (
    CookUser,
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    ShoppingCart
)


class Base64ImageField(serializers.ImageField):
    "Модуль с функциями кодирования и декодирования base64"
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCreateSerializer(BaseUserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta(BaseUserCreateSerializer.Meta):
        model = CookUser
        fields = BaseUserSerializer.Meta.fields


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta(BaseUserSerializer.Meta):
        model = CookUser
        fields = BaseUserSerializer.Meta.fields + (
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, following=obj).exists()
        return False

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара."""

    avatar = Base64ImageField()

    class Meta:

        model = CookUser
        fields = ("avatar",)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:

        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    amount = serializers.IntegerField(
        source='recipeIngredient.amount', read_only=True)

    class Meta:

        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и количества ингредиентов."""
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'name', 'measurement_unit']

    def to_internal_value(self, data):
        ingredient_id = data.get('id')
        amount = data.get('amount')

        try:
            ingredient = Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError({'id': 'Ingredient not found.'})

        return {'ingredient': ingredient, 'amount': amount}


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    author = serializers.ReadOnlyField(source='author.id')
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author']

    def validate(self, attrs):
        validate_recipe(attrs)
        return attrs

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('ingredient')
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            for ingredient_data in ingredients_data:
                ingredient = ingredient_data.pop('ingredient')
                amount = ingredient_data['amount']

                recipe_ingredient, created = (
                    RecipeIngredient.objects.update_or_create(
                        recipe=instance,
                        ingredient=ingredient,
                        defaults={'amount': amount}))

        instance.save()
        return instance


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для деталей рецепта."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request.user.is_authenticated else None
        return Favorite.objects.filter(
            user=user, recipe=obj).exists() if user else False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = representation['image'] or ''
        return representation

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeMinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = Favorite

        fields = ['id', 'name', 'image', 'cooking_time']


class UserSubscribeSerializer(UserSerializer):
    """"Сериализатор для предоставления информации
    о подписках пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = CookUser
        fields = ('email', 'id', 'username', 'first_name', 'avatar',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = (
            'email', 'avatar', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeMinSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отписки от пользователей."""

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubscribeSerializer(
            instance.following, context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже добавлен в список покупок",
            )
        ]

    def to_representation(self, instance):
        """Представление объекта."""
        recipe = instance.recipe
        return {
            "id": recipe.id,
            "name": recipe.name,
            "image": recipe.image.url if recipe.image else None,
            "cooking_time": recipe.cooking_time
        }
