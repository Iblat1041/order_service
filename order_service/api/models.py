from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Optional

class Supplier(models.Model):
    """Модель поставщика, содержащая информацию о поставщике товаров."""
    name: models.CharField = models.CharField(max_length=255, verbose_name="Наименование организации")
    country: models.CharField = models.CharField(max_length=100, verbose_name="Страна")
    city: models.CharField = models.CharField(max_length=100, verbose_name="Город")
    street: models.CharField = models.CharField(max_length=100, verbose_name="Улица")
    building: models.CharField = models.CharField(max_length=50, verbose_name="Здание")

    def __str__(self) -> str:
        """Возвращает строковое представление поставщика."""
        return self.name

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

class Category(models.Model):
    """Модель категории товаров, поддерживающая иерархическую структуру."""
    name: models.CharField = models.CharField(max_length=100, verbose_name="Название категории")
    parent: Optional[models.ForeignKey] = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="Родительская категория"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление категории."""
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    """Модель товара, связанного с поставщиком и категорией."""
    name: models.CharField = models.CharField(max_length=255, verbose_name="Наименование")
    supplier: models.ForeignKey = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Поставщик"
    )
    category: models.ForeignKey = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    def __str__(self) -> str:
        """Возвращает строковое представление товара."""
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Stock(models.Model):
    """Модель остатков товара на складе."""
    product: models.ForeignKey = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name="Товар"
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name="Количество")

    def __str__(self) -> str:
        """Возвращает строковое представление остатка на складе."""
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        verbose_name = "Остаток на складе"
        verbose_name_plural = "Остатки на складе"

class Order(models.Model):
    """Модель заказа, связанного с покупателем."""
    buyer: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Покупатель"
    )
    order_date: models.DateTimeField = models.DateTimeField(default=timezone.now, verbose_name="Дата заказа")

    def __str__(self) -> str:
        """Возвращает строковое представление заказа."""
        return f"Заказ {self.id} от {self.buyer.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    """Модель элемента заказа, связывающего заказ и товар."""
    order: models.ForeignKey = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Заказ"
    )
    product: models.ForeignKey = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name="Количество")
    purchase_price: models.DecimalField = models.DecimalField(
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

class UserProfile(models.Model):
    """Модель профиля пользователя, расширяющая стандартную модель User."""
    user: models.OneToOneField = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    first_name: models.CharField = models.CharField(max_length=100, verbose_name="Имя")
    last_name: models.CharField = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name: models.CharField = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    age: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name="Возраст")
    email_verified: models.BooleanField = models.BooleanField(default=False, verbose_name="Почта подтверждена")
    verification_token: models.CharField = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Токен подтверждения"
    )
    verification_sent_at: Optional[models.DateTimeField] = models.DateTimeField(
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
