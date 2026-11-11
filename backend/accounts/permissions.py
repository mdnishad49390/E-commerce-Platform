from rest_framework.permissions import BasePermission

from .guards import is_platform_admin
from .models import UserRoleProfile
from .roles import get_user_role


class IsSuperAdminOrAdmin(BasePermission):
    """Superuser bypasses all checks; admins pass permission gates."""

    def has_permission(self, request, view):
        return is_platform_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        return is_platform_admin(request.user)


class IsAdmin(IsSuperAdminOrAdmin):
    pass


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_user_role(request.user) == UserRoleProfile.ROLE_EMPLOYEE
        )


class IsAdminOrEmployee(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return get_user_role(request.user) in {
            UserRoleProfile.ROLE_ADMIN,
            UserRoleProfile.ROLE_EMPLOYEE,
        }


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_user_role(request.user) == UserRoleProfile.ROLE_CUSTOMER
        )
