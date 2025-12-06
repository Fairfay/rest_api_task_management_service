import logging
import pytest

from decimal import Decimal
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status

from payouts.models import PayoutRequest
from server.tasks import process_payout


@pytest.fixture
def api_client():
    """Фикстура для создания API клиента."""
    return APIClient()


@pytest.fixture
def payout_data():
    """Фикстура с данными для создания заявки на выплату."""
    return {
        'payment_sum': '1000.00',
        'currency': 'USD',
        'recipients_details': 'Bank Account: 1234567890, SWIFT: ABCDUS33',
        'comment': 'Test payout request'
    }


@pytest.mark.django_db
class TestPayoutRequestCreation:
    """Тесты для создания заявок на выплату."""

    def test_successful_payout_creation(self, api_client, payout_data):
        """
        Тест успешного создания заявки на выплату.
        - Заявка успешно создается через API
        - Все поля сохраняются корректно
        - Статус устанавливается в OPEN по умолчанию
        - Возвращается правильный HTTP статус
        """
        url = reverse('payouts-list')
        response = api_client.post(url, payout_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['payment_sum'] == '1000.00'
        assert data['currency'] == 'USD'
        assert data['recipients_details'] == 'Bank Account: 1234567890, SWIFT: ABCDUS33'
        assert data['comment'] == 'Test payout request'
        assert data['status'] == PayoutRequest.PayoutRequestStatus.OPEN
        assert PayoutRequest.objects.count() == 1
        payout = PayoutRequest.objects.first()
        assert payout.payment_sum == Decimal('1000.00')
        assert payout.currency == 'USD'
        assert payout.status == PayoutRequest.PayoutRequestStatus.OPEN
        assert payout.id == data['id']

    def test_payout_creation_without_comment(self, api_client):
        """
        Тест создания заявки без комментария (опциональное поле).
        """
        url = reverse('payouts-list')
        data = {
            'payment_sum': '500.00',
            'currency': 'EUR',
            'recipients_details': 'IBAN: DE89370400440532013000'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['comment'] is None or response_data['comment'] == ''

    def test_payout_creation_validation_errors(self, api_client, payout_data):
        """
        Тест валидации при создании заявки.
        """
        url = reverse('payouts-list')
        invalid_data = payout_data.copy()
        invalid_data['payment_sum'] = '-100.00'
        response = api_client.post(url, invalid_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        invalid_data = payout_data.copy()
        del invalid_data['currency']
        response = api_client.post(url, invalid_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        invalid_data = payout_data.copy()
        invalid_data['recipients_details'] = ''
        response = api_client.post(url, invalid_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
class TestCeleryTaskIntegration:
    """Тесты для проверки интеграции с Celery."""

    @patch('payouts.views.process_payout.delay')
    def test_celery_task_called_on_payout_creation(
        self, mock_task_delay, api_client, payout_data
    ):
        """
        Тест проверки вызова Celery-задачи при создании заявки.
        - Celery задача вызывается после успешного создания заявки
        - Задача вызывается с правильным ID заявки
        - Задача вызывается через transaction.on_commit
        Использует transaction=True для правильной работы transaction.on_commit
        """
        url = reverse('payouts-list')
        mock_task_delay.reset_mock()
        response = api_client.post(url, payout_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        payout_id = response.json()['id']
        assert PayoutRequest.objects.filter(id=payout_id).exists()
        mock_task_delay.assert_called_once_with(payout_id)

    @patch('payouts.views.process_payout.delay')
    def test_celery_task_receives_correct_payout_id(
        self, mock_task_delay, api_client, payout_data
    ):
        """
        Тест проверки передачи правильного ID в Celery задачу.
        Использует mock для проверки вызова задачи с правильным ID.
        """
        url = reverse('payouts-list')
        mock_task_delay.reset_mock()
        response = api_client.post(url, payout_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        payout_id = response.json()['id']
        assert PayoutRequest.objects.filter(id=payout_id).exists()
        mock_task_delay.assert_called_once()
        call_args = mock_task_delay.call_args[0]
        assert call_args[0] == payout_id


@pytest.mark.django_db
class TestPayoutRequestList:
    """Тесты для получения списка заявок."""

    def test_get_payout_list(self, api_client):
        """Тест получения списка заявок."""
        # Создаем тестовые заявки
        PayoutRequest.objects.create(
            payment_sum=Decimal('100.00'),
            currency='USD',
            recipients_details='Account: 1111'
        )
        PayoutRequest.objects.create(
            payment_sum=Decimal('200.00'),
            currency='EUR',
            recipients_details='Account: 2222'
        )
        url = reverse('payouts-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data or isinstance(data, list)
        results = data.get('results', data) if isinstance(data, dict) else data
        assert len(results) == 2

    def test_get_payout_detail(self, api_client):
        """Тест получения детальной информации о заявке."""
        payout = PayoutRequest.objects.create(
            payment_sum=Decimal('500.00'),
            currency='RUB',
            recipients_details='Account: 3333',
            comment='Test comment'
        )
        url = reverse('payouts-detail', kwargs={'pk': payout.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == payout.id
        assert data['payment_sum'] == '500.00'
        assert data['currency'] == 'RUB'
        assert data['comment'] == 'Test comment'


@pytest.mark.django_db
class TestCeleryTaskExecution:
    """Тесты для выполнения Celery задачи."""

    def test_process_payout_task_success(self):
        """
        Тест успешного выполнения Celery задачи обработки заявки.
        """
        payout = PayoutRequest.objects.create(
            payment_sum=Decimal('1000.00'),
            currency='USD',
            recipients_details='Bank Account: 1234567890'
        )
        assert payout.status == PayoutRequest.PayoutRequestStatus.OPEN
        process_payout(payout.id)
        payout.refresh_from_db()
        assert payout.status == PayoutRequest.PayoutRequestStatus.RESOLVED

    def test_process_payout_task_already_processed(self):
        """
        Тест обработки уже обработанной заявки.
        """
        payout = PayoutRequest.objects.create(
            payment_sum=Decimal('500.00'),
            currency='EUR',
            recipients_details='Account: 1111',
            status=PayoutRequest.PayoutRequestStatus.RESOLVED
        )
        process_payout(payout.id)
        payout.refresh_from_db()
        assert payout.status == PayoutRequest.PayoutRequestStatus.RESOLVED

    @pytest.mark.django_db
    def test_process_payout_task_not_found(self, caplog):
        non_existent_id = 99999
        with caplog.at_level(logging.ERROR):
            process_payout(non_existent_id)
        assert f"Payout {non_existent_id} not found" in caplog.text
