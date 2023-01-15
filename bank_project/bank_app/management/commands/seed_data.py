import secrets, os, random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import Employee, Account, Ledger, Customer, Stock, Stocks_Ledger, Stock_Symbols
from django.conf import settings
from uuid import uuid4
from faker import Faker
fake = Faker(['da_DK'])
Faker.seed(random.randint(0, 1_000_000))


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding seed data ...')

        # Delete all data in all tables
        os.system("python manage.py flush --no-input")

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
            is_loan=True,
        )

        # Create account for all external transactions
        external_transfers_user = User.objects.create_user('external-transfers', password=secrets.token_urlsafe(64), is_active=False)
        external_transfers_as_customer = Customer.objects.create(user=external_transfers_user)
        external_transfers_account = Account.objects.create(customer=external_transfers_as_customer, name='External Transactions Account')

        # Create Employee User

        dummy_employee = Employee.create_employee(fname=fake.first_name(), lname=fake.last_name(), email=fake.email(), uname='dummyemp', passwd='mirror12')
        print("Dummy Employee is created")
        # Create Customer User with 2 Accounts
        dummy_customer = Employee.create_customer(fname=fake.first_name(), lname=fake.last_name(), email=fake.email(), uname='johndoe', phone=fake.phone_number(), passwd='mirror12', rank='SILVER')
        dummy_customer_account1 = Employee.create_account(customer_username='johndoe', acc_name="Checking Account")
        dummy_customer_account2 = Employee.create_account(customer_username='johndoe', acc_name= "Savings account")
        print("Fist Dummy Customer with 2 account is created")

        # Transfer funds to customers account
        Ledger.transfer(
            1000,
            ops_account,
            'Initial payout',
            dummy_customer_account1,
            'Initial payout',
        )

        # Create another Customer User with 2 Accounts
        dummy_customer2 = Employee.create_customer(fname=fake.first_name(), lname=fake.last_name(), email=fake.email(), uname='cena', phone=fake.phone_number(), passwd='mirror12')
        dummy_customer2_account1 = Employee.create_account(customer_username='cena', acc_name= "GAINS")
        dummy_customer2_account2 = Employee.create_account(customer_username='cena', acc_name= "Millionaire Account")
        print("Second Dummy Customer with 2 account is created")

        # Transfer funds to customers account
        Ledger.transfer(
            42060,
            ops_account,
            'Initial payout',
            dummy_customer2_account1,
            'Initial payout',
        )
        Ledger.transfer(
            1000000,
            ops_account,
            'Instant millionaire',
            dummy_customer2_account2,
            'Instant millionaire',
        )


        # Adding some stocks to Bank 
        bank_stock_symbols = Stock_Symbols.values
        for bank_stock_symbol in bank_stock_symbols:
            # print("bank: ", bank_as_customer)
            stock = Stock.save_new_stock(bank_stock_symbol, bank_as_customer)
            transaction_uuid = uuid4()
            print("Stock: ", stock)
            Stocks_Ledger.objects.create(transaction_id=transaction_uuid, stock=stock, stock_volume=100)
            # Stocks_Ledger.transfer_stock(0, 100, stock, ops_account, "bank stocks", stock, ops_account, "bank stocks", bank_stocks=True)
            print(f"Adding some {bank_stock_symbol} stocks to Bank")