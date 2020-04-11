from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form
from django import forms

from .widgets import BootstrapDateTimePickerInput, BootstrapDatePickerInput
from .models import Income, Expense

class IncomeSubmitForm(ModelForm):

    class Meta:
        model = Income
        exclude = ['user', 'code']
        help_texts = {'details': ('Please describe how do you earn this income'),
                                'amount': ('How much do you make?'),}
        error_messages = {'details': {'invalid': 'You must explain how you earn this income'},
                                          'amount': {'invalid': 'How much this is important. don\' forget that'}}
        widgets =  {
            'date': BootstrapDateTimePickerInput(attrs={'autocomplete':'off'}), # datepicker pop up
        }


class ExpenseSubmitForm(ModelForm):
    
    class Meta:
        model = Expense
        exclude = ['user', 'code']
        help_texts = {'details': ('Please describe how do you spend this money'),
                                'amount': ('How much do you spend?'),}
        error_messages = {'details': {'invalid': 'You must explain how you spend this money'},
                                          'amount': {'invalid': 'How much this is important. don\' forget that'}}
        widgets =  {
            'date': BootstrapDateTimePickerInput(attrs={'autocomplete':'off'}), # datepicker pop up
        }

class ReportForm(Form):
    choices = (
        ('income', 'Income'),
        ('expense', 'Expense')
    )
    report_choice = forms.ChoiceField(
        choices=choices, required=True, initial=None,
        help_text='Which one of your transactions do you want to see?')
    from_date = forms.DateField(
        widget=BootstrapDatePickerInput(attrs={'autocomplete':'off'}),
        input_formats=['%d-%m-%Y'],
        help_text='Please pick a from date to see incomes or leave blank to see all of your incomes',
        required=False
        )
    to_date = forms.DateField(
        widget=BootstrapDatePickerInput(attrs={'autocomplete':'off'}),
        input_formats=['%d-%m-%Y'],
        help_text='Please pick a from date to see incomes or leave blank to see all of your incomes',
        required=False
        )