from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('register/', views.Register.as_view(), name='register'),
    path('register/athlete', views.AthleteRegister.as_view(), name='athlete_register'),
    path('register/coach', views.CoachRegister.as_view(), name='coach_register'),
    path('submit/income', views.SubmitIncome.as_view(), name='submit_income'),
    path('submit/expense', views.SubmitExpense.as_view(), name='submit_expense'),
    path('report/income', views.IncomeTransactionReport.as_view(), name='income_report'),
    path('report/expense', views.ExpenseTransactionReport.as_view(), name='expense_report'),
    path('report/total', views.TotalTransactionReport.as_view(), name='total_transaction_report'),
    path('reset_password', views.ResetPassword.as_view(), name='reset_password'),
    path('login', views.Login.as_view(), name='login'),
]