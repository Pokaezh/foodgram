from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import BasePermission

User = get_user_model()


class AllowAnyExceptMe(BasePermission):
    """
    Разрешает доступ всем пользователям, кроме доступа к /api/users/me/
    """
    def has_permission(self, request, view):
        # Разрешить доступ ко всем эндпоинтам
        if request.method in ['GET'] and view.action in ['list', 'retrieve']:
            return True
        # Запретить доступ к /api/users/me/
        if view.action == 'me':
            return False
        return True


class DeleteAndUdateOnlyAuthor(permissions.BasePermission):
    """
    Разрешение для проверки, является ли пользователь автором объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
