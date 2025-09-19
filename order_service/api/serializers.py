from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import uuid
from typing import Dict, Any

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from .models import (
    Supplier,
    Category,
    Product,
    Stock,
    Order,
    OrderItem,
    UserProfile,
)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример поставщика',
            value={
                'name': 'ООО "Поставщик"',
                'country': 'Россия',
                'city': 'Москва',
                'street': 'Ленина',
                'building': '10'
            },
            request_only=True,
            response_only=False,
        )
    ]
)
class SupplierSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Supplier."""
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'country', 'city', 'street', 'building']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример товара',
            value={
                'name': 'Ноутбук',
                'supplier': 1,
                'category': 1,
                'price': '50000.00'
            },
            request_only=True,
        )
    ]
)
class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product."""
    class Meta:
        model = Product
        fields = ['id', 'name', 'supplier', 'category', 'price']


class StockSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Stock."""
    class Meta:
        model = Stock
        fields = ['id', 'product', 'quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem."""
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'purchase_price']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример заказа',
            value={
                'buyer': 1,
                'items': [
                    {
                        'product': 1,
                        'quantity': 2,
                        'purchase_price': '45000.00'
                    }
                ]
            },
            request_only=True,
        )
    ]
)
class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order, включающий элементы заказа."""
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_date', 'buyer', 'items']

    def create(self, validated_data: Dict[str, Any]) -> Order:
        """
        Создает заказ, обновляет остатки на складе и отправляет письмо покупателю.
        """
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            stock = Stock.objects.get(product=item_data['product'])
            if stock.quantity < item_data['quantity']:
                raise serializers.ValidationError(
                    f"Недостаточно товара {item_data['product'].name} "
                    f"на складе"
                )
            OrderItem.objects.create(order=order, **item_data)
            stock.quantity -= item_data['quantity']
            stock.save()

        # Отправка email только если настроен email бэкенд
        if not settings.DEBUG or hasattr(settings, 'EMAIL_BACKEND'):
            try:
                send_mail(
                    subject='Подтверждение заказа',
                    message=f'Ваш заказ {order.id} успешно создан.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.buyer.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка отправки email: {e}")

        return order


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример регистрации',
            value={
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'middle_name': 'Иванович',
                'age': 30,
                'email': 'ivan@example.com',
                'username': 'ivanov',
                'password': 'securepassword123'
            },
            request_only=True,
        )
    ]
)
class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserProfile, включающий регистрацию пользователя."""
    email = serializers.EmailField(
        write_only=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        label="Электронная почта"
    )
    username = serializers.CharField(
        write_only=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        label="Имя пользователя"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label="Пароль"
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'age',
            'email',
            'username',
            'password'
        ]

    def create(self, validated_data: Dict[str, Any]) -> UserProfile:
        """
        Создает профиль пользователя и отправляет письмо для подтверждения почты.

        Args:
            validated_data: Валидированные данные для создания пользователя.

        Returns:
            UserProfile: Созданный профиль пользователя.
        """
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password')
        }
        user = User.objects.create_user(**user_data)

        user_profile = UserProfile.objects.create(
            user=user,
            **validated_data,
            verification_token=str(uuid.uuid4()),
            verification_sent_at=timezone.now()
        )

        # Отправка email только если настроен email бэкенд
        if not settings.DEBUG or hasattr(settings, 'EMAIL_BACKEND'):
            try:
                send_mail(
                    subject='Подтверждение электронной почты',
                    message=(
                        f'Перейдите по ссылке для подтверждения: '
                        f'{settings.SITE_URL}/api/verify-email/'
                        f'{user_profile.verification_token}/'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка отправки email: {e}")

        return user_profile
