import base64  
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from food.models import CookUser, Follow, Tag, Ingredient

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
        fields = "__all__"

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    
    class Meta:

        model = Ingredient
        fields = "__all__"