import base64  
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from food.models import CookUser, Follow, Tag, Ingredient, Recipe, RecipeIngredient

# Модуль с функциями кодирования и декодирования base64

class Base64ImageField(serializers.ImageField):
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
    avatar = Base64ImageField (required=False, allow_null=True)

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
        # проверка подписки
        request = self.context.get('request')
        if request.user.is_authenticated:
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
        fields = ("id", "name", "slug")

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    
    class Meta:

        model = Ingredient
        fields = "__all__"

class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов с указанием количества."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    
    ingredients = IngredientAmountSerializer (many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), 
        many=True)
    image = Base64ImageField (required=False, allow_null=True)


    class Meta:

        model = Recipe
        fields = ["ingredients", "author", "tags", "image", "name", "text", "cooking_time"]

    def create(self, validated_data):
        # Создание рецепта
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user

        recipe = Recipe.objects.create(**validated_data)

        # Создаем связи между рецептом и ингредиентами
        recipe_ingredients = [
            RecipeIngredient(recipe=recipe, ingredient_id=ingredient['id'], amount=ingredient['amount'])
            for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        # Устанавливаем связи между рецептом и тегами
        recipe.tags.set(tags_data)

        return recipe

class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения деталей рецепта."""
    
    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ["id", "author", "tags", "ingredients", "name", "image", "text", "cooking_time"]