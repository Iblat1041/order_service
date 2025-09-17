from datetime import timezone
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Supplier, Category, Product, Stock, Order, OrderItem, UserProfile
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail
from django.conf import settings
import uuid
from typing import Dict, Any

class SupplierSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Supplier."""
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'country', 'city', 'street', 'building']
        extra_kwargs = {
            'name': {'verbose_name': 'Наименование организации'},
            'country': {'verbose_name': 'Страна'},
            'city': {'verbose_name': 'Город'},
            'street': {'verbose_name': 'Улица'},
            'building': {'verbose_name': 'Здание'},
        }

class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']
        extra_kwargs = {
            'name': {'verbose_name': 'Название категории'},
            'parent': {'verbose_name': 'Родительская категория'},
        }

class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product."""
    class Meta:
        model = Product
        fields = ['id', 'name', 'supplier', 'category', 'price']
        extra_kwargs = {
            'name': {'verbose_name': 'Наименование'},
            'supplier': {'verbose_name': 'Поставщик'},
            'category': {'verbose_name': 'Категория'},
            'price': {'verbose_name': 'Цена за единицу'},
        }

class StockSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Stock."""
    class Meta:
        model = Stock
        fields = ['id', 'product', 'quantity']
        extra_kwargs = {
            'product': {'verbose_name': 'Товар'},
            'quantity': {'verbose_name': 'Количество'},
        }

class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem."""
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'purchase_price']
        extra_kwargs = {
            'product': {'verbose_name': 'Товар'},
            'quantity': {'verbose_name': 'Количество'},
            'purchase_price': {'verbose_name': 'Закупочная цена'},
        }

class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order, включающий элементы заказа."""
    items: OrderItemSerializer = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_date', 'buyer', 'items']
        extra_kwargs = {
            'order_date': {'verbose_name': 'Дата заказа'},
            'buyer': {'verbose_name': 'Покупатель'},
            'items': {'verbose_name': 'Товары в заказе'},
        }

    def create(self, validated_data: Dict[str, Any]) -> Order:
        """
        Создает заказ, обновляет остатки на складе и отправляет письмо покупателю.

        Args:
            validated_data: Валидированные данные для создания заказа.

        Raises:
            serializers.ValidationError: Если на складе недостаточно товара.

        Returns:
            Order: Созданный объект заказа.
        """
        items_data: list = validated_data.pop('items')
        order: Order = Order.objects.create(**validated_data)
        for item_data in items_data:
            stock: Stock = Stock.objects.get(product=item_data['product'])
            if stock.quantity < item_data['quantity']:
                raise serializers.ValidationError(
                    f"Недостаточно товара {item_data['product'].name} на складе"
                )
            OrderItem.objects.create(order=order, **item_data)
            stock.quantity -= item_data['quantity']
            stock.save()
        send_mail(
            subject='Подтверждение заказа',
            message=f'Ваш заказ {order.id} успешно создан.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.buyer.email],
            fail_silently=False,
        )
        return order

class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserProfile, включающий регистрацию пользователя."""
    email: serializers.EmailField = serializers.EmailField(
        write_only=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        label="Электронная почта"
    )
    username: serializers.CharField = serializers.CharField(
        write_only=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        label="Имя пользователя"
    )
    password: serializers.CharField = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label="Пароль"
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'middle_name', 'age', 'email', 'username', 'password']
        extra_kwargs = {
            'first_name': {'verbose_name': 'Имя'},
            'last_name': {'verbose_name': 'Фамилия'},
            'middle_name': {'verbose_name': 'Отчество'},
            'age': {'verbose_name': 'Возраст'},
        }

    def create(self, validated_data: Dict[str, Any]) -> UserProfile:
        """
        Создает профиль пользователя и отправляет письмо для подтверждения почты.

        Args:
            validated_data: Валидированные данные для создания пользователя.

        Returns:
            UserProfile: Созданный профиль пользователя.
        """
        user_data: Dict[str, str] = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password')
        }
        user: User = User.objects.create_user(**user_data)
        user_profile: UserProfile = UserProfile.objects.create(
            user=user,
            **validated_data,
            verification_token=str(uuid.uuid4()),
            verification_sent_at=timezone.now()
        )
        send_mail(
            subject='Подтверждение электронной почты',
            message=(
                f'Перейдите по ссылке для подтверждения: '
                f'{settings.SITE_URL}/api/verify-email/{user_profile.verification_token}/'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user_profile
