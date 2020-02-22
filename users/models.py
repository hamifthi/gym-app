from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time
from multiselectfield import MultiSelectField
from .choices import *

class Person(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100, null=True)
    password = models.CharField(max_length=50, null=True)
    age = models.IntegerField()
    sport_field = models.CharField(max_length=1, choices=Sport_Field)
    days_of_week = MultiSelectField(choices=Day_Choices)
    code = models.CharField(max_length=28, null=True)

    def __str__(self):
                return f'{self.name}_{self.last_name}'

class Token(models.Model):
    user = models.OneToOneField(Person, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    
    def __str__(self):
            return f'{self.user.name}_token'

# Coach class
class Coach(Person):
    salary = models.BigIntegerField()
    start_time = models.TimeField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)
    
    def __str__(self):
        return f'{self.name }_{self.last_name}'

# Athlete class
class Athlete(Person):
    last_payment = models.DateField()
    trainer = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.name }_{self.last_name}'