from datetime import timedelta

from django.conf import settings


REFRESH_COOKIE_NAME = 'tm_refresh_token'


def refresh_cookie_max_age():
    lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=7))
    return int(lifetime.total_seconds())


def set_refresh_cookie(response, refresh_token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=refresh_cookie_max_age(),
        httponly=True,
        secure=settings.JWT_REFRESH_COOKIE_SECURE,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
        path='/',
    )


def clear_refresh_cookie(response) -> None:
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path='/',
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
    )


def attach_auth_response(response, data: dict):
    """Move refresh token into HttpOnly cookie; return access + user metadata only."""
    refresh = data.pop('refresh', None)
    if refresh:
        set_refresh_cookie(response, refresh)
    return response
