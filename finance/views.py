from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.views import View
from django.apps import apps

from .models import Income, Expense
from .forms import *

from dateutil import relativedelta
import datetime

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class SubmitIncome(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = IncomeSubmitForm(request.POST)
        if form.is_valid():
            details = form.cleaned_data['details']
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            user = request.user
            Income.objects.create(details=details, date=date, amount=amount, user=user)
            return redirect('home')
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'submit_income.html', context={'error_message': error_message,
            'form': form}, status=422)

    def get(self, request, *args, **kwargs):
        message = 'Welcome, please fill out the form below and submit your income'
        return render(request, 'submit_income.html', {'message': message, 'form': IncomeSubmitForm()})

@method_decorator(csrf_exempt, name='dispatch')
class SubmitExpense(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = ExpenseSubmitForm(request.POST)
        if form.is_valid():
            details = form.cleaned_data['details']
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            user = request.user
            Expense.objects.create(details=details, date=date, amount=amount, user=user)
            return redirect('home')
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'submit_expense.html', context={'error_message': error_message,
            'form': form}, status=422)

    def get(self, request, *args, **kwargs):
        message = 'Welcome, please fill out the form below and submit your expense'
        return render(
            request, 'submit_expense.html', {'message': message, 'form': ExpenseSubmitForm()}
            )

@method_decorator(csrf_exempt, name='dispatch')
class IncomeTransactionReport(LoginRequiredMixin, ListView):
    def post(self, request, *args, **kwargs):
        # add other situations whether if the user doesn't exist or there are no transactions
        form = IncomeReportForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            return redirect('income_report')
        else:
            error_message = 'Please solve the error and try again'
            return render(request, 'report_income.html', context={'error_message': error_message,
            'form': form}, status=422)

    def get(self, request, *args, **kwargs):
        if from_date and to_date != None:
            incomes = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(to_date)).all()
        elif from_date != None:
            incomes = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).all()
        else:
            incomes = Income.objects.filter(user=user).all()
        page = request.POST.get('page', 1)
        paginator = Paginator(incomes, 5)
        try:
            incomes = paginator.page(page)
        except PageNotAnInteger:
            incomes = paginator.page(1)
        except EmptyPage:
            incomes = paginator.page(paginator.num_pages)
        message = 'This is your requested list of incomes'
        return render(request, 'report_income.html', {'message': message, 'incomes': incomes})
        
        message = 'Welcome to this page for seeing a list of your incomes'
        return render(
            request, 'report_income.html', {'message': message, 'form': IncomeReportForm()}
            )
        

@method_decorator(csrf_exempt, name='dispatch')
class ExpenseTransactionReport(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if 'from' and 'to' in request.POST:
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            expense = Expense.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        return JsonResponse({'expense': expense}, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class TotalTransactionReport(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if 'from' and 'to' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            income = Income.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
            expense = Expense.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        info = {}
        info['income'] = income
        info['expense'] = expense
        info['total'] = income['amount__sum'] - expense['amount__sum']
        return JsonResponse(info, encoder=JSONEncoder)