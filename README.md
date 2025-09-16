# Сервис заказов со склада

REST API для управления поставщиками, товарами, остатками на складе, заказами и профилями покупателей. Проект построен на Django и Django REST Framework (DRF) и включает функциональность для регистрации пользователей с подтверждением email, управления заказами с проверкой остатков и автоматической отправкой писем.

## Основные функции

### Управление поставщиками
*   Создание, обновление и удаление поставщиков (с каскадным удалением связанных данных).

### Управление складом
*   Просмотр остатков товаров (с кэшированием через Redis).
*   Добавление товаров и управление их остатками.
*   Обновление и удаление товаров.

### Управление заказами
*   Создание заказов с проверкой наличия товаров на складе.
*   Отправка письма с подтверждением заказа на email покупателя.

### Управление пользователями и email
*   Регистрация покупателей с автоматическим созданием профиля.
*   Подтверждение email через токен.
*   Отправка напоминаний через 1 день и деактивация аккаунта через 2 дня, если email не подтвержден.

## Используемые технологии

*   **Backend:** Django 4.2.7, Django REST Framework 3.14.0
*   **База данных:** PostgreSQL 13 (SQLite для локальной разработки)
*   **Кэширование:** Redis 6
*   **Фоновые задачи:** Celery 5.3.6, Celery Beat 2.5.0
*   **Контейнеризация:** Docker, Docker Compose
*   **Дополнительно:** python-dotenv для управления переменными окружения

## Установка и запуск

### Требования

*   Python 3.12
*   Docker и Docker Compose (для контейнеризации)
*   SMTP-сервер (например, Gmail) для отправки писем
*   PostgreSQL и Redis (для продакшена)

### Установка локально

1.  Клонируйте репозиторий:
    ```bash
    git clone <ваш-репозиторий>
    cd order-service
    ```

2.  Создайте файл `.env` в корне проекта (пример):
    ```ini
    SECRET_KEY=your-secret-key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DB_ENGINE=django.db.backends.postgresql
    POSTGRES_DB=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=localhost
    DB_PORT=5432
    CELERY_BROKER_URL=redis://localhost:6379/0
    CELERY_RESULT_BACKEND=redis://localhost:6379/0
    REDIS_URL=redis://localhost:6379/1
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your-email@gmail.com
    EMAIL_HOST_PASSWORD=your-app-password
    SITE_URL=http://localhost:8000
    ```

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

### Установка с Docker

1.  Создайте файл `.env` (как указано выше, но с `DB_HOST=db` и `IS_LOCAL=False`).

2.  Запустите Docker Compose:
    ```bash
    docker-compose up --build
    ```

3.  **Доступ к API:**
    *   API: http://localhost:8000/api/
    *   Swagger-документация (если добавлена): http://localhost:8000/swagger/

## Структура проекта
```bash
order-service/
├── api/
│   ├── __init__.py
│   ├── apps.py        # Конфигурация приложения и регистрация сигналов
│   ├── migrations/    # Миграции базы данных
│   ├── models.py      # Модели (Supplier, Category, Product, Stock, Order, OrderItem, UserProfile)
│   ├── serializers.py # Сериализаторы для API
│   ├── signals.py     # Сигналы (например, создание UserProfile)
│   ├── tasks.py       # Фоновые задачи Celery (проверка email)
│   ├── tests.py       # Тесты (опционально)
│   ├── urls.py        # Маршруты API
│   ├── views.py       # Представления API
├── order_service/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py    # Настройки проекта
│   ├── urls.py        # Основные маршруты
│   ├── wsgi.py
├── .env               # Переменные окружения
├── Dockerfile         # Конфигурация Docker
├── docker-compose.yml # Конфигурация Docker Compose
├── manage.py          # Управление Django
├── requirements.txt   # Зависимости
```


## Использование API

### Основные эндпоинты

*   **Поставщики:** `/api/suppliers/`
    *   `GET`: Получение списка поставщиков
    *   `POST`: Создание нового поставщика
    *   `PUT/PATCH`: Обновление существующего поставщика
    *   `DELETE`: Удаление поставщика (с каскадным удалением товаров и остатков)

*   **Категории:** `/api/categories/`
    *   `GET`: Получение списка категорий
    *   `POST`: Создание категории (с поддержкой вложенных категорий)
    *   `PUT/PATCH`: Обновление категории
    *   `DELETE`: Удаление категории

*   **Товары:** `/api/products/`
    *   Полный набор CRUD-операций для товаров

*   **Остатки:** `/api/stocks/`
    *   `GET`: Получение списка остатков (с кэшированием в Redis)
    *   `POST`: Добавление остатков
    *   `PUT/PATCH`: Обновление остатков
    *   `DELETE`: Удаление остатков

*   **Заказы:** `/api/orders/`
    *   `GET`: Получение списка заказов (только для авторизованного пользователя)
    *   `POST`: Создание заказа (проверяет остатки, отправляет email)
    *   *Требуется аутентификация:* `Authorization: Token <token>`

*   **Регистрация:** `/api/register/`
    *   `POST`: Регистрация пользователя (создает User и UserProfile, отправляет письмо с токеном верификации)

*   **Подтверждение email:** `/api/verify-email/<token>/`
    *   `GET`: Подтверждение email по токену

### Пример запроса (регистрация)

```bash
curl -X POST http://localhost:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "securepassword123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "middle_name": "Иванович",
    "age": 30
}'
