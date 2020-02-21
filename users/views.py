from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from users.models import Person, Athlete, Coach, Token
from json import JSONEncoder
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
            name=request.POST['name']
            last_name=request.POST['last_name']
            email = request.POST['email']
            username = request.POST['username']
            password = make_password(request.POST['password'])
            age=request.POST['age']
            # sport_field=request.POST['sport_field']
            # days_of_week=request.POST['days_of_week']
            user_account = Person.objects.create(name=name,last_name=last_name, email=email,
            username=username, password=password, age=age, code=code)
            subject = 'Activating your account'
            message = f'To activate your account please click on this link\
                http://127.0.0.1:8000/users/register/?email={email}&code={code}'
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

# @method_decorator(csrf_exempt, name='dispatch')
# class CreateAthlete(View):
#     def post(self, request, *args, **kwargs):
#         trainer = Coach.objects.filter(name = request.POST['trainer'])[0]
#         token = binascii.b2a_hex(os.urandom(64))
#         athlete, _ = Athlete.objects.get_or_create(name=request.POST['name'],
#         last_name=request.POST['last_name'], age=request.POST['age'],
#         sex=request.POST['sex'], sport_field=request.POST['sport_field'],
#         days_of_week=request.POST['days_of_week'],
#         last_payment=request.POST['last_payment'], trainer=trainer)
#         Token.objects.create(user=athlete, token=token)
#         return JsonResponse({
#             'status': 'ok'
#         }, encoder=JSONEncoder)

# @method_decorator(csrf_exempt, name='dispatch')
# class CreateCoach(View):
#     def post(self, request, *args, **kargs):
#         token = binascii.b2a_hex(os.urandom(64))
#         coach, _ = Coach.objects.get_or_create(name=request.POST['name'],
#         last_name=request.POST['last_name'], age=request.POST['age'],
#         sex=request.POST['sex'], sport_field=request.POST['sport_field'],
#         days_of_week=request.POST['days_of_week'],
#         salary=request.POST['salary'], start_time=request.POST['start_time'],
#         end_time=request.POST['end_time'])
#         Token.objects.create(user=coach, token=token)
#         return JsonResponse({
#             'status': 'ok'
#         }, encoder=JSONEncoder)