from django.urls import path
from . import views

urlpatterns = [
    path('create_athlete/',  views.CreateAthlete.as_view()),
    path('create_coach/', views.CreateCoach.as_view()),
]