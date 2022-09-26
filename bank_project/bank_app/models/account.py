from django.db import models
from .customer import Customer

class Account(models.Model):
    name = models.CharField(max_length=60)
    is_loan = models.BooleanField(default=False)
    account_uuid = models.UUIDField(unique=True)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)
    deactivated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def balance(self):
        pass

    def transaction_history(self):
        pass
