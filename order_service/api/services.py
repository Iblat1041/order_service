from celery.exceptions import CeleryError
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, transaction
from django.core.mail import send_mail
from django.conf import settings
from .repositories import ProductRepository, OrderRepository, UserProfileRepository
from .tasks import send_email_task
import uuid
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(validated_data, user):
        """Создаёт новый заказ с элементами и обновляет остатки на складе.

        Args:
            validated_data (dict): Валидированные данные для создания заказа.
            user (User): Пользователь, создающий заказ.

        Returns:
            Order: Созданный объект заказа.

        Raises:
            ValueError: Если недостаточно товара на складе или товар отсутствует.
            DatabaseError: Если произошла ошибка базы данных.
        """
        items_data = validated_data.pop('items', [])
        validated_data['buyer'] = user.id
        order = OrderRepository.create_order(validated_data)

        for item_data in items_data:
            try:
                stock = ProductRepository.get_stock_by_product(item_data['product'])
                if stock.quantity < item_data['quantity']:
                    logger.error(
                        f"Недостаточно товара {item_data['product'].name} на складе. "
                        f"Доступно: {stock.quantity}, запрошено: {item_data['quantity']}"
                    )
                    raise ValueError(
                        f"Недостаточно товара {item_data['product'].name} на складе"
                    )
                ProductRepository.update_stock(stock, item_data['quantity'])
            except ObjectDoesNotExist:
                logger.error(f"Товар {item_data['product'].name} отсутствует на складе")
                raise ValueError(f"Товар {item_data['product'].name} отсутствует на складе")
            except DatabaseError as db_err:
                logger.error(f"Ошибка базы данных при обновлении стока: {db_err}")
                raise DatabaseError(f"Ошибка при обработке заказа: {db_err}")

        OrderRepository.create_order_items(order, items_data)

        try:
            send_email_task.delay(
                subject='Подтверждение заказа',
                message=f'Ваш заказ {order.id} успешно создан.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[order.buyer.email]
            )
            order.email_sent = True
            order.save()
            logger.info(f"Заказ {order.id} успешно создан, email отправлен асинхронно")
        except Exception as e:
            logger.warning(f"Не удалось отправить email для заказа {order.id}: {e}")
            # Транзакция уже завершена, продолжаем без уведомления

        return order


    @staticmethod
    @transaction.atomic
    def update_order(instance, validated_data):
        """Обновляет существующий заказ, включая элементы заказа и остатки на складе.
    
        Args:
            instance (Order): Объект заказа для обновления.
            validated_data (dict): Валидированные данные для обновления.
    
        Returns:
            Order: Обновлённый объект заказа.
    
        Raises:
            ValueError: Если недостаточно товара на складе.
            ObjectDoesNotExist: Если товар отсутствует на складе.
        """
        # Извлекаем данные по элементам заказа
        items_data = validated_data.pop('items', None)
    
        # Обновляем базовые поля заказа
        instance.buyer = validated_data.get('buyer', instance.buyer)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.save()
    
        if items_data:
            # Сохраняем старые элементы для восстановления остатков
            old_items = list(instance.items.all())  # Конвертируем в список до удаления
            instance.items.all().delete()
    
            # Восстанавливаем остатки для старых элементов
            for old_item in old_items:
                try:
                    stock = ProductRepository.get_stock_by_product(old_item.product)
                    stock.quantity += old_item.quantity
                    stock.save()
                except ObjectDoesNotExist:
                    logger.warning(
                        f"Сток для товара {old_item.product.name} не найден при восстановлении"
                    )
                    continue  # Пропускаем, если сток удалён
                
            # Обновляем остатки и создаём новые элементы
            for item_data in items_data:
                try:
                    stock = ProductRepository.get_stock_by_product(item_data['product'])
                    # Вычисляем разницу с учётом старого количества (если было)
                    old_quantity = next(
                        (i.quantity for i in old_items if i.product.id == item_data['product'].id),
                        0
                    )
                    delta = item_data['quantity'] - old_quantity
                    if delta > 0 and stock.quantity < delta:
                        logger.error(
                            f"Недостаточно товара {item_data['product'].name} на складе"
                        )
                        raise ValueError(
                            f"Недостаточно товара {item_data['product'].name} на складе"
                        )
                    ProductRepository.update_stock(stock, delta)
                except ObjectDoesNotExist:
                    logger.error(
                        f"Товар {item_data['product'].name} отсутствует на складе"
                    )
                    raise ValueError(
                        f"Товар {item_data['product'].name} отсутствует на складе"
                    )
    
            # Создаём новые элементы заказа
            OrderRepository.create_order_items(instance, items_data)
    
        # Отправка уведомления (с обработкой возможного сбоя Celery)
        try:
            send_email_task.delay(
                subject='Обновление заказа',
                message=f'Ваш заказ {instance.id} был обновлён.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.buyer.email]
            )
            logger.info(f"Заказ {instance.id} успешно обновлён, email отправлен асинхронно")
        except CeleryError as e:
            logger.error(f"Не удалось отправить email для заказа {instance.id}: {e}")
            # Транзакция уже завершена, логируем и продолжаем
    
        return instance

    @staticmethod
    @transaction.atomic
    def reorder_order(original_order, request_user):
        """Создаёт новый заказ на основе существующего с проверкой остатков.

        Args:
            original_order (Order): Исходный заказ для копирования.
            request_user (User): Пользователь, создающий новый заказ.

        Returns:
            Order: Новый созданный заказ.

        Raises:
            ValueError: Если недостаточно товара на складе или товар отсутствует.
        """
        # Подготавливаем данные для нового заказа
        order_data = {
            'buyer': request_user.id,
            'items': []
        }

        # Проходим по элементам старого заказа
        for item in original_order.items.all():
            try:
                # Проверяем наличие остатка для товара
                stock = ProductRepository.get_stock_by_product(item.product)
                if stock.quantity < item.quantity:
                    logger.error(
                        f"Недостаточно товара {item.product.name} на складе"
                        )
                    raise ValueError(
                        f"Недостаточно товара {item.product.name} на складе"
                        )
                # Добавляем данные в новый заказ
                order_data['items'].append({
                    'product': item.product.id,
                    'quantity': item.quantity,
                    'purchase_price': str(item.purchase_price)
                })
            except ObjectDoesNotExist:
                logger.error(
                    f"Товар {item.product.name} отсутствует на складе"
                    )
                raise ValueError(
                    f"Товар {item.product.name} отсутствует на складе"
                    )

        # Создаём новый заказ
        from .serializers import OrderSerializer  # Импорт внутри функции для избежания циклических зависимостей
        serializer = OrderSerializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        new_order = serializer.save()

        logger.info(
            f"Создан новый заказ {new_order.id} на основе {original_order.id}"
            )
        return new_order


class UserProfileService:
    @staticmethod
    @transaction.atomic
    def create_user_profile(validated_data):
        """Создаёт новый профиль пользователя и отправляет письмо для верификации.

        Args:
            validated_data (dict): Валидированные данные для создания профиля.

        Returns:
            UserProfile: Созданный объект профиля пользователя.
        """
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password')
        }
        user = UserProfileRepository.create_user(user_data)
        verification_token = str(uuid.uuid4())
        user_profile = UserProfileRepository.create_user_profile(
            user=user,
            validated_data=validated_data,
            verification_token=verification_token,
            verification_sent_at=timezone.now()
        )

        send_email_task.delay(
            subject='Подтверждение электронной почты',
            message=(
                f'Перейдите по ссылке для подтверждения: '
                f'{settings.SITE_URL}/api/verify-email/{user_profile.verification_token}/'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        logger.info(f"Профиль пользователя {user.username} создан, email отправлен асинхронно")
        return user_profile

    @staticmethod
    @transaction.atomic
    def update_user_profile(instance, validated_data):
        """Обновляет профиль пользователя и отправляет письмо для верификации при смене email.

        Args:
            instance (UserProfile): Объект профиля пользователя для обновления.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            UserProfile: Обновлённый объект профиля пользователя.
        """
        user = instance.user
        username = validated_data.get('username', user.username)
        email = validated_data.get('email', user.email)

        # Обновляем поля User, если они изменились
        if username != user.username or email != user.email:
            user.username = username
            user.email = email
            user.save()

            # Если email изменился, сбрасываем верификацию и отправляем новое письмо
            if email != instance.user.email:
                instance.email_verified = False
                instance.verification_token = str(uuid.uuid4())
                instance.verification_sent_at = timezone.now()
                send_email_task.delay(
                    subject='Подтверждение новой электронной почты',
                    message=(
                        f'Перейдите по ссылке для подтверждения нового email: '
                        f'{settings.SITE_URL}/api/verify-email/{instance.verification_token}/'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email]
                )
                logger.info(f"Email пользователя {user.username} изменён, отправлено письмо для верификации")

        # Обновляем поля UserProfile
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.age = validated_data.get('age', instance.age)
        instance.save()

        logger.info(f"Профиль пользователя {user.username} успешно обновлён")
        return instance
