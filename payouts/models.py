from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class PayoutRequest(models.Model):
    """Модель заявки на выплату средств."""

    # Кастомные условия для выбора
    class PayoutRequestStatus(models.TextChoices):
        OPEN = 'open', 'Открыта'
        IN_PROGRESS = 'in_progress', 'В работе'
        RESOLVED = 'resolved', 'Решена'
        CLOSED = 'closed', 'Закрыта'
        CANSELLED = 'canselled', 'Отклонена'

    payment_sum = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        # Стандартный django валидатор
        validators=[
            MinValueValidator(Decimal('0.01'))
        ],
        verbose_name='Сумма выплаты',
        help_text='Сумма выплаты (должна быть положительной)'
    )
    currency = models.CharField(
        max_length=3,
        verbose_name='Валюта',
        help_text='Код валюты в формате ISO 4217 (например: USD, EUR, RUB)'
    )
    # Здесь желательно знать точные значения, иначе API
    # не является удобным в использовании
    recipients_details = models.TextField(
        verbose_name='Реквизиты получателя',
        help_text='Банковские реквизиты или платежная информация получателя'
    )
    status = models.CharField(
        max_length=20,
        choices=PayoutRequestStatus.choices,
        default=PayoutRequestStatus.OPEN,
        db_index=True,
        verbose_name='Статус'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий',
        help_text='Опциональное описание или комментарий к заявке'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Время обновления'
    )

    class Meta:
        verbose_name = 'Заявка на выплату'
        verbose_name_plural = 'Заявки на выплату'
        # Сортируем по дате и добавляем индексы для оптимизации
        # Много индексов не значит хорошо, кидаем только на частые поля
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['currency']),
            models.Index(fields=['created_at']),
        ]

    # Краткое отображение для админки
    def __str__(self):
        return (
            f'Заявка на выплату: №{self.id}'
            f' | Время создания: {self.created_at}'
            f' | Статус: {self.status}'
        )
