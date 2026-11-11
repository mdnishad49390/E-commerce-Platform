"""
Django settings for TechMart / config project.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name: str, default: str = '') -> list[str]:
    raw = os.getenv(name, default)
    return [part.strip() for part in raw.split(',') if part.strip()]


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-only-change-in-production')
DEBUG = env_bool('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = env_list(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,tech-mart-7vuc.onrender.com',
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products',
    'accounts',
    'rest_framework',
    'corsheaders',
    'orders',
    'wishlist',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=env_bool('DATABASE_SSL_REQUIRE', default=False),
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@techmart.local')
EMAIL_BRAND_NAME = os.getenv('EMAIL_BRAND_NAME', 'TechMart')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID', '')
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID', '')
APPLE_KEY_ID = os.getenv('APPLE_KEY_ID', '')
APPLE_PRIVATE_KEY = os.getenv('APPLE_PRIVATE_KEY', '')

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

_default_cors = (
    'http://localhost:5173,http://127.0.0.1:5173,'
    'https://tech-mart-7vuc.onrender.com'
)
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', _default_cors)

_regex_env = os.getenv('CORS_ALLOWED_ORIGIN_REGEXES', '').strip()
if _regex_env:
    CORS_ALLOWED_ORIGIN_REGEXES = [part.strip() for part in _regex_env.split('|') if part.strip()]
else:
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r'^https://.*\.vercel\.app$',
        r'^https://.*\.onrender\.com$',
    ]

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', _default_cors)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_MINUTES', '15'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_DAYS', '7'))),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

JWT_REFRESH_COOKIE_SECURE = env_bool('JWT_REFRESH_COOKIE_SECURE', default=not DEBUG)
JWT_REFRESH_COOKIE_SAMESITE = os.getenv('JWT_REFRESH_COOKIE_SAMESITE', 'Strict')

FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173').rstrip('/')

PRIMARY_SUPER_ADMIN_USERNAME = os.getenv('PRIMARY_SUPER_ADMIN_USERNAME', 'techmart_admin')

SSLCOMMERZ_STORE_ID = os.getenv('SSLCOMMERZ_STORE_ID', '')
SSLCOMMERZ_STORE_PASSWORD = os.getenv('SSLCOMMERZ_STORE_PASSWORD', '')
SSLCOMMERZ_SANDBOX = env_bool('SSLCOMMERZ_SANDBOX', default=True)
SSLCOMMERZ_API_ROOT = os.getenv(
    'SSLCOMMERZ_API_ROOT',
    'https://sandbox.sslcommerz.com' if SSLCOMMERZ_SANDBOX else 'https://securepay.sslcommerz.com',
)

if DEBUG:
    SECURE_SSL_REDIRECT = False
else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
