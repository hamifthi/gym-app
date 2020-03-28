from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, reverse
from django.db.models import Count, Sum
from django.core.mail import send_mail
from django.conf import settings
from django.views import View

from users.models import Person, Token, Expense, Income, Athlete, Coach
from .utils import user_recaptcha_fails
from dateutil import relativedelta
from json import JSONEncoder
from .choices import *
from .forms import *

import os, binascii
import requests
import datetime
import jwt

@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        form = PersonRegisterForm(request.POST)
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
            password = make_password(form.cleaned_data['password'])
            user_account = Person.objects.create(name=name, last_name=last_name, email=email,
            password=password)
            message = f"To activate your account please click on this link \
                {request.build_absolute_uri('/register/')}?email={email}&code={user_account.code}"
            send_mail('Activating your account', message, settings.EMAIL_HOST_USER,
            recipient_list=[email])
            message = 'The activation link has been sent to your account'
            return render(request, 'register.html', {'message': message, 'form': PersonRegisterForm()})
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
                    user = Person.objects.get(email=email)
                    Person.objects.filter(code=code).update(code=None)
                    payload = {
                        'id' : user.id,
                        'email': user.email
                    }
                    token = Token.objects.create(user=user,
                    token=jwt.encode(payload, settings.SECRET_KEY))
                    message = f'Your account has been activated please save your token is \
                    {token.token} because it will not show to you again'
                    return render(request, 'register.html', {'message': message, 'form': PersonRegisterForm()})
                else:
                    error_message = 'This code is unvalid, please try again'
                    return render(request, 'register.html', {'error_message': error_message,
                    'form': PersonRegisterForm()}, status=404)
            else:
                error_message = 'Your request doesn\'t have email or code or both of them'
                return render(request, 'register.html', {'error_message': error_message,
                'form': PersonRegisterForm()}, status=404)
        # load the register page for the first visit
        else:
            message = 'Welcome. Please fill out the fields and Sign Up'
            return render(request, 'register.html', {'message': message, 'form': PersonRegisterForm()})
                
@method_decorator(csrf_exempt, name='dispatch')
class AthleteRegister(View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'athlete_register.html',
            {'error_message': error_message, 'form': AthleteRegisterForm()}, status=429)

        form = AthleteRegisterForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data['age']
            sport_field = form.cleaned_data['sport_field']
            days_of_week = form.cleaned_data['days_of_week']
            user = form.cleaned_data['user']
            coach = form.cleaned_data['trainer']
            user_account = Athlete.objects.create(age=age, sport_field=sport_field,
                                       user=user, trainer=coach)
            user_account.days_of_week.set(days_of_week)
            message = 'This user now becomes an athlete in your gym'
            return render(request, 'athlete_register.html',
            {'message': message, 'form': AthleteRegisterForm()})
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'athlete_register.html',
            {'error_message': error_message, 'form': form})
        
    def get(self, request, *args, **kwargs):
        message = 'Welcome to this page. Please fill out the fields and submit the form'
        return render(request, 'athlete_register.html', {'message': message, 'form': AthleteRegisterForm()})

@method_decorator(csrf_exempt, name='dispatch')
class CoachRegister(View):
    def post(self, request, *args, **kwargs):
        # user has the requestcode
        if user_recaptcha_fails(request):
            error_message = 'the captcha is not correct maybe you are robot?\
            please enter the code correctly'
            return render(request, 'coach_register.html',
            {'error_message': error_message, 'form': CoachRegisterForm()}, status=429)

        form = CoachRegisterForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data['age']
            sport_field = form.cleaned_data['sport_field']
            days_of_week = form.cleaned_data['days_of_week']
            user = form.cleaned_data['user']
            salary = form.cleaned_data['salary']
            user_account = Coach.objects.create(age=age, sport_field=sport_field,
                                    salary=salary, user=user)
            user_account.days_of_week.set(days_of_week)
            message = 'This user now becomes a coach in your gym'
            return render(request, 'coach_register.html',
            {'message': message, 'form': CoachRegisterForm()})
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'coach_register.html',
            {'error_message': error_message, 'form': form})
    
    def get(self, request, *args, **kwargs):
        message = 'Welcome to this page. Please fill out the fields and submit the form'
        return render(request, 'coach_register.html', {'message': message, 'form': CoachRegisterForm()})

@method_decorator(csrf_exempt, name='dispatch')
class SubmitIncome(View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.get(token=token).user
        if 'date' not in request.POST:
            date = datetime.datetime.now()
        else:
            date = request.POST['date']
        Income.objects.create(user=user, amount=request.POST['amount'],
        details=request.POST['details'], date=date)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitExpense(View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.get(token=token).user
        if 'date' not in request.POST:
            date = datetime.datetime.now()
        else:
            date = request.POST['date']
        Expense.objects.create(user=user, amount=request.POST['amount'],
        details=request.POST['details'], date=date)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class IncomeTransactionReport(View):
    def post(self, request, *args, **kwargs):
        # add other situations whether if the user doesn't exist or there are no transactions
        token = request.POST['token']
        user = Token.objects.filter(token=token).get().user
        if 'from' and 'to' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            income = Income.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        return JsonResponse({'income': income}, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class ExpenseTransactionReport(View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.filter(token=token).get().user
        if 'from' and 'to' in request.POST:
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            expense = Expense.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        return JsonResponse({'expense': expense}, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class TotalTransactionReport(View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.filter(token=token).get().user
        if 'from' and 'to' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            income = Income.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
            expense = Expense.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        info = {}
        info['income'] = income
        info['expense'] = expense
        info['total'] = income['amount__sum'] - expense['amount__sum']
        return JsonResponse(info, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class Login(View):
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        if Person.objects.filter(email=email).exists():
            user = Person.objects.get(email=email)
            if check_password(password, user.password):
                token = Token.objects.get(user=user).token
                context = {'token': token}
                return render(request, 'login.html', context)
            else:
                context = {'message': 'You entered wrong password please try again or if you forgot your\
                    password go to forgot pass page'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'You are not sign up yet please first sign up.'}
            return redirect(reverse('register'))

    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

@method_decorator(csrf_exempt, name='dispatch')
class ResetPassword(View):
    def post(self, request, *args, **kwargs):
        return render(request, 'resetpassword.html')

    def get(self, request, *args, **kwargs):
        return render(request, 'resetpassword.html')


@method_decorator(csrf_exempt, name='dispatch')
class Index(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'index.html', context)
