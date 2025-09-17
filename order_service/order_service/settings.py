import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent

SECRET_KEY: str = os.getenv(
    'SECRET_KEY',
    'django-insecure--k#i2==p2rgsshf5$x0@2vm-legyxb+s6946jc4c+@z02u32q3'
)

DEBUG: bool = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS: List[str] = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,web').split(',')

INSTALLED_APPS: List[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Добавляем Django REST Framework
    'rest_framework.authtoken',  # Добавляем токен-аутентификацию
    'django_redis',
    'django_celery_beat',
    'api.apps.ApiConfig',
]


MIDDLEWARE: List[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
"""Список middleware для обработки запросов."""

ROOT_URLCONF: str = 'order_service.urls'
"""Основной модуль маршрутов URL."""

TEMPLATES: List[Dict[str, Any]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION: str = 'order_service.wsgi.application'
"""Точка входа для WSGI-приложения."""

IS_LOCAL: bool = os.getenv('IS_LOCAL', 'True') == 'True'
"""Флаг локальной разработки."""

if IS_LOCAL:
    DATABASES: Dict[str, Dict[str, Any]] = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES: Dict[str, Dict[str, Any]] = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.getenv('POSTGRES_DB', 'postgres'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'db'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
"""Настройки базы данных (SQLite для локальной разработки, PostgreSQL для продакшена)."""

AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
"""Валидаторы паролей для пользователей."""

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',  # Добавьте это
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# Настройки кэширования с django-redis
CACHES: Dict[str, Dict[str, Any]] = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Настройки отправки писем
EMAIL_BACKEND: str = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST: str = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')
EMAIL_PORT: int = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS: bool = True
EMAIL_HOST_USER: str = os.getenv('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD: str = os.getenv('EMAIL_HOST_PASSWORD', 'your-email-password')
DEFAULT_FROM_EMAIL: str = EMAIL_HOST_USER
SITE_URL: str = os.getenv('SITE_URL', 'http://localhost:8000')

# Настройки Celery
CELERY_BROKER_URL: str = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND: str = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT: List[str] = ['json']
CELERY_TASK_SERIALIZER: str = 'json'
CELERY_RESULT_SERIALIZER: str = 'json'
CELERY_TIMEZONE: str = 'Europe/Moscow'

# Настройки Celery Beat
CELERY_BEAT_SCHEDULE: Dict[str, Dict[str, Any]] = {
    'check-email-verification': {
        'task': 'api.tasks.check_email_verification',
        'schedule': 3600.0,  # Каждые час
    },
}

LANGUAGE_CODE: str = 'ru-RU'

TIME_ZONE: str = 'Europe/Moscow'

USE_I18N: bool = True

USE_TZ: bool = True

STATIC_URL: str = 'static/'

STATIC_ROOT: str = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

STATIC_ROOT: str = os.path.join(BASE_DIR, 'staticfiles')
