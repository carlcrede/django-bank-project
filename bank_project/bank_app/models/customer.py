from __future__ import annotations
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .notification import Notification
from bank_app.models import Account, Ledger, Stock, ExternalTransfer


class Customer(models.Model):

    class Rank(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        SILVER = 'SILVER', 'Silver'
        GOLD = 'GOLD', 'Gold'

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15)
    secret_for_2fa = models.CharField(max_length=32, null=True)
    rank = models.CharField(
        choices=Rank.choices,
        default=Rank.BASIC,
        max_length=6
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # customer_uuid

    def __str__(self) -> str:
        return f"{self.user.last_name}, {self.user.first_name}, {self.user.username} - {self.rank}"

    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(customer=self, is_loan=False, deactivated=False)

    def account(self, ban) -> Account:
        account = Account.objects.get(customer=self, ban=ban, is_loan=False, deactivated=False)
        return account

    def account_by_name(self, name) -> Account:
        account = Account.objects.get(customer=self, name=name, is_loan=False, deactivated=False)
        return account

    @classmethod
    def default_bank_acc(cls):
        user = cls.objects.get(user__username='bank')
        acc = user.account_by_name('Bank OPS Account')
        return acc

    @classmethod
    def external_transactions_acc(cls):
        user = cls.objects.get(user__username='external-transfers')
        acc = user.account_by_name('External Transactions Account')
        return acc

    @property
    def loans(self) -> QuerySet:
        return Account.objects.filter(customer=self, is_loan=True, deactivated=False)

    def loan(self, ban) -> QuerySet:
        loan = Account.objects.get(customer=self, ban=ban, is_loan=True, deactivated=False)
        return loan

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def unread_notifications_count(self) -> QuerySet:
        return Notification.objects.filter(customer=self, is_read=False).count()

    @property
    def notifications(self) -> QuerySet:
        return Notification.objects.filter(customer=self)

    @property
    def unread_count(self):
        return Notification.objects.filter(customer = self, is_read=False).count()

    @property
    def external_transfers_sent(self):
        external_transfers = ExternalTransfer.objects.filter(
            Q(debit_account__in=self.accounts)
        )
        return external_transfers

    def get_loan(self, ban, amount):
        # get bank account, create loan account(assigned to customer) -> tranfer(ledger table) between bank and loan the amount
        # get customer's account by ban -> transfer from loan account to customer account the amount
        bank_account = Account.objects.get(ban=self.default_bank_acc().ban)
        customer_account = self.account(ban)

        with transaction.atomic():
            # print(self)
            loan = Account.objects.create(
                name=f"Loan {datetime.now()}", customer=self, is_loan=True)
            # print(ban, amount)
            # print("customer_account: ", customer_account)
            transfer_from_bank_to_loan = Ledger.transfer(amount=float(amount), debit_account=bank_account, debit_text="debit from bank",
                                                         credit_account=loan, credit_text="credit to loan", is_loan=True,  direct_transaction_with_bank=True)
            transfer_from_loan_to_customer_account = Ledger.transfer(amount=float(
                amount), debit_account=loan, debit_text="debit from loan", credit_account=customer_account, credit_text="credit to customer account", is_loan=True)

        return loan
        # user = User.objects.get(username=customer_username)
        # customer = Customer.objects.get(user=user)
        # customer.rank = new_rank
        # customer.save()
        # return customer

    def pay_loan(self, amount, customer_account, customer_text, loan_account, loan_text="test"):
        print(
            f"in pay_loan function -> amount: {amount}, customer_account: {customer_account}, customer_text: {customer_text}, loan_account: {loan_account}, loan_text:{loan_text}")

        # transfer from customer account to loan account the amount
        # get bank account -> tranfer amount from loan to bank account
        bank_account = Account.objects.get(ban=self.default_bank_acc().ban)

        with transaction.atomic():
            transfer_from_customer_account_to_loan = Ledger.transfer(amount=float(
                amount), debit_account=customer_account, debit_text=customer_text, credit_account=loan_account, credit_text=loan_text)
            transfer_from_loan_to_bank = Ledger.transfer(amount=float(amount), debit_account=loan_account, debit_text="debit from laon",
                                                         credit_account=bank_account, credit_text="credit to bank", is_loan=True, direct_transaction_with_bank=True)

        # ALSO check that the amount paid is not more than the loan amount
        if loan_account.available_balance >= 0:
            loan_account.deactivated = True
            loan_account.save()

        return customer_account

    @property
    def stocks(self):
        return Stock.stocks(self)
        # customer_stocks = Stock.stocks(self)
        # return [stock for stock in customer_stocks if stock.stock_volume > 0]
    
# Send signal to the customer when they are created or updated
@receiver(post_save, sender=Customer, dispatch_uid="post_save_customer_notification")
def post_save_customer_notification(sender, instance, created, update_fields, **kwargs):
        if created:
            print("**** Customer signal received")
            print(f'Welcome message sent to newly created customer!')
            Notification.objects.create(
               customer=instance, 
               message = "Welcome to Django Bank!"
            )
        elif update_fields: 
            print("**** Customer signal received")
            print(f'{update_fields} modified for customer {instance}')
            for field in list(update_fields):    
                Notification.objects.create(
                    customer=instance, 
                    message = f"Your {field} has been changed to {getattr(instance, field.__str__())}"
                )