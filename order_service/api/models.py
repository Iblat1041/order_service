from django.db.models import (
    BooleanField, CASCADE, CharField, DateTimeField, DecimalField,
    OneToOneField, PositiveIntegerField, ForeignKey, Model)
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Optional


class Supplier(Model):
    """Модель поставщика, содержащая информацию о поставщике товаров."""
    name: CharField = CharField(
        max_length=255,
        verbose_name="Наименование организации",
        )
    country: CharField = CharField(
        max_length=100,
        verbose_name="Страна",
        )
    city: CharField = CharField(
        max_length=100,
        verbose_name="Город",
        )
    street: CharField = CharField(
        max_length=100,
        verbose_name="Улица",
        )
    building: CharField = CharField(
        max_length=50,
        verbose_name="Здание",
        )

    def __str__(self) -> str:
        """Возвращает строковое представление поставщика."""
        return self.name

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"


class Category(Model):
    """Модель категории товаров, поддерживающая иерархическую структуру."""
    name: CharField = CharField(
        max_length=100,
        verbose_name="Название категории",
        )
    parent: Optional[ForeignKey] = ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name='subcategories',
        verbose_name="Родительская категория"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление категории."""
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(Model):
    """Модель товара, связанного с поставщиком и категорией."""
    name: CharField = CharField(
        max_length=255,
        verbose_name="Наименование"
        )
    supplier: ForeignKey = ForeignKey(
        Supplier,
        on_delete=CASCADE,
        related_name='products',
        verbose_name="Поставщик",
    )
    category: ForeignKey = ForeignKey(
        Category,
        on_delete=CASCADE,
        related_name='products',
        verbose_name="Категория",
    )
    price: DecimalField = DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за единицу",
        )

    def __str__(self) -> str:
        """Возвращает строковое представление товара."""
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Stock(Model):
    """Модель остатков товара на складе."""
    product: ForeignKey = ForeignKey(
        Product,
        on_delete=CASCADE,
        related_name='stock',
        verbose_name="Товар"
    )
    quantity: PositiveIntegerField = PositiveIntegerField(
        verbose_name="Количество",
        )

    def __str__(self) -> str:
        """Возвращает строковое представление остатка на складе."""
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        verbose_name = "Остаток на складе"
        verbose_name_plural = "Остатки на складе"


class Order(Model):
    """Модель заказа, связанного с покупателем."""
    buyer: ForeignKey = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='orders',
        verbose_name="Покупатель"
    )
    order_date: DateTimeField = DateTimeField(
        default=timezone.now,
        verbose_name="Дата заказа",
        )

    def __str__(self) -> str:
        """Возвращает строковое представление заказа."""
        return f"Заказ {self.id} от {self.buyer.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(Model):
    """Модель элемента заказа, связывающего заказ и товар."""
    order: ForeignKey = ForeignKey(
        Order,
        on_delete=CASCADE,
        related_name='items',
        verbose_name="Заказ"
    )
    product: ForeignKey = ForeignKey(
        Product,
        on_delete=CASCADE,
        verbose_name="Товар"
    )
    quantity: PositiveIntegerField = PositiveIntegerField(
        verbose_name="Количество",
        )
    purchase_price: DecimalField = DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Закупочная цена"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление элемента заказа."""
        return f"{self.product.name} в заказе {self.order.id}"

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"


class UserProfile(Model):
    """Модель профиля пользователя, расширяющая стандартную модель User."""
    user: OneToOneField = OneToOneField(
        User,
        on_delete=CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    first_name: CharField = CharField(
        max_length=100,
        verbose_name="Имя",
        )
    last_name: CharField = CharField(
        max_length=100,
        verbose_name="Фамилия",
        )
    middle_name: CharField = CharField(
        max_length=100,
        blank=True,
        verbose_name="Отчество",
        )
    age: PositiveIntegerField = PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Возраст",
        )
    email_verified: BooleanField = BooleanField(
        default=False,
        verbose_name="Почта подтверждена",
        )
    verification_token: CharField = CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Токен подтверждения",
    )
    verification_sent_at: Optional[DateTimeField] = DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата отправки токена"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление профиля пользователя."""
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
