Cервис заказов со склада

Документация API
API предоставляет следующие эндпоинты:

Поставщики:

GET /api/suppliers/ — получить список поставщиков
POST /api/suppliers/ — создать поставщика
PUT /api/suppliers/{id}/ — обновить поставщика
DELETE /api/suppliers/{id}/ — удалить поставщика (удаляет связанные товары и остатки)


Категории:

GET /api/categories/ — получить список категорий
POST /api/categories/ — создать категорию
PUT /api/categories/{id}/ — обновить категорию
DELETE /api/categories/{id}/ — удалить категорию


Товары:

GET /api/products/ — получить список товаров
POST /api/products/ — создать товар
PUT /api/products/{id}/ — обновить товар
DELETE /api/products/{id}/ — удалить товар


Остатки на складе:

GET /api/stocks/ — получить список остатков
POST /api/stocks/ — добавить остаток
PUT /api/stocks/{id}/ — обновить остаток
DELETE /api/stocks/{id}/ — удалить остаток


Заказы:

GET /api/orders/ — получить список заказов текущего пользователя
POST /api/orders/ — создать заказ (уменьшает остатки на складе, отправляет письмо)


Пользователи:

POST /api/register/ — регистрация пользователя (отправляет письмо для подтверждения)
GET /api/verify-email/{token}/ — подтверждение почты