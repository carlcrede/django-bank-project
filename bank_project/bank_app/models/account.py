from decimal import Decimal
from bank_app.models import ExternalTransfer, TransferStatus
from django.db import models
from django.db.models.query import QuerySet
from ..util import gen_ban, gen_iban
from django.db.models import Q
from bank_app.models import Ledger

class Account(models.Model):
    # maybe generate more realistic account id (IBAN) with schwifty

    name = models.CharField(max_length=60)
    is_loan = models.BooleanField(default=False)
    ban = models.CharField(max_length=10, default=gen_ban, primary_key=True)
    iban = models.CharField(max_length=34, default=gen_iban)
    customer = models.ForeignKey(to="Customer", on_delete=models.PROTECT)
    deactivated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    @property
    def available_balance(self) -> Decimal:
        actual_balance = self.balance
        sent_transactions = (
            ExternalTransfer.objects
            .filter(Q(debit_account=self.ban))
            .exclude(Q(status=TransferStatus.COMPLETED) | Q(status=TransferStatus.FAILED))
            .aggregate(models.Sum('amount'))['amount__sum']
        or 0) * -1
        return round(sum([actual_balance, sent_transactions]), 2)

    @property
    def movements(self) -> QuerySet:
        movements = Ledger.objects.filter(account=self, direct_transaction_with_bank=False).order_by('-created_at')
        # if self.is_loan:
        #     # since the transfer from bank account to loan account was done first and is last in 
        #     #   array(because we order by date in movements function and the oldest transactions are at the end),
        #     #   we can use all the ledgers except the last one
        #     movements_without_bank_to_loan = movements.filter(direct_transaction_with_bank=False)
        #     # size = movements_without_direct_transaction_with_bank.count()
        #     # index_for_bank_to_loan_movement = size - 1
        #     # movements_without_bank_to_loan = movements_without_direct_transaction_with_bank[index_for_bank_to_loan_movement]
        #     return movements_without_bank_to_loan
        return movements

    def __str__(self) -> str:
        return f'({self.pk}) {self.name}'