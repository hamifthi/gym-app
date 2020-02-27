from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('register/', views.Register.as_view(), name='register'),
    path('register/athlete', views.AthleteRegister.as_view(), name='athlete_register'),
    path('register/coach', views.CoachRegister.as_view(), name='coach_register'),
]