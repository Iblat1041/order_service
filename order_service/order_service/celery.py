import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

# Создаём экземпляр Celery
app = Celery('order_service')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически регистрируем задачи из всех приложений
app.autodiscover_tasks()
