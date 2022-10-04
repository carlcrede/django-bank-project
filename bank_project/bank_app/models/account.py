from decimal import Decimal
from uuid import uuid4
from django.db import models
from django.db.models.query import QuerySet
from .ledger import Ledger

class Account(models.Model):
    # maybe generate more realistic account id (IBAN) with schwifty

    name = models.CharField(max_length=60)
    is_loan = models.BooleanField(default=False)
    account_uuid = models.UUIDField(unique=True, default=uuid4)
    customer = models.ForeignKey(to="Customer", on_delete=models.PROTECT)
    deactivated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    @property
    def movements(self) -> QuerySet:
        return Ledger.objects.filter(account=self).order_by('-created_at')
