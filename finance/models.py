from django.utils.timezone import now
from django.db import models

from utils_module.utils import random_code

# Create your models here.
class FinancialTradeOff(models.Model):
    details = models.CharField(max_length=250, null=True)
    date = models.DateTimeField(default=now)
    amount = models.BigIntegerField(null=True)
    user = models.ForeignKey('users.Person', on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=48, default=random_code)

    class Meta:
        abstract = True

class Income(FinancialTradeOff):
    def __str__(self):
        return f'{self.user} {self.date} {self.amount} toman'

class Expense(FinancialTradeOff):
    def __str__(self):
        return f'{self.user} {self.date} {self.amount} toman'