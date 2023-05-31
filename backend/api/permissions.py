from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission
from users.userroles import UserRoles


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.role == UserRoles.ADMIN)


class IsCurrentUserOrAdminOrGuest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.id == request.user
                or request.user.role == UserRoles.ADMIN)
