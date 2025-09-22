from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Stock, Order, OrderItem, UserProfile, User


class ProductRepository:
    """Репозиторий для работы с моделями Product и Stock в базе данных."""

    @staticmethod
    def get_product_by_id(product_id):
        """Получает продукт по его идентификатору.

        Args:
            product_id (int): Идентификатор продукта.

        Returns:
            Product: Объект модели Product.

        Raises:
            ObjectDoesNotExist: Если продукт с указанным ID не найден.
        """
        return Product.objects.get(id=product_id)

    @staticmethod
    def get_stock_by_product(product):
        """Получает складской остаток для указанного продукта.

        Args:
            product (Product): Объект модели Product.

        Returns:
            Stock: Объект модели Stock, связанный с продуктом.

        Raises:
            ObjectDoesNotExist: Если запись о складе для продукта не найдена.
        """
        return Stock.objects.get(product=product)

    @staticmethod
    def update_stock(stock, quantity):
        """Обновляет количество товара на складе, уменьшая его на указанное значение.

        Args:
            stock (Stock): Объект модели Stock.
            quantity (int): Количество, на которое нужно уменьшить остаток.

        Returns:
            Stock: Обновлённый объект модели Stock.
        """
        stock.quantity -= quantity
        stock.save()
        return stock


class OrderRepository:
    """Репозиторий для работы с моделями Order и OrderItem в базе данных."""

    @staticmethod
    def create_order(validated_data):
        """Создаёт новый заказ в базе данных.

        Args:
            validated_data (dict): Валидированные данные для создания заказа.

        Returns:
            Order: Созданный объект модели Order.
        """
        return Order.objects.create(**validated_data)

    @staticmethod
    def create_order_items(order, items_data):
        """Создаёт элементы заказа в базе данных одним запросом.

        Args:
            order (Order): Объект модели Order, к которому привязаны элементы.
            items_data (list): Список словарей с данными для создания OrderItem.

        Returns:
            list: Список созданных объектов модели OrderItem.
        """
        return OrderItem.objects.bulk_create([
            OrderItem(order=order, **item_data) for item_data in items_data
        ])


class UserProfileRepository:
    """Репозиторий для работы с моделями User и UserProfile в базе данных."""

    @staticmethod
    def create_user(user_data):
        """Создаёт нового пользователя в базе данных.

        Args:
            user_data (dict): Данные для создания пользователя (username, email, password).

        Returns:
            User: Созданный объект модели User.
        """
        return User.objects.create_user(**user_data)

    @staticmethod
    def create_user_profile(user, validated_data, verification_token, verification_sent_at):
        """Создаёт профиль пользователя в базе данных.

        Args:
            user (User): Объект модели User, к которому привязан профиль.
            validated_data (dict): Валидированные данные для создания профиля.
            verification_token (str): Токен для верификации email.
            verification_sent_at (datetime): Время отправки письма для верификации.

        Returns:
            UserProfile: Созданный объект модели UserProfile.
        """
        return UserProfile.objects.create(
            user=user,
            **validated_data,
            verification_token=verification_token,
            verification_sent_at=verification_sent_at
        )
