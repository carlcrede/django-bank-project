from django.db import DatabaseError, models, transaction
import uuid, httpx, django_rq
from rq import Retry
from django.conf import settings
from django.core.validators import MinValueValidator
from bank_app.models import Ledger
from ..errors import InsufficientFunds

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
    def reserve_transfer(cls, serialized_data, external_transfer, external_t_acc, debit_account, bank_url):
        response = httpx.post(f'http://{bank_url}/bank/api/v1/transfer', json=serialized_data.data)
        response.raise_for_status()

        # If reaching this line, we know the receiving bank has created the external transfer in RESERVED state
        django_rq.enqueue(
            confirm_local_transfer,
            serialized_data, 
            external_transfer, 
            external_t_acc,
            debit_account,
            bank_url,
            retry=Retry(max=3, interval=5),
            on_failure=transfer_failed
        )

def confirm_local_transfer(serialized_data, external_transfer, external_t_acc, debit_account, bank_url):
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
        confirm_transfer,
        serialized_data,
        external_transfer,
        external_t_acc,
        debit_account,
        bank_url,
        retry=Retry(max=3, interval=5),
        on_failure=transfer_failed
    )

def confirm_transfer(serialized_data, external_transfer, external_t_acc, debit_acc, bank_url):
    response = httpx.get(f'http://{bank_url}/bank/api/v1/confirm/{external_transfer.pk}')
    response.raise_for_status()

    external_transfer.status = TransferStatus.COMPLETED
    external_transfer.save()

    django_rq.enqueue(
        complete_transfer,
        serialized_data,
        external_transfer,
        external_t_acc,
        debit_acc,
        bank_url,
        retry=Retry(max=3, interval=5),
        on_failure=transfer_failed
    )

def complete_transfer(serialized_data, external_transfer, external_t_acc, debit_acc, bank_url):
    response = httpx.get(f'http://{bank_url}/bank/api/v1/complete/{external_transfer.pk}')
    response.raise_for_status()

def transfer_failed(job, connection, type, value, traceback):
    if job.retries_left:
        return

    external_transfer = job.args[1]
    external_t_acc = job.args[2]
    customer_acc = job.args[3]
    bank_url = job.args[4]
   
    if (
        external_transfer.status == TransferStatus.RESERVED or 
        external_transfer.status == TransferStatus.CONFIRMED
    ):
        external_transfer.status = TransferStatus.FAILED
        external_transfer.save()
        httpx.get(f'http://{bank_url}/bank/api/v1/failed/{external_transfer.pk}')

    if external_transfer.status == TransferStatus.COMPLETED:
        try:
            with transaction.atomic():
                Ledger.transfer(
                    amount=external_transfer.amount,
                    debit_account=external_t_acc,
                    debit_text='external transfer reversal',
                    credit_account=customer_acc,
                    credit_text='external transfer reversal',
                    direct_transaction_with_bank=True
                )
                external_transfer.status = TransferStatus.FAILED
                external_transfer.save()
        except Exception as exc:
            print('Something has gone really wrong :(', exc)
        
        httpx.get(f'http://{bank_url}/bank/api/v1/failed/{external_transfer.pk}')