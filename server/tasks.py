import logging
import time
from celery import shared_task

from django.db import transaction

from payouts.models import PayoutRequest


logger = logging.getLogger(__name__)


@shared_task(
    bind=True, autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5}
)
def process_payout(self, payout_id: int):
    """
    Асинхронная обработка заявки на выплату.
    Демонстрирует интеграцию Django + Celery.
    """
    # логи на английском писал я сам)
    logger.info("Start processing payout %s", payout_id)
    try:
        with transaction.atomic():
            payout = (
                PayoutRequest.objects
                .select_for_update()
                .get(id=payout_id)
            )
            if payout.status != PayoutRequest.PayoutRequestStatus.OPEN:
                logger.warning(
                    "Payout %s in another status (status=%s)",
                    payout.id,
                    payout.status
                )
                return
            payout.status = PayoutRequest.PayoutRequestStatus.IN_PROGRESS
            payout.save(update_fields=["status"])
        logger.info("Payout %s processing...", payout_id)
        time.sleep(3)
        # всегда положительно закончиваем процесс
        is_ok = True
        with transaction.atomic():
            payout = PayoutRequest.objects.select_for_update(
            ).get(id=payout_id)
            payout.status = (
                PayoutRequest.PayoutRequestStatus.RESOLVED
                if is_ok
                else PayoutRequest.PayoutRequestStatus.CANSELLED
            )
            payout.save(update_fields=["status"])
        logger.info(
            "Payout %s save with status=%s",
            payout_id,
            payout.status
        )
    except PayoutRequest.DoesNotExist:
        logger.error("Payout %s not found", payout_id)
