from django.shortcuts import render

from .forms import PersonCreationForm
from .models import Coach, Athlete
# from datetime.date import today

def user_is_coach(function):
    def wrap(request, *args, **kwargs):
        try:
            coach = Coach.objects.get(user=request.user)
            message = f'{request.user.name} you are a coach and you can not become a(n)\
                {request.get_full_path()[16:-1]} again.'
            return render(
                request, 'register.html', {'message': message, 'form': PersonCreationForm()}, status=403
            )
        except:
            return function(request, *args, **kwargs)
    return wrap

def user_is_athlete(function):
    def wrap(request, *args, **kwargs):
        try:
            athlete = Athlete.objects.get(user=request.user)
            message = f'{request.user.name} you are an athlete and you can not become a(n)\
                {request.get_full_path()[16:-1]} again.'
            return render(
                request, 'register.html', {'message': message, 'form': PersonCreationForm()}, status=403
            )
        except:
            return function(request, *args, **kwargs)
    return wrap