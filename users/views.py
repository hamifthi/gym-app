from django.shortcuts import render
from django.views import View
from users.models import Athlete, Coach, Token
from django.http import JsonResponse
from json import JSONEncoder
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os, binascii

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class CreateAthlete(View):
    def post(self, request, *args, **kargs):
        name = request.POST['name']
        last_name = request.POST['last_name']
        age =request.POST['age']
        sex = request.POST['sex']
        sport_field = request.POST['sport_field']
        days_of_week = request.POST['days_of_week']
        last_payment = request.POST['last_payment']
        trainer_name = request.POST['trainer']
        trainer = Coach.objects.filter(name = trainer_name)[0]
        token = binascii.b2a_hex(os.urandom(64))
        athlete, _ = Athlete.objects.get_or_create(name=name, last_name=last_name, age=age, 
        sex=sex, sport_field=sport_field, days_of_week=days_of_week,
        last_payment=last_payment, trainer=trainer)
        Token.objects.create(user=athlete, token=token)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class CreateCoach(View):
    def post(self, request, *args, **kargs):
        name = request.POST['name']
        last_name = request.POST['last_name']
        age =request.POST['age']
        sex = request.POST['sex']
        sport_field = request.POST['sport_field']
        days_of_week = list(request.POST['days_of_week'])
        salary = request.POST['salary']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        token = binascii.b2a_hex(os.urandom(64))
        coach, _ = Coach.objects.get_or_create(name=name, last_name=last_name, age=age, 
        sex=sex, sport_field=sport_field, days_of_week=days_of_week,
        salary=salary, start_time=start_time, end_time=end_time)
        Token.objects.create(user=coach, token=token)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)


