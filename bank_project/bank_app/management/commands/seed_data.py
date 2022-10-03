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

        # Create Employee User
        dummy_employee = Employee.create_employee(fname='Donald', lname='Duck', email='donald@duck.com', uname='DonaldD', passwd='mirror12')

        # Create Customer User with 2 Account
        dummy_customer = Employee.create_customer(fname='Dummy', lname='Dimwit', email='dummy@dummy.com', uname='DummyD',phone='12341234', passwd='mirror12')
        dummy_customer_account1 = Employee.create_account(customer_username='DummyD', acc_name= "Dummy Customer Account 1")
        dummy_customer_account2 = Employee.create_account(customer_username='DummyD', acc_name= "Dummy Customer Account 2")
