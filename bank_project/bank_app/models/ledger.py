from uuid import uuid4
from django.db import models, transaction
from ..errors import InsufficientFunds
from django.db.models.signals import post_save
from django.dispatch import receiver
from .notification import Notification

class Ledger(models.Model):
    transaction_id = models.UUIDField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    text = models.CharField(max_length=200, null=True)
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    direct_transaction_with_bank = models.BooleanField(default=False) # indicates a transfer/transaction between the self.account to bank account

    @classmethod
    def transfer(
        cls, amount, debit_account, 
        debit_text, credit_account, 
        credit_text, is_loan=False, 
        direct_transaction_with_bank=False, 
        external_transfer=False
    ):
        assert amount >= 0, 'Transfer amount must be a positive number'
        uuid = uuid4()
        with transaction.atomic():
            if external_transfer or direct_transaction_with_bank or is_loan or debit_account.available_balance >= amount:
                cls(transaction_id=uuid, amount=-amount, text=debit_text, account=debit_account, direct_transaction_with_bank=direct_transaction_with_bank).save()
                cls(transaction_id=uuid, amount=amount, text=credit_text, account=credit_account, direct_transaction_with_bank=direct_transaction_with_bank).save()
            else: 
                raise InsufficientFunds
        return uuid

    @classmethod
    def total_balance(cls):
        ledgers = cls.objects.all()
        balance = ledgers.aggregate(models.Sum('amount'))['amount__sum']
        return balance

# Send signal to the customer when a ledger row that includes them is created
@receiver(post_save, sender=Ledger, dispatch_uid="post_save_ledger_notification")
def post_save_ledger_notification(sender, instance, **kwargs):
    print("**** Ledger signal received")
    if instance.amount > 0:
        print(f'{instance.account} received {abs(instance.amount)} dkk with text: "{instance.text}"')
        Notification.objects.create(
            customer=instance.account.customer, 
            message=f'You received {abs(instance.amount)} dkk with text: "{instance.text}" in your account {instance.account}'
        )
    else:
        print(f'{instance.account} sent {abs(instance.amount)} dkk with text: "{instance.text}"')
        Notification.objects.create(
            customer=instance.account.customer, 
            message=f'You sent {abs(instance.amount)} dkk with text: "{instance.text}" from your account {instance.account}'
            )

