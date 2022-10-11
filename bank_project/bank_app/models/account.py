from decimal import Decimal
from enum import unique
from django.db import models
from django.db.models.query import QuerySet
from .ledger import Ledger
from ..util import gen_ban, gen_iban

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
    def movements(self) -> QuerySet:
        return Ledger.objects.filter(account=self).order_by('-created_at')

    def __str__(self) -> str:
        return f'({self.pk}) {self.name}'