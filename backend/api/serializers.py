from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from food.models import CookUser


class UserCreateSerializer(BaseUserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = CookUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password")
    # def validate_first_name(self, value):
    #     if not value:
    #         raise serializers.ValidationError("Это поле обязательно.")
    #     return value


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        model = CookUser
        fields = (
              "email",
              "id",
              "username",
              "first_name",
              "last_name",)

    # def get_is_subscribed(self, obj):
    #     # Логика для определения подписки (например, проверка на наличие подписки)
    #     return False  # надо что-то придумать

    # is_subscribed = serializers.SerializerMethodField()
    # avatar = serializers.ImageField(source='profile.avatar')
            