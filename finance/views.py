from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.urls import reverse
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
class TransactionDisplay(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # add other situations whether if the user doesn't exist or there are no transactions
        form = ReportForm(request.POST)
        if form.is_valid():
            request.session['from_date'] = str(form.cleaned_data['from_date'])
            request.session['to_date'] = str(form.cleaned_data['to_date'])
            if form.cleaned_data['report_choice'] == 'income':
                return redirect(reverse('report_income'))
            elif form.cleaned_data['report_choice'] == 'expense':
                return redirect(reverse('report_expense'))
            else:
                return redirect(reverse('total_transaction_report'))
        else:
            error_message = 'Please solve the error and try again.'
            return render(request, 'report_income.html', context={'error_message': error_message,
            'form': form}, status=422)

    def get(self, request, *args, **kwargs):
            message = 'Welcome to this page for seeing a list of your transactions.'
            return render(
                request, 'report_display.html', {'message': message, 'form': ReportForm()}
                )
    
@method_decorator(csrf_exempt, name='dispatch')
class IncomeTransactionReport(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'report_income.html'
    context_object_name = 'incomes'
    paginate_by = 5

    def get_queryset(self):
        from_date = self.request.session['from_date']
        to_date = self.request.session['to_date']
        user = self.request.user
        if from_date != 'None' and to_date != 'None':
            incomes = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(to_date)).all()
        elif from_date != 'None':
            incomes = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).all()
        else:
            incomes = Income.objects.filter(user=user).all()
        return incomes

@method_decorator(csrf_exempt, name='dispatch')
class ExpenseTransactionReport(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'report_expense.html'
    context_object_name = 'expenses'
    paginate_by = 5

    def get_queryset(self):
        from_date = self.request.session['from_date']
        to_date = self.request.session['to_date']
        user = self.request.user
        if from_date != 'None' and to_date != 'None':
            expenses = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(to_date)).all()
        elif from_date != 'None':
            expenses = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).all()
        else:
            expenses = Expense.objects.filter(user=user).all()
        return expenses

@method_decorator(csrf_exempt, name='dispatch')
class TotalTransactionReport(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from_date = self.request.session['from_date']
        to_date = self.request.session['to_date']
        user = self.request.user
        if from_date != 'None' and to_date != 'None':
            incomes = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(to_date))\
                .aggregate(Count('amount'), Sum('amount'))
            expenses = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(to_date))\
                .aggregate(Count('amount'), Sum('amount'))
        elif from_date != 'None':
            incomes = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
            expenses = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(from_date),
            date__lte=datetime.date.fromisoformat(from_date) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            incomes = Income.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
            expenses = Expense.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        del self.request.session['from_date']
        del self.request.session['to_date']
        total = incomes['amount__sum'] - expenses['amount__sum']
        return render(request, 'report_total.html', {'incomes': incomes, 'expenses': expenses,
        'total': total})