from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.admin import widgets
from django.forms import ModelForm
from django import forms

from .widgets import FengyuanChenDatePickerInput
from users.models import Person, Athlete, Coach

import re

class PersonRegisterForm(ModelForm):
    class Meta:
        model = Person
        exclude = ['code']
        help_texts = {'name': ('Please enter your name here. pay attention that it must be\
                                                at least 4 character'),
                                'last_name': ('Please enter your last_name here. pay attention that it must be\
                                                at least 4 character'),
                                'email': ('confirmation link will be sent to this address'),
                                'password': ('Please enter your password. it must be at least 8 characters')}

        error_messages = {'email': {'invalid_email': 'this email is invalid. please enter a valid email.'},
                                          'password': {'invalid_password': 'please enter your password. it must be at\
                                               least 8 characters.'}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['last_name'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if email and not re.match(email_regex, email):
            raise ValidationError('Invalid email format')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as error:
            return error
        return password

class CoachRegisterForm(ModelForm):

    class Meta:
        model = Coach
        fields = '__all__'
        help_texts = {'age': ('Please enter your age here'),
                                'salary': ('Please enter your salary here.'),
                                'start_time': ('Work hour starting time'),
                                'end_time': ('Work hour ending time'),
                                'user': ('Who are you? Or better to say by which person are you?')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].widget.attrs['min'] = 10
        self.fields['age'].widget.attrs['max'] = 100
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False

class AthleteRegisterForm(ModelForm):

    class Meta:
        model = Athlete
        fields = '__all__'
        widgets =  {
            'last_payment': FengyuanChenDatePickerInput(), # specify date-frmat
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].widget.attrs['min'] = 10
        self.fields['age'].widget.attrs['max'] = 100
        self.fields['last_payment'].required = True
        self.fields['trainer'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        