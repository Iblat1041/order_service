from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
from django.contrib.auth.models import User
from typing import QuerySet

@shared_task
def check_email_verification() -> None:
    """
    Проверяет неподтвержденные email и отправляет напоминания или деактивирует аккаунты.

    Проверяет профили пользователей, у которых email не подтвержден:
    - Если прошло более 1 дня, отправляет напоминание.
    - Если прошло более 2 дней, деактивирует аккаунт.

    Задача выполняется периодически через Celery Beat (каждый час, согласно
    настройке CELERY_BEAT_SCHEDULE в settings.py).
    """
    one_day_ago = timezone.now() - timedelta(days=1)
    two_days_ago = timezone.now() - timedelta(days=2)

    one_day_unverified: QuerySet[UserProfile] = UserProfile.objects.filter(
        email_verified=False,
        verification_sent_at__lte=one_day_ago,
        verification_sent_at__gt=two_days_ago
    )
    for profile in one_day_unverified:
        send_mail(
            subject='Напоминание о подтверждении почты',
            message=(
                f'Пожалуйста, подтвердите вашу почту, перейдя по ссылке: '
                f'{settings.SITE_URL}/api/verify-email/{profile.verification_token}/'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[profile.user.email],
            fail_silently=True,
        )

    two_days_unverified: QuerySet[UserProfile] = UserProfile.objects.filter(
        email_verified=False,
        verification_sent_at__lte=two_days_ago
    )
    for profile in two_days_unverified:
        profile.user.is_active = False
        profile.user.save()
