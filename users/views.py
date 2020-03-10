from django.shortcuts import render, redirect, reverse
from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.db.models import Count, Sum
from users.models import Person, Token, Expense, Income, Athlete, Coach
from json import JSONEncoder
from dateutil import relativedelta
from .choices import *
import os, binascii
import requests
import datetime
import jwt

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
                context = {'message' : 'the captcha is not correct maybe you are robot?\
                     please enter the code correctly'}
                return render(request, 'register.html', context, status=429)

        # new user
        if not Person.objects.filter(email = request.POST['email']).exists():
            code = binascii.b2a_hex(os.urandom(28)).decode('utf-8')
            name = request.POST['name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = make_password(request.POST['password'])
            user_account = Person.objects.create(name=name, last_name=last_name, email=email,
            password=password, code=code)
            subject = 'Activating your account'
            message = f"To activate your account please click on this link \
                {request.build_absolute_uri('/register/')}?email={email}&code={code}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            context = {'message' : 'The activation link has been sent to your account'}
            return render(request, 'register.html', context)
        else:
            context = {'message' : 'this email has used before, if this is your email go to forgot password\
                and change your password'}
            return render(request, 'register.html', context, status=409)
    
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
                    jwt_token = jwt.encode(payload, settings.SECRET_KEY)
                    token = Token.objects.create(user=user, token=jwt_token)
                    context = {'message': f'Your account has been activated please save your token is \
                    {token.token} because it will not show to you again'}
                    return render(request, 'register.html', context)
                else:
                    context = {'message': 'This code is unvalid, please try again'}
                    return render(request, 'register.html', context, status=404)
            else:
                context = {'message': 'Your request doesn\'t have email or code or both of them'}
                return render(request, 'register.html', context, status=404)
        # load the register page for the first visit
        else:
            context = {'message': ''}
            return render(request, 'register.html', context)
                
@method_decorator(csrf_exempt, name='dispatch')
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
            user = Person.objects.get(email=email)
        else:
            context = {'message' : 'This user is not registered yet'}
            return render(request,  'athlete_register.html', context, status=404)
        coach_email = request.POST['coach_email']
        if Person.objects.filter(email=coach_email).exists():
            coach = Person.objects.get(email=coach_email)
            # accessing to the coach attributes
            attributes = Coach.objects.get(user=coach)
        else:
            context = {'message' : 'This coach is not registered yet'}
            return render(request,  'athlete_register.html', context, status=404)
        age = request.POST['age']
        sport_field = request.POST['sport_field']
        # Here we can't normally send the sport_field for saving in DB we must send the code
        for sport in Sport_Field:
            if sport_field == sport[1]:
                sport_field = sport[0]
                # match the sport field of coach with athlete
                if sport_field != attributes.sport_field:
                    context = {'message' : 'This coach doesn\'t work in this field'}
                    return render(request,  'athlete_register.html', context, status=406)
        # Here we can't normally send the days_of_week for saving in DB we must send the code
        days_of_week = request.POST['days_of_week']
        days_of_week = days_of_week.split(', ')
        list_of_days = []
        for day in Day_Choices:
            if day[1].lower() in days_of_week:
                list_of_days.append(day[0])
        user_account = Athlete.objects.create(age=age, sport_field=sport_field,
                                    days_of_week=list_of_days, user=user, trainer=coach)
        context = {'message' : 'This user become an athlete in your gym now'}
        return render(request, 'athlete_register.html', context)
        
    def get(self, request, *args, **kwargs):
        context = {'message': ''}
        return render(request, 'athlete_register.html', context)

@method_decorator(csrf_exempt, name='dispatch')
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
            user = Person.objects.get(email=email)
        else:
            context = {'message' : 'This user is not registered yet'}
            return render(request,  'coach_register.html', context, status=404)
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
