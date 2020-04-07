from django.urls import path, re_path, reverse_lazy
from . import views

urlpatterns = [
    path('income/submit/', views.SubmitIncome.as_view(), name='submit_income'),
    path('expense/submit/', views.SubmitExpense.as_view(), name='submit_expense'),
    path('income/report/', views.IncomeTransactionReport.as_view(), name='income_report'),
    path('expense/report/', views.ExpenseTransactionReport.as_view(), name='expense_report'),
    path('total/report/', views.TotalTransactionReport.as_view(), name='total_transaction_report'),
]