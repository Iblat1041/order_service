from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.utils import timezone
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Supplier, Category, Product, Stock, Order, OrderItem, UserProfile
from .services import OrderService, UserProfileService


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
        )
    ]
)
class SupplierSerializer(serializers.Serializer):
    """Сериализатор для модели Supplier."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    street = serializers.CharField(max_length=100)
    building = serializers.CharField(max_length=50)

    def create(self, validated_data):
        """Создаёт новый объект Supplier.

        Args:
            validated_data (dict): Валидированные данные для создания поставщика.

        Returns:
            Supplier: Созданный объект поставщика.
        """
        return Supplier.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий объект Supplier.

        Args:
            instance (Supplier): Объект поставщика для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            Supplier: Обновлённый объект поставщика.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.country = validated_data.get('country', instance.country)
        instance.city = validated_data.get('city', instance.city)
        instance.street = validated_data.get('street', instance.street)
        instance.building = validated_data.get('building', instance.building)
        instance.save()
        return instance


class CategorySerializer(serializers.Serializer):
    """Сериализатор для модели Category."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False
    )

    def create(self, validated_data):
        """Создаёт новый объект Category.

        Args:
            validated_data (dict): Валидированные данные для создания категории.

        Returns:
            Category: Созданный объект категории.
        """
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий объект Category.

        Args:
            instance (Category): Объект категории для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            Category: Обновлённый объект категории.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.save()
        return instance


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
class ProductSerializer(serializers.Serializer):
    """Сериализатор для модели Product."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        """Создаёт новый объект Product.

        Args:
            validated_data (dict): Валидированные данные для создания продукта.

        Returns:
            Product: Созданный объект продукта.
        """
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий объект Product.

        Args:
            instance (Product): Объект продукта для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            Product: Обновлённый объект продукта.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.category = validated_data.get('category', instance.category)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance


class StockSerializer(serializers.Serializer):
    """Сериализатор для модели Stock."""
    id = serializers.IntegerField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=0)

    def create(self, validated_data):
        """Создаёт новый объект Stock.

        Args:
            validated_data (dict): Валидированные данные для создания остатка.

        Returns:
            Stock: Созданный объект остатка.
        """
        return Stock.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий объект Stock.

        Args:
            instance (Stock): Объект остатка для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            Stock: Обновлённый объект остатка.
        """
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance


class OrderItemSerializer(serializers.Serializer):
    """Сериализатор для модели OrderItem."""
    id = serializers.IntegerField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        """Создаёт новый объект OrderItem.

        Args:
            validated_data (dict): Валидированные данные для создания элемента заказа.

        Returns:
            OrderItem: Созданный объект элемента заказа.
        """
        return OrderItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий объект OrderItem.

        Args:
            instance (OrderItem): Объект элемента заказа для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            OrderItem: Обновлённый объект элемента заказа.
        """
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.purchase_price = validated_data.get('purchase_price', instance.purchase_price)
        instance.save()
        return instance


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
class OrderSerializer(serializers.Serializer):
    """Сериализатор для модели Order, включающий элементы заказа."""
    id = serializers.IntegerField(read_only=True)
    order_date = serializers.DateTimeField(default=timezone.now)
    buyer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    items = OrderItemSerializer(many=True)

    def create(self, validated_data):
        """Создаёт новый заказ, используя OrderService.

        Args:
            validated_data (dict): Валидированные данные для создания заказа.

        Returns:
            Order: Созданный объект заказа.
        """
        return OrderService.create_order(validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий заказ, используя OrderService.

        Args:
            instance (Order): Объект заказа для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            Order: Обновлённый объект заказа.
        """
        return OrderService.update_order(instance, validated_data)


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
class UserProfileSerializer(serializers.Serializer):
    """Сериализатор для модели UserProfile, включающий регистрацию пользователя."""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(max_length=100, allow_blank=True)
    age = serializers.IntegerField(min_value=0, allow_null=True, required=False)
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
        label="Пароль",
        required=True,
        min_length=8,
        help_text="Пароль должен содержать минимум 8 символов"        
    )

    def create(self, validated_data):
        """Создаёт новый профиль пользователя, используя UserProfileService.

        Args:
            validated_data (dict): Валидированные данные для создания профиля.

        Returns:
            UserProfile: Созданный объект профиля пользователя.
        """
        return UserProfileService.create_user_profile(validated_data)

    def update(self, instance, validated_data):
        """Обновляет существующий профиль пользователя, используя UserProfileService.

        Args:
            instance (UserProfile): Объект профиля пользователя для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            UserProfile: Обновлённый объект профиля пользователя.
        """
        return UserProfileService.update_user_profile(instance, validated_data)
