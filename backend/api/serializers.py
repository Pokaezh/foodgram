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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj in request.user.followers.all()
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
        fields =  "__all__"

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    amount = serializers.IntegerField(
        source='recipeIngredient.amount', read_only=True)
    
    class Meta:

        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id','recipe','ingredient',  'amount']

    def to_internal_value(self, data):
        ingredient_id = data.get('id')
        amount = data.get('amount')

        try:
            ingredient = Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError({'id': 'Ingredient not found.'})

        return {'ingredient': ingredient, 'amount': amount}

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""
    
    author = serializers.ReadOnlyField(source='author.id')
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    
    image = Base64ImageField (required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'image', 'name', 'text', 'cooking_time', 'author']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('ingredient')
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)

        return recipe

class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для деталей рецепта."""
    
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 
                  'name', 'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        # request = self.context.get('request')
        # if request and request.user.is_authenticated:
        #     return obj in request.user.favorites.all()  
        return False

    def get_is_in_shopping_cart(self, obj):
        # request = self.context.get('request')
        # if request and request.user.is_authenticated:
        #     return obj in request.user.shopping_cart.all()  
        return False

