from __future__ import annotations
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from .account import Account


class Customer(models.Model):

    class Rank(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        SILVER = 'SILVER', 'Silver'
        GOLD = 'GOLD', 'Gold'

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    phone = models.CharField(max_length=8)
    rank = models.CharField(
        choices=Rank.choices,
        default=Rank.BASIC,
        max_length=6
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # customer_uuid

    def __str__(self) -> str:
        return f"{self.user.last_name}, {self.user.first_name} - {self.rank}"

    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(customer=self, is_loan=False)

    @property
    def loans(self) -> QuerySet:
        return Account.objects.filter(customer=self, is_loan=True)

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"
