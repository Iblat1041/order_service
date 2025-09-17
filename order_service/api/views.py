from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Supplier, Category, Product, Stock, Order, OrderItem, UserProfile
from .serializers import (
    SupplierSerializer, CategorySerializer, ProductSerializer,
    StockSerializer, OrderSerializer, UserProfileSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample,
    OpenApiResponse, OpenApiTypes
)

@extend_schema_view(
    list=extend_schema(
        summary="Список поставщиков",
        description="Получение списка всех поставщиков",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Поиск по названию поставщика'
            ),
        ]
    ),
    create=extend_schema(
        summary="Создать поставщика",
        description="Создание нового поставщика (требуются права администратора)"
    ),
    retrieve=extend_schema(
        summary="Детали поставщика",
        description="Получение детальной информации о поставщике"
    ),
    update=extend_schema(
        summary="Обновить поставщика",
        description="Полное обновление информации о поставщике"
    ),
    partial_update=extend_schema(
        summary="Частично обновить поставщика",
        description="Частичное обновление информации о поставщике"
    ),
    destroy=extend_schema(
        summary="Удалить поставщика",
        description="Удаление поставщика из системы"
    )
)
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

@extend_schema_view(
    list=extend_schema(
        summary="Список категорий",
        description="Получение иерархического списка категорий товаров"
    ),
    retrieve=extend_schema(
        summary="Детали категории",
        description="Получение информации о конкретной категории"
    )
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@extend_schema_view(
    list=extend_schema(
        summary="Список товаров",
        description="Получение списка товаров с возможностью фильтрации",
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Фильтр по категории'
            ),
            OpenApiParameter(
                name='supplier',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Фильтр по поставщику'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Минимальная цена'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Максимальная цена'
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Детали товара",
        description="Получение детальной информации о товаре"
    )
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().select_related('supplier', 'category')
    serializer_class = ProductSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Список остатков",
        description="Получение информации об остатках товаров на складе",
        parameters=[
            OpenApiParameter(
                name='product',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Фильтр по товару'
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Детали остатка",
        description="Получение информации об остатке конкретного товара"
    )
)
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all().select_related('product')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

@extend_schema_view(
    create=extend_schema(
        summary="Создать заказ",
        description="Создание нового заказа. Автоматически уменьшает остатки на складе.",
        responses={
            201: OpenApiResponse(response=OrderSerializer, description='Заказ создан'),
            400: OpenApiResponse(description='Недостаточно товара на складе')
        }
    ),
    list=extend_schema(
        summary="Мои заказы",
        description="Получение списка заказов текущего пользователя",
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Сортировка (-order_date для новых первыми)'
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Детали заказа",
        description="Получение детальной информации о заказе"
    ),
    destroy=extend_schema(
        summary="Удалить заказ",
        description="Удаление заказа (только для своих заказов)"
    )
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).prefetch_related('items__product')

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @extend_schema(
        summary="Повторить заказ",
        description="Создание нового заказа на основе существующего",
        responses={
            201: OpenApiResponse(response=OrderSerializer, description='Заказ создан'),
            400: OpenApiResponse(description='Ошибка при создании заказа')
        }
    )
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        original_order = self.get_object()
        
        # Создаем новый заказ с теми же товарами
        order_data = {
            'buyer': request.user.id,
            'items': []
        }
        
        for item in original_order.items.all():
            order_data['items'].append({
                'product': item.product.id,
                'quantity': item.quantity,
                'purchase_price': str(item.purchase_price)
            })
        
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        new_order = serializer.save()
        
        return Response(OrderSerializer(new_order).data, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="Регистрация пользователя",
    description="Создание нового пользователя и отправка письма для подтверждения email",
    request=UserProfileSerializer,
    responses={
        201: OpenApiResponse(
            description='Пользователь создан, отправлено письмо для подтверждения',
            examples=[
                OpenApiExample(
                    'Успешная регистрация',
                    value={
                        'message': 'Пользователь создан. Проверьте email для подтверждения.',
                        'user_id': 1
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Неверные данные',
            examples=[
                OpenApiExample(
                    'Ошибка валидации',
                    value={
                        'email': ['Это поле обязательно.'],
                        'username': ['Это имя пользователя уже занято.']
                    }
                )
            ]
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        user_profile = serializer.save()
        return Response(
            {
                'message': 'Пользователь создан. Проверьте email для подтверждения.',
                'user_id': user_profile.user.id
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Подтверждение email",
    description="Подтверждение электронной почты по токену",
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Токен подтверждения из письма'
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Email успешно подтвержден',
            examples=[
                OpenApiExample(
                    'Успешное подтверждение',
                    value={
                        'message': 'Email успешно подтвержден',
                        'token': 'abc123def456...'
                    }
                )
            ]
        ),
        404: OpenApiResponse(
            description='Неверный токен подтверждения',
            examples=[
                OpenApiExample(
                    'Ошибка подтверждения',
                    value={
                        'error': 'Неверный токен подтверждения'
                    }
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        user_profile = UserProfile.objects.get(verification_token=token, email_verified=False)
        user_profile.email_verified = True
        user_profile.verification_token = None
        user_profile.save()
        
        # Создаем токен аутентификации
        token, created = Token.objects.get_or_create(user=user_profile.user)
        
        return Response(
            {
                'message': 'Email успешно подтвержден',
                'token': token.key
            },
            status=status.HTTP_200_OK
        )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Неверный токен подтверждения'},
            status=status.HTTP_404_NOT_FOUND
        )

@extend_schema(
    summary="Информация о текущем пользователе",
    description="Получение информации о текущем аутентифицированном пользователе",
    responses={
        200: OpenApiResponse(
            description='Информация о пользователе',
            examples=[
                OpenApiExample(
                    'Данные пользователя',
                    value={
                        'username': 'ivanov',
                        'email': 'ivan@example.com',
                        'first_name': 'Иван',
                        'last_name': 'Иванов',
                        'email_verified': True
                    }
                )
            ]
        ),
        401: OpenApiResponse(description='Не авторизован')
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_info(request):
    user = request.user
    profile = user.profile
    
    return Response({
        'username': user.username,
        'email': user.email,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'middle_name': profile.middle_name,
        'age': profile.age,
        'email_verified': profile.email_verified
    })
