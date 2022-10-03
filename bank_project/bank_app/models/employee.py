from django.db import models
from django.contrib.auth.models import User
from .customer import Customer
from .account import Account
import uuid

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    @classmethod
    def create_employee(cls, fname, lname, email, uname, passwd):
        new_user = User.objects.create_user(first_name=fname, last_name=lname, email=email, username=uname, password=passwd)
        # print(f"user: {user}")
        new_empoyee = Employee.objects.create(user=new_user)
        # print(f"new_empoyee {new_empoyee}")
        return new_empoyee

    @classmethod  
    def create_customer(cls, fname, lname, email, uname, phone, passwd, rank='BASIC'):
        new_user = User.objects.create_user(first_name=fname, last_name=lname, email=email, username=uname, password=passwd)
        # print(f"user: {user}")
        new_customer = Customer.objects.create(user=new_user, phone=phone, rank=rank)
        # print(f"new_empoyee {new_customer}")
        return new_customer

    @classmethod
    def create_account(cls,  customer_username, acc_name):
        user = User.objects.get(username=customer_username)
        customer = Customer.objects.get(user=user)
        account_uuid = uuid.uuid4()
        new_account = Account.objects.create(name=acc_name, account_uuid=account_uuid, customer=customer)
        return new_account
        

    # def __str__(self):
    #         return self.employee
