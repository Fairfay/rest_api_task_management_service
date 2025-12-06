from decimal import Decimal
from rest_framework import serializers
from typing import Dict, Any

from payouts.models import PayoutRequest


class PayoutRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели PayoutRequest с валидацией.
    Валидация в сериализаторе используется для:
    - Нормализации данных (например, приведение валюты к верхнему регистру)
    - Дополнительных бизнес-правил, которых нет в модели
    - Кросс-полевой валидации (проверка комбинаций полей)
    Базовые проверки уже есть в модели.
    """

    class Meta:
        model = PayoutRequest
        fields = '__all__'
        read_only_fields = (
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'payment_sum': {
                'required': True,
                'help_text': 'Сумма выплаты должна быть положительной.'
            },
            'currency': {
                'required': True,
                'help_text': 'Код валюты в формате ISO 4217.'
            },
            'recipients_details': {
                'required': True,
                'help_text': 'Банковские реквизиты.'
            },
            'comment': {
                'required': False,
                'allow_blank': True,
                'allow_null': True,
                'help_text': 'Опциональное описание или комментарий к заявке.'
            },
        }

    def validate_currency(self, value: str) -> str:
        """
        Нормализация и дополнительная валидация валюты.
        - Нормализуем данные (upper, strip) - это удобно для API
        - Проверяем формат (только буквы)
        """
        if not value:
            return value
        value = value.upper().strip()
        if not value.isalpha():
            raise serializers.ValidationError(
                'Код валюты должен содержать только буквы латинского алфавита.'
            )
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация на уровне объекта (кросс-полевая валидация).
        """
        payment_sum = attrs.get('payment_sum')
        currency = attrs.get('currency', '').upper() if attrs.get('currency') else ''
        comment = attrs.get('comment')
        if payment_sum and payment_sum > Decimal('100000.00'):
            if not comment or (isinstance(comment, str) and not comment.strip()):
                raise serializers.ValidationError(
                    {
                        'comment': 'Для выплат свыше 100000 рекомендуется указать комментарий.'
                    }
                )
        if currency == 'RUB' and payment_sum:
            max_rub_amount = Decimal('10000000.00')
            if payment_sum > max_rub_amount:
                raise serializers.ValidationError(
                    {
                        'payment_sum': f'Максимальная сумма для рублевых выплат: {max_rub_amount} RUB.'
                    }
                )
        return attrs
