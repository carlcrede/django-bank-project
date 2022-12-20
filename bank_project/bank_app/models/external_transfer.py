from django.db import models
import uuid
import os

class TransferStatus(models.TextChoices):
    RESERVED = 'RESERVED', 'Reserved'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'

class ExternalTransfer(models.Model):

    idempotency_key = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4())
    status = models.CharField(
        choices=TransferStatus.choices,
        default=TransferStatus.RESERVED,
        max_length=9
    )

    debit_account = models.CharField(max_length=10)
    credit_account= models.CharField(max_length=10)
    to_bank = models.CharField(max_length=5)
    from_bank=models.CharField(max_length=5, default=os.getenv('BANK_REGISTRATION_NUMBER'))
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    text = models.CharField(max_length=200, null=True)

    created_at = models.DateTimeField(auto_now_add=True)