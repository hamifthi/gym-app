from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms

from .models import Income, Expense

class IncomeSubmitForm(ModelForm):
    class Meta:
        model = Income
        exclude = ['code']

class ExpenseSubmitForm(ModelForm):
    class Meta:
        model = Expense
        exclude = ['code']