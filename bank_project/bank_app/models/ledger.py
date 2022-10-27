from uuid import uuid4
from django.db import models, transaction
from ..errors import InsufficientFunds


class Ledger(models.Model):
    transaction_id = models.UUIDField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    text = models.CharField(max_length=200, null=True)
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    direct_transaction_with_bank = models.BooleanField(default=False)

    @classmethod
    def transfer(cls, amount, debit_account, debit_text, credit_account, credit_text, is_loan=False, direct_transaction_with_bank=False):
        assert amount >= 0, 'Transfer amount must be a positive number'
        uuid = uuid4()
        with transaction.atomic():
            if debit_account.balance >= amount or is_loan:
                cls(transaction_id=uuid, amount=-amount, text=debit_text, account=debit_account, direct_transaction_with_bank=direct_transaction_with_bank).save()
                cls(transaction_id=uuid, amount=amount, text=credit_text, account=credit_account, direct_transaction_with_bank=direct_transaction_with_bank).save()
            else: 
                raise InsufficientFunds
        return uuid
