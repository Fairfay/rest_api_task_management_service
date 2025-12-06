from django.db import transaction

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from payouts.models import PayoutRequest
from payouts.serializers import (
    PayoutRequestSerializer
)
from server.tasks import process_payout


class PayoutRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заявками на выплату с асинхронной
    обработкой через Celery.
    """

    # permission уже есть в настройках
    queryset = PayoutRequest.objects.all()
    serializer_class = PayoutRequestSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        payout = serializer.save()
        transaction.on_commit(
            lambda: process_payout.delay(payout.id)
        )
