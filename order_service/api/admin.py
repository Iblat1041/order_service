from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Supplier, Category, Product, Stock, Order, OrderItem, UserProfile)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профили'


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'is_staff',
        'is_active', 'is_superuser', 'date_joined',
        )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    list_editable = ('is_active', 'is_staff', 'is_superuser')
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'street', 'building')
    search_fields = ('name', 'city')
    list_filter = ('country', 'city')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'category', 'price')
    search_fields = ('name',)
    list_filter = ('supplier', 'category')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product__name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'order_date')
    search_fields = ('buyer__username',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'purchase_price')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'email_verified', 'age')
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = ('email_verified',)
    list_editable = ('email_verified',)
