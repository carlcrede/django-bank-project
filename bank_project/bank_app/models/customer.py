from __future__ import annotations
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from .account import Account
from .ledger import Ledger
from datetime import datetime


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

    def account(self, ban) -> Account:
        account = Account.objects.get(customer=self, is_loan=False, ban=ban)
        return account

    @property
    def loans(self) -> QuerySet:
        return Account.objects.filter(customer=self, is_loan=True)

    
    def loan(self, ban) -> QuerySet:
        loan = Account.objects.get(customer=self, is_loan=True, ban=ban)
        return loan

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    def get_loan(self, ban, amount):
        # get bank account, create loan account(assigned to customer) -> tranfer(ledger table) between bank and loan the amount
        # get customer's account by ban -> transfer from loan account to customer account the amount
        bank_account = Account.objects.get(ban="021578155")
        customer_account = self.account(ban)
        
        with transaction.atomic():
            print(self)
            loan = Account.objects.create(name=f"Loan {datetime.now()}", customer=self, is_loan=True)
            print(ban, amount)
            print("customer_account: ", customer_account)
            transfer_from_bank_to_loan = Ledger.transfer(amount=float(amount), debit_account=bank_account, debit_text="debit", credit_account=loan, credit_text="creadit", is_loan=True)
            transfer_from_loan_to_customer_account = Ledger.transfer(amount=float(amount), debit_account=loan, debit_text="debit", credit_account=customer_account, credit_text="creadit", is_loan=True)

        return loan
        # user = User.objects.get(username=customer_username)
        # customer = Customer.objects.get(user=user)
        # customer.rank = new_rank
        # customer.save()
        # return customer