from django.db import DatabaseError, models, transaction
import uuid, httpx, django_rq
from rq import Retry
from django.conf import settings
from django.core.validators import MinValueValidator
from bank_app.models import Ledger
from ..errors import InsufficientFunds
import logging

class TransferStatus(models.TextChoices):
    RESERVED = 'RESERVED', 'Reserved'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'

class ExternalTransfer(models.Model):

    idempotency_key = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    status = models.CharField(
        choices=TransferStatus.choices,
        default=TransferStatus.RESERVED,
        max_length=9
    )

    debit_account = models.CharField(max_length=10)
    credit_account= models.CharField(max_length=10)
    to_bank = models.CharField(max_length=5)
    from_bank=models.CharField(max_length=5, default=settings.BANK_REGISTRATION_NUMBER)
    amount = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0.0)])
    text = models.CharField(max_length=200, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, amount, debit_account, credit_account, to_bank, text):
        if debit_account.available_balance < amount:
            raise InsufficientFunds

        return ExternalTransfer.objects.create(
            amount=amount,
            debit_account=debit_account.ban,
            credit_account=credit_account,
            to_bank=to_bank,
            text=text
        )

    @classmethod
    def transfer(cls, serialized_data, external_transfer, external_t_acc, debit_account):
        # step 3
        response = httpx.post(f'http://localhost:{external_transfer.to_bank}/bank/api/v1/transfer', json=serialized_data.data)
        response.raise_for_status()
        django_rq.enqueue(
            confirm_transfer, 
            external_transfer, 
            external_t_acc,
            debit_account,
            retry=Retry(max=3, interval=5),
            on_failure=transfer_failed
        )

def transfer_failed(job, connection, type, value, traceback):
    if job.retries_left:
        return

    external_transfer = job.args[1]
    # Transfer job failed
    # Change ExternalTransfer status to failed
    # let receiving bank know transfer is failed
    if external_transfer.status == TransferStatus.RESERVED:
        external_transfer.status = TransferStatus.FAILED
        external_transfer.save()
        #httpx.get(f'http://localhost:{external_transfer.to_bank}/bank/api/v1/failed/{external_transfer.pk}')


    # Confirm job failed
    if external_transfer.status == TransferStatus.CONFIRMED:
        external_transfer.status = TransferStatus.FAILED
        external_transfer.save()

    # Complete job failed
    if external_transfer.status == TransferStatus.COMPLETED:
        ...
    
    print('last retry failed')
    logging.debug('last retry failed')

def confirm_transfer(external_transfer, external_t_acc, debit_account):
    try:
        with transaction.atomic():
            Ledger.transfer(
                amount=external_transfer.amount, 
                debit_account=debit_account, 
                debit_text=external_transfer.text, 
                credit_account=external_t_acc, 
                credit_text=external_transfer.text, 
            )
            external_transfer.status = TransferStatus.CONFIRMED
            external_transfer.save()
    except InsufficientFunds as err:
        raise err
    except DatabaseError as err:
        raise err
    

    django_rq.enqueue(
        complete_transfer, 
        external_transfer,
        retry=Retry(max=3, interval=5),
        on_failure=transfer_failed
    )

def complete_transfer(external_transfer):
    response = httpx.get(f'http://localhost:{external_transfer.to_bank}/bank/api/v1/confirm/{external_transfer.pk}')
    response.raise_for_status()

    external_transfer.status = TransferStatus.COMPLETED
    external_transfer.save()