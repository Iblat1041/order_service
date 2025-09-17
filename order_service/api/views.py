from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db import models
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Supplier, Category, Product, Stock, Order, UserProfile
from .serializers import (
    SupplierSerializer, CategorySerializer, ProductSerializer,
    StockSerializer, OrderSerializer, UserProfileSerializer
)
from typing import Any

class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet для управления поставщиками."""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для управления категориями."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для управления товарами."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class StockViewSet(viewsets.ModelViewSet):
    """ViewSet для управления остатками на складе."""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    @method_decorator(cache_page(60 * 5))  # Кэш на 5 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заказами, доступными только авторизованным пользователям."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self) -> models.QuerySet:
        """
        Возвращает queryset заказов, доступных только текущему пользователю.

        Returns:
            QuerySet: Список заказов текущего пользователя.
        """
        if self.request.user.is_authenticated:
            return Order.objects.filter(buyer=self.request.user)
        return Order.objects.none()

    def perform_create(self, serializer: OrderSerializer) -> None:
        """
        Сохраняет заказ, устанавливая текущего пользователя как покупателя.

        Args:
            serializer: Сериализатор заказа.
        """
        serializer.save(buyer=self.request.user)

@api_view(['POST'])
def register_user(request: Request) -> Response:
    """
    Регистрирует нового пользователя и отправляет письмо для подтверждения почты.

    Args:
        request: HTTP-запрос с данными пользователя.

    Returns:
        Response: Ответ с сообщением об успешной регистрации или ошибками.
    """
    serializer: UserProfileSerializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пользователь зарегистрирован, подтвердите почту'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verify_email(request: Request, token: str) -> Response:
    """
    Подтверждает email пользователя по токену.

    Args:
        request: HTTP-запрос.
        token: Токен подтверждения email.

    Returns:
        Response: Ответ с сообщением об успехе или ошибке.
    """
    profile: UserProfile = get_object_or_404(UserProfile, verification_token=token)
    profile.email_verified = True
    profile.verification_token = None
    profile.verification_sent_at = None
    profile.save()
    return Response(
        {'message': 'Электронная почта успешно подтверждена'},
        status=status.HTTP_200_OK
    )
