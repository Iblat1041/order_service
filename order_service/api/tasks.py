from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    """
    Асинхронная отправка email через Celery.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
        )
        logger.info(f"Email успешно отправлен: {subject} для {recipient_list}")
    except Exception as e:
        logger.error(f"Ошибка отправки email: {e}")


@shared_task
def check_email_verification():
    """
    Проверяет неподтвержденные email и отправляет напоминания или деактивирует аккаунты.
    """
    try:
        one_day_ago = timezone.now() - timedelta(days=1)
        two_days_ago = timezone.now() - timedelta(days=2)

        one_day_unverified = UserProfile.objects.filter(
            email_verified=False,
            verification_sent_at__lte=one_day_ago,
            verification_sent_at__gt=two_days_ago
        )
        logger.info(f"Проверено {one_day_unverified.count()} профилей на 1 день")
        for profile in one_day_unverified:
            send_email_task.delay(
                subject='Напоминание о подтверждении почты',
                message=(
                    f'Пожалуйста, подтвердите вашу почту, перейдя по '
                    f'ссылке: {settings.SITE_URL}/api/verify-email/{profile.verification_token}/'
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[profile.user.email]
            )

        two_days_unverified = UserProfile.objects.filter(
            email_verified=False,
            verification_sent_at__lte=two_days_ago
        )
        logger.info(f"Проверено {two_days_unverified.count()} профилей на 2 дня")
        for profile in two_days_unverified:
            profile.user.is_active = False
            profile.user.save()
            logger.info(f"Деактивирован аккаунт {profile.user.username}")
    except Exception as e:
        logger.error(f"Ошибка в check_email_verification: {e}")
