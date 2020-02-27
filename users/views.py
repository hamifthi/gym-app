from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from users.models import Person, Token, Expense, Income, Athlete, Coach
from json import JSONEncoder
from .choices import *
import os, binascii
import requests
import datetime

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def google_recaptcha_verify(request):
    captcha_response = request.POST.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_response,
        'remoteip': get_client_ip(request)
    }
    verify_response = requests.post(url=url, params=params, verify=True)
    verify_response = verify_response.json()
    return verify_response.get("success",)

@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        if 'requestcode' in request.POST:
            if not google_recaptcha_verify(request):
                context = {'message' : 'the captcha is not correct maybe you are robot? please enter the\
                    code correctly'}
                return render(request, 'register.html', context)

        # email is dupilicate
        if Person.objects.filter(email = request.POST['email']).exists():
            context = {'message' : 'this email has used before, if this is your email go to forgot password\
                and change your password'}
            return render(request, 'register.html', context)

        # new user
        if not Person.objects.filter(username = request.POST['username']).exists():
            code = binascii.b2a_hex(os.urandom(28))
            name = request.POST['name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            username = request.POST['username']
            password = make_password(request.POST['password'])
            user_account = Person.objects.create(name=name,last_name=last_name, email=email,
            username=username, password=password, code=code)
            subject = 'Activating your account'
            message = f"To activate your account please click on this link \
                {request.build_absolute_uri('/register/')}?email={email}&code={code}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            context = {'message' : 'The activation link has been sent to your account'}
            return render(request, 'register.html', context)
        else:
            context = {'message': 'This username has used before, please use another username'}
            return render(request, 'register.html', context)

    def get(self, request, *args, **kwargs):
        # user click on activation link
        if 'code' in request.GET:
            email = request.GET['email']
            code = request.GET['code']
            # person exist and we activate it
            if Person.objects.filter(code=code).exists():
                user = Person.objects.get(email=email)
                Person.objects.filter(code=code).update(code=None)
                token = binascii.b2a_hex(os.urandom(64))
                token = Token.objects.create(user=user, token=token)
                context = {'message': f'Your account has been activated please save your token is \
                {token.token} because it will not show to you again'}
                return render(request, 'register.html', context)
            else:
                context = {'message': 'This code is unvalid, please try again'}
                return render(request, 'register.html', context)
        # load the register page for the first visit
        else:
            context = {'message': ''}
            return render(request, 'register.html', context)
                

class AthleteRegister(View):
    def post(self, request, *args, **kwargs):
        if 'requestcode' in request.POST:
            if not google_recaptcha_verify(request):
                context = {'message' : 'the captcha is not correct maybe you are robot? please enter the\
                    code correctly'}
                return render(request,  'athlete_register.html', context)
        # get attributes
        email = request.POST['email']
        if Person.objects.filter(email=email).exists():
            user = Person.objects.filter(email=email).get()
        else:
            context = {'This user is not registered yet'}
            return render(request,  'athlete_register.html', context)
        age = request.POST['age']
        sport_field = request.POST['sport_field']
        # Here we can't normally send the sport_field for saving in DB we must send the code
        for sport in Sport_Field:
            if sport_field == sport[1]:
                sport_field = sport[0]
        # Here we can't normally send the days_of_week for saving in DB we must send the code
        days_of_week = request.POST['days_of_week']
        days_of_week = days_of_week.split(', ')
        list_of_days = []
        for day in Day_Choices:
            if day[1].lower() in days_of_week:
                list_of_days.append(day[0])
        user_account = Athlete.objects.create(age=age, sport_field=sport_field,
                                    days_of_week=list_of_days, user=user)

        context = {'message' : 'This user become an athlete in your gym now'}
        return render(request, 'athlete_register.html', context)
        
    def get(self, request, *args, **kwargs):
        context = {'message': ''}
        return render(request, 'athlete_register.html', context)

class CoachRegister(View):
    def post(self, request, *args, **kwargs):
        if 'requestcode' in request.POST:
            if not google_recaptcha_verify(request):
                context = {'message' : 'the captcha is not correct maybe you are robot? please enter the\
                    code correctly'}
                return render(request, 'coach_register.html', context)
        # get attributes
        email = request.POST['email']
        if Person.objects.filter(email=email).exists():
            user = Person.objects.filter(email=email).get()
        else:
            context = {'This user is not registered yet'}
            return render(request,  'coach_register.html', context)
        age = request.POST['age']
        sport_field = request.POST['sport_field']
        # Here we can't normally send the sport_field for saving in DB we must send the code
        for sport in Sport_Field:
            if sport_field == sport[1]:
                sport_field = sport[0]
        # Here we can't normally send the days_of_week for saving in DB we must send the code
        days_of_week = request.POST['days_of_week']
        days_of_week = days_of_week.split(', ')
        list_of_days = []
        for day in Day_Choices:
            if day[1].lower() in days_of_week:
                list_of_days.append(day[0])
        salary = request.POST['salary']
        user_account = Coach.objects.create(age=age, sport_field=sport_field,
                                    days_of_week=list_of_days, salary=salary, user=user)
        context = {'message' : 'This user become a coach in your gym now'}
        return render(request, 'coach_register.html', context)
    
    def get(self, request, *args, **kwargs):
        context = {'message': ''}
        return render(request, 'coach_register.html', context)

class Index(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'index.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitIncome(View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Person.objects.filter(token=token).get()
        if 'date' not in request.POST:
            date = datetime.datetime.now()
        Income.objects.create(user=user, amount=request.POST['amount'],
        details=request.POST['details'], date=date)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitExpense(View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Person.objects.filter(token=token).get()
        if 'date' not in request.POST:
            date = datetime.datetime.now()
        Expense.objects.create(user=user, amount=request.POST['amount'],
        details=request.POST['details'], date=date)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)