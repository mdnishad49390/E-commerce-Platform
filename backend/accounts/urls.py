from django.urls import path

from .auth_views import CookieTokenRefreshView, CustomTokenObtainPairView, LogoutAPIView
from .views import (
    AppleLoginAPIView,
    ChangePasswordAPIView,
    GoogleLoginAPIView,
    MyProfileAPIView,
    RegisterAPIView,
)


urlpatterns = [
    path(
        'register/',
        RegisterAPIView.as_view(),
        name='register'
    ),
    path(
        'login/',
        CustomTokenObtainPairView.as_view(),
        name='login'
    ),
    path(
        'google-login/',
        GoogleLoginAPIView.as_view(),
        name='google-login'
    ),
    path(
        'apple-login/',
        AppleLoginAPIView.as_view(),
        name='apple-login'
    ),
    path('profile/', MyProfileAPIView.as_view(), name='my-profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path(
        'token/refresh/',
        CookieTokenRefreshView.as_view(),
        name='token-refresh',
    ),
    path(
        'logout/',
        LogoutAPIView.as_view(),
        name='logout',
    ),
]