from django.shortcuts import render

from .forms import PersonCreationForm
from .models import Coach, Athlete
# from datetime.date import today

def user_is_Coach(function):
    def wrap(request, *args, **kwargs):
        try:
            coach = Coach.objects.get(user=request.user)
            message = 'You are a coach. you can not become a coach again'
            return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})
        except:
            return function(request, *args, **kwargs)
    return wrap

def user_is_Athlete(function):
    def wrap(request, *args, **kwargs):
        try:
            athlete = Athlete.objects.get(user=request.user)
            message = 'You are an athlete. you can not become an athlete again'
            return render(request, 'register.html', {'message': message, 'form': PersonCreationForm()})
        except:
            return function(request, *args, **kwargs)
    return wrap