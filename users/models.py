from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time
from multiselectfield import MultiSelectField
from .choices import *

# Create your models here.
# The person class which contains credentials of a person whether he or she is athelte or Coach
class Person(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=Sex_Choices)
    sport_field = models.CharField(max_length=1, choices=Sport_Field)
    days_of_week = MultiSelectField(choices=Day_Choices)

class Coach(Person):
    salary = models.BigIntegerField()
    start_time = models.TimeField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)
    
    def __str__(self):
        return f'{self.name }_{self.last_name}'

class Athelte(Person):
    last_payment = models.DateField()
    trainer = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.name }_{self.last_name}'