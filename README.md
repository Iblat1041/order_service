# REST API для управления складом и заказами

Проект представляет собой RESTful API для комплексного управления складской логистикой и заказами. Решение построено на Django и Django REST Framework и предоставляет полный цикл работы с товарами: от управления поставщиками и контроля остатков на складе до обработки заказов покупателей.

Ключевые особенности включают систему регистрации пользователей с подтверждением email, интеллектуальное управление заказами с автоматической проверкой наличия товаров, иерархическую организацию товарных категорий, а также автоматизированную отправку email-уведомлений.

API обеспечивает безопасное взаимодействие через token-аутентификацию и предлагает полную документацию в формате OpenAPI 3.0 с интерактивным интерфейсом Swagger UI для удобного тестирования и интеграции.

## Стек технологии

*   **Backend:**   Django 4.2.5, Django REST Framework 3.14.0
*   **База данных:**   PostgreSQL (SQLite для локальной разработки)
*   **Кэширование:**   Redis
*   **Фоновые задачи:**   Celery 5.3.4, Celery Beat 2.5.0
*   **Документация API:**   DRF Spectacular (OpenAPI 3.0)
*   **Контейнеризация:**   Docker, Docker Compose
*   **Дополнительно:**   python-dotenv для управления переменными окружения

## Установка локально

1.  Клонируйте репозиторий:
    ```bash
    git clone <ваш-репозиторий>
    cd order-service
    ```

2.  Создайте файл `.env` в корне проекта. Образец env.example:

3.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4.  Выполните миграции:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  Запустите сервер, Celery и Celery Beat:
    ```bash
    # Сервер
    python manage.py runserver

    # В отдельных терминалах:
    # Celery worker
    celery -A order_service worker -l info
    # Celery beat
    celery -A order_service beat -l info
    ```

6.  **Доступ к API:**
    API доступно по адресу: http://localhost:8000/api/

## Установка с Docker

1.  Создайте файл `.env`.
```bash
Добавьте настройки superuser
Настройки Email
SECRET_KEY
```

2.  Запустите Docker Compose:
    ```bash
    docker-compose up --build
    ```

## Документация API
*   **Swagger UI : http://localhost:8000/api/schema/swagger-ui/**

*   **ReDoc : http://localhost:8000/api/schema/redoc/**

## Структура проекта
```bash
.
├── celerybeat-schedule
├── docker-compose.yml
├── Dockerfile
├── order_service
│   ├── api
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── __pycache__
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── tasks.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── db.sqlite3
│   ├── manage.py
│   ├── order_service
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── structure.txt
├── README.md
├── requirements.txt
```

