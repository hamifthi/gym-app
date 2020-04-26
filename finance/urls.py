from django.urls import path, re_path, reverse_lazy
from . import views

urlpatterns = [
    path('submit/income/', views.SubmitIncome.as_view(), name='submit_income'),
    path('submit/expense/', views.SubmitExpense.as_view(), name='submit_expense'),
    path('report/form/', views.TransactionReportForm.as_view(), name='report_form'),
    path('report/income/', views.IncomeTransactionReport.as_view(), name='report_income'),
    path('report/expense/', views.ExpenseTransactionReport.as_view(), name='report_expense'),
    path('report/total/', views.TotalTransactionReport.as_view(), name='total_transaction_report'),
]