from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):

    class Rank(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        SILVER = 'SILVER', 'Silver'
        GOLD = 'GOLD', 'Gold'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=8)
    rank = models.CharField(
        choices = Rank.choices,
        default = Rank.BASIC,
        max_length=6
    )