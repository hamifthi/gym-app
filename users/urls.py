from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    # path('create_athlete/',  views.CreateAthlete.as_view(), name='register_athlete'),
    # path('create_coach/', views.CreateCoach.as_view(), name='register_coach'),
]