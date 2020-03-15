from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db import models
from datetime import time

from multiselectfield import MultiSelectField
from .utils import random_code
from .choices import *

import datetime

class Person(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=False, unique=True, null=True)
    password = models.CharField(max_length=50 , blank=False, null=True)
    code = models.CharField(max_length=28, null=True, default=random_code)

    def __str__(self):
                return f'{self.name}_{self.last_name}'

class Token(models.Model):
    token = models.CharField(max_length=300)
    user = models.OneToOneField(Person, on_delete=models.CASCADE)
    
    def __str__(self):
            return f'{self.user.email}_token'

class Day(models.Model):
    day = models.CharField(max_length=9)
    number = models.IntegerField()

    def __str__(self):
        return f'{self.day}'

class GymAccount(models.Model):
    age = models.IntegerField(null=True)
    sport_field = models.CharField(max_length=1, choices=Sport_Field, null=True)
    days_of_week = models.ManyToManyField(Day, null=True)
    user = models.OneToOneField(Person, on_delete=models.CASCADE)

    class Meta:
        abstract = True

# Athlete class
class Athlete(GymAccount):
    last_payment = models.DateField(default=now)
    trainer = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True,
    related_name='user_trainer')

    def __str__(self):
        return f'{self.user.name}_{self.user.last_name}'

# Coach class
class Coach(GymAccount):
    salary = models.BigIntegerField()
    # start_time = models.TimeField(null=False, blank=False)
    # end_time = models.TimeField(null=False, blank=False)
    
    def __str__(self):
        return f'{self.user.name}_{self.user.last_name}'

class FinancialTradeOff(models.Model):
    details = models.CharField(max_length=250, null=True)
    date = models.DateTimeField(default=now)
    amount = models.BigIntegerField(null=True)
    user = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=48, default=random_code)

    class Meta:
        abstract = True

class Income(FinancialTradeOff):
    def __str__(self):
        return f'{self.user} {self.date} {self.amount} toman'

class Expense(FinancialTradeOff):
    def __str__(self):
        return f'{self.user} {self.date} {self.amount} toman'