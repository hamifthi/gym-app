from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from users.models import Person
import re

class RegisterForm(ModelForm):
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

    # Add validation for fields
    class Meta:
        model = Person
        exclude = ['code']
        help_texts = {'name': ('please enter your name here. pay attention that it must be\
                                                at least 4 character'),
                                'last_name': ('please enter your last_name here. pay attention that it must be\
                                                at least 4 character'),
                                'email': ('confirmation link will be sent to this address'),
                                'password': ('please enter your password. it must be at least 8 characters')}
        error_messages = {'email': {'invalid_email': 'confirmation link will be sent to this address'},
                                          'password': {'invalid_password': 'please enter your password. it must be at\
                                               least 8 characters'}}