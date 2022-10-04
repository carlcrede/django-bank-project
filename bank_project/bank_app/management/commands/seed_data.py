import secrets
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import Employee, Account, Ledger, Customer


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding seed data ...')

        # bank_user = User.objects.create_user('bank', email='', password=secrets.token_urlsafe(64))
        # bank_user.is_active = False
        # bank_user.save()
        # ipo_account = Account.objects.create(user=bank_user, name='Bank IPO Account')
        # ops_account = Account.objects.create(user=bank_user, name='Bank OPS Account')
        # Ledger.transfer(
        #     10_000_000,
        #     ipo_account,
        #     'Operational Credit',
        #     ops_account,
        #     'Operational Credit',
        #     is_loan=True
        # )


        # Delete all data in all tables
        os.system("python manage.py flush")

        # Create SuperUser
        superuser = User.objects.create_superuser(username='super', password='super', email='super@gmail.com')
        self.stdout.write('SuperUser is created')

        # Create bank user and bank accounts
        bank_user = User.objects.create_user('bank', password=secrets.token_urlsafe(64), is_active=False)
        bank_as_customer = Customer.objects.create(user=bank_user)
        ipo_account = Account.objects.create(customer=bank_as_customer, name='Bank IPO Account')
        ops_account = Account.objects.create(customer=bank_as_customer, name='Bank OPS Account')
        
        # Transfer from banks investment acc to operational acc
        Ledger.transfer(
            amount=99_999_999,
            debit_account=ipo_account,
            debit_text='Operational Credit',
            credit_account=ops_account,
            credit_text='Operational Credit',
            is_loan=True
        )

        # Create Employee User
        dummy_employee = Employee.create_employee(fname='Donald', lname='Duck', email='donald@duck.com', uname='donaldd', passwd='mirror12')

        # Create Customer User with 2 Account
        dummy_customer = Employee.create_customer(fname='John', lname='Doe', email='john@doe.com', uname='johndoe', phone='12345678', passwd='mirror12')
        dummy_customer_account1 = Employee.create_account(customer_username='johndoe', acc_name= "Checking account")
        dummy_customer_account2 = Employee.create_account(customer_username='johndoe', acc_name= "Savings account")

        # Transfer funds to customers account
        Ledger.transfer(
            1000,
            ops_account,
            'Initial payout',
            dummy_customer_account1,
            'Initial payout',
        )
