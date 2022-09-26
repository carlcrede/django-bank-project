from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def create_customer(self, *data):
        pass

    def create_account(self, *data):
        pass