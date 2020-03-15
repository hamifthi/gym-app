from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.admin import widgets
from django.forms import ModelForm
from django import forms

from .widgets import FengyuanChenDatePickerInput
from users.models import Person, Athlete

import re

class PersonRegisterForm(ModelForm):
    class Meta:
        model = Person
        exclude = ['code']
        help_texts = {'name': ('please enter your name here. pay attention that it must be\
                                                at least 4 character'),
                                'last_name': ('please enter your last_name here. pay attention that it must be\
                                                at least 4 character'),
                                'email': ('confirmation link will be sent to this address'),
                                'password': ('please enter your password. it must be at least 8 characters')}
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

class AthleteRegisterForm(ModelForm):

    class Meta:
        model = Athlete
        fields = '__all__'
        widgets =  {
            'last_payment': FengyuanChenDatePickerInput(), # specify date-frmat
         }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['trainer'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        