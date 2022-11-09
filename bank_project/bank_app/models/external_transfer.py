from django.db import models

class ExternalTransfer(models.Model):

    class TransferStatus(models.TextChoices):
        RESERVED = 'RESERVED', 'Reserved'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    idempotency_key = models.UUIDField(unique=True, primary_key=True)
    status = models.CharField(
        choices=TransferStatus.choices,
        default=TransferStatus.RESERVED,
        max_length=9
    )

    created_at = models.DateTimeField(auto_now_add=True)