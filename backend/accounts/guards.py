from django.conf import settings

from .models import UserRoleProfile
from .roles import get_user_role


def primary_super_admin_username() -> str:
    return (settings.PRIMARY_SUPER_ADMIN_USERNAME or 'techmart_admin').strip()


def is_primary_super_admin(user) -> bool:
    return bool(user and user.username == primary_super_admin_username())


def is_platform_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return get_user_role(user) == UserRoleProfile.ROLE_ADMIN


def validate_user_mutation(actor, target, *, new_role=None, deactivate=False, delete=False, demote_super=False):
    if not is_primary_super_admin(target):
        return None

    if actor and actor.pk != target.pk and is_platform_admin(actor):
        return None

    if delete or deactivate or demote_super:
        return 'Primary super admin account cannot be deleted or deactivated.'
    if new_role and new_role != UserRoleProfile.ROLE_ADMIN:
        return 'Primary super admin role cannot be changed.'
    return None
