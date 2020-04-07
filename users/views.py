from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views import View

from users.models import Person, Token, Athlete, Coach
from utils_module.utils import user_recaptcha_fails
from finance.models import Expense
from json import JSONEncoder
from .decorators import *
from .forms import *
import jwt

@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        form = PersonCreationForm(request.POST)
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'register.html', {'error_message': error_message,
            'form': form}, status=429)
        # new user
        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password1'])
            user_account = Person.objects.create(name=name, last_name=last_name, email=email,
            password=password, is_active=False)
            message = f"To activate your account please click on this link {request.build_absolute_uri()}?email={email}&code={user_account.code}"
            send_mail('Activating your account', message, settings.EMAIL_HOST_USER,
            recipient_list=[email])
            message = 'The activation link has been sent to your account'
            return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'register.html', {'error_message': error_message, 'form': form},
            status=404)
    
    def get(self, request, *args, **kwargs):
        # user click on activation link
        if 'code' in request.GET:
            # check that the code and email isn't none or empty
            if request.GET['code'] != 'None' and request.GET['email'] != 'None':
                email = request.GET['email']
                code = request.GET['code']
                # person exist and we activate it
                if Person.objects.filter(code=code).exists():
                    Person.objects.filter(code=code).update(is_active=True)
                    Person.objects.filter(code=code).update(code=None)
                    user = Person.objects.get(email=email)
                    payload = {
                        'id' : user.id,
                        'email': user.email
                    }
                    token = Token.objects.create(user=user,
                    token = jwt.encode(payload, settings.SECRET_KEY))
                    message = f'Your account has been activated.'
                    return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})
                else:
                    error_message = 'This code is unvalid, please try again'
                    return render(request, 'register.html', {'error_message': error_message,
                    'form': PersonCreationForm()}, status=404)
            else:
                error_message = 'Your request doesn\'t have email or code or both of them'
                return render(request, 'register.html', {'error_message': error_message,
                'form': PersonCreationForm()}, status=404)
        # load the register page for the first visit
        else:
            message = 'Welcome. Please fill out the fields and Sign Up'
            return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})

@method_decorator(user_is_Athlete, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class AthleteRegister(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'register_athlete.html',
            {'error_message': error_message, 'form': AthleteRegisterForm()}, status=429)

        form = AthleteRegisterForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data['age']
            sport_field = form.cleaned_data['sport_field']
            days_of_week = form.cleaned_data['days_of_week']
            user = form.cleaned_data['user']
            coach = form.cleaned_data['trainer']
            transaction_amount = form.cleaned_data['transaction_amount']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            user_account = Athlete.objects.create(age=age, sport_field=sport_field, start_time=start_time,
                                        end_time=end_time, user=user, trainer=coach,
                                        transaction_amount=transaction_amount)
            user_account.days_of_week.set(days_of_week)
            Expense.objects.create(details='user registration gym membership',
                amount=transaction_amount, user=user)
            message = 'This user now becomes an athlete in your gym'
            return render(request, 'register_athlete.html',
            {'message': message, 'form': AthleteRegisterForm()})
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'register_athlete.html',
            {'error_message': error_message, 'form': form})
        
    def get(self, request, *args, **kwargs):
        message = 'Welcome to this page. Please fill out the fields and submit the form'
        return render(request, 'register_athlete.html', {'message': message, 'form': AthleteRegisterForm()})

@method_decorator(user_is_Coach, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CoachRegister(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'register_coach.html',
            {'error_message': error_message, 'form': CoachRegisterForm()}, status=429)

        form = CoachRegisterForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data['age']
            sport_field = form.cleaned_data['sport_field']
            days_of_week = form.cleaned_data['days_of_week']
            user = form.cleaned_data['user']
            transaction_amount = form.cleaned_data['transaction_amount']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            user_account = Coach.objects.create(age=age, sport_field=sport_field, start_time=start_time,
                                        end_time=end_time, transaction_amount=transaction_amount, user=user)
            user_account.days_of_week.set(days_of_week)
            message = 'This user now becomes a coach in your gym'
            return render(request, 'register_coach.html',
            {'message': message, 'form': CoachRegisterForm()})
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'register_coach.html',
            {'error_message': error_message, 'form': form})
    
    def get(self, request, *args, **kwargs):
        message = 'Welcome to this page. Please fill out the fields and submit the form'
        return render(request, 'register_coach.html', {'message': message, 'form': CoachRegisterForm()})

class Index(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'index.html', context)