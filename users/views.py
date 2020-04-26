from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views import View

from users.models import Person, Athlete, Coach
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
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            message = f"""To activate your account please click on this link {request.build_absolute_uri()}
                ?email={user.email}&code={user.code}"""
            send_mail(
                'Activating your account', message, settings.EMAIL_HOST_USER,recipient_list=[user.email]
            )
            message = 'The activation link has been sent to your account'
            return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})
        # form was invalid and user must correct the form and submit it again
        else:
            error_message = 'Please solve the error and try again'
            return render(
                request, 'register.html', {'error_message': error_message, 'form': form}, status=422
            )
    
    def get(self, request, *args, **kwargs):
        # user click on activation link
        if 'code' in request.GET:
            # check that the code and email isn't none or empty
            if request.GET['code'] != '' and request.GET['email'] != '':
                email = request.GET['email']
                code = request.GET['code']
                # person exist and we activate it
                if Person.objects.filter(code=code).exists():
                    Person.objects.filter(code=code).update(is_active=True)
                    Person.objects.filter(code=code).update(code=None)
                    user = Person.objects.get(email=email)
                    message = 'Your account has been activated.'
                    return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})
                else:
                    error_message = 'This code is invalid, please try again'
                    return render(request, 'register.html', {'error_message': error_message,
                    'form': PersonCreationForm()}, status=422)
            else:
                error_message = 'Your request doesn\'t have email or code or both of them'
                return render(request, 'register.html', {'error_message': error_message,
                'form': PersonCreationForm()}, status=422)
        # load the register page for the first visit
        else:
            message = 'Welcome. Please fill out the fields and Sign Up'
            return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})

@method_decorator(user_is_coach, name='dispatch')
@method_decorator(user_is_athlete, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class AthleteRegister(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = AthleteRegisterForm(request.POST)
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'register_athlete.html',
            {'error_message': error_message, 'form': form}, status=429)

        if form.is_valid():
            athlete = form.save(commit=False)
            athlete.user = request.user
            athlete.save()
            Expense.objects.create(
                details='user registration gym membership',
                amount=form.cleaned_data['transaction_amount'], user=request.user
            )
            message = f'{request.user.name}_{request.user.last_name} now becomes an athlete in your gym'
            return render(
                request, 'register_athlete.html',
                {'message': message, 'form': AthleteRegisterForm()}
            )
        else:
            error_message = 'Please solve the error and try again'
            return render(
                request, 'register_athlete.html',
                {'error_message': error_message, 'form': form}, status=422
            )
        
    def get(self, request, *args, **kwargs):
        message = 'Welcome to this page. Please fill out the fields and submit the form'
        return render(request, 'register_athlete.html', {'message': message, 'form': AthleteRegisterForm()})

@method_decorator(user_is_athlete, name='dispatch')
@method_decorator(user_is_coach, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CoachRegister(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CoachRegisterForm(request.POST)
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'register_coach.html',
            {'error_message': error_message, 'form': CoachRegisterForm()}, status=429)

        if form.is_valid():
            coach = form.save(commit=False)
            coach.user = request.user
            coach.save()
            message = f'{request.user.name}_{request.user.last_name} is a coach in your gym now'
            return render(
                request, 'register_coach.html',
                {'message': message, 'form': CoachRegisterForm()}
            )
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'register_coach.html',
            {'error_message': error_message, 'form': form}, status=422)
    
    def get(self, request, *args, **kwargs):
        message = 'Welcome to this page. Please fill out the fields and submit the form'
        return render(request, 'register_coach.html', {'message': message, 'form': CoachRegisterForm()})

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')