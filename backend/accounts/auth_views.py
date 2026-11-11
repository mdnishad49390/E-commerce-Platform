from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .jwt_cookies import REFRESH_COOKIE_NAME, attach_auth_response, clear_refresh_cookie, set_refresh_cookie
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            attach_auth_response(response, response.data)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(REFRESH_COOKIE_NAME) or request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'Refresh token missing.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data={'refresh': refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            response = Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)
            clear_refresh_cookie(response)
            return response

        data = dict(serializer.validated_data)
        response = Response(data, status=status.HTTP_200_OK)
        new_refresh = data.get('refresh')
        if new_refresh:
            set_refresh_cookie(response, new_refresh)
        return response


class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        response = Response({'message': 'Logged out.'}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)
        return response
