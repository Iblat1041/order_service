from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, CategoryViewSet, ProductViewSet,
    StockViewSet, OrderViewSet, register_user, verify_email
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_user, name='register_user'),
    path('verify-email/<str:token>/', verify_email, name='verify_email'),
]
"""Маршруты API для управления поставщиками, категориями, товарами, остатками и заказами."""