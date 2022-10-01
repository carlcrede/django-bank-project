from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    employee = models.OneToOneField(User, on_delete=models.CASCADE)

    def create_customer(self, *data):
        pass

    def create_account(self, *data):
        pass

    # def __str__(self):
    #         return self.employee

    @classmethod
    def create_employee(self, fname, lname, email, uname, passwd):
        new_user = User.objects.create_user(first_name=fname, last_name=lname, email=email, username=uname, password=passwd)
        # print(f"user: {user}")
        new_empoyee = Employee.objects.create(employee=new_user)
        # print(f"new_empoyee {new_empoyee}")
        return new_empoyee