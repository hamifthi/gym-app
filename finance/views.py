from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.apps import apps

from finance.models import Income, Expense

from dateutil import relativedelta

Token = apps.get_model('users', 'Token')

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class SubmitIncome(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.get(token=token).user
        if 'date' not in request.POST:
            date = datetime.datetime.now()
        else:
            date = request.POST['date']
        Income.objects.create(user=user, amount=request.POST['amount'],
        details=request.POST['details'], date=date)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitExpense(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.get(token=token).user
        if 'date' not in request.POST:
            date = datetime.datetime.now()
        else:
            date = request.POST['date']
        Expense.objects.create(user=user, amount=request.POST['amount'],
        details=request.POST['details'], date=date)
        return JsonResponse({
            'status': 'ok'
        }, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class IncomeTransactionReport(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # add other situations whether if the user doesn't exist or there are no transactions
        token = request.POST['token']
        user = Token.objects.filter(token=token).get().user
        if 'from' and 'to' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            income = Income.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        return JsonResponse({'income': income}, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class ExpenseTransactionReport(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.filter(token=token).get().user
        if 'from' and 'to' in request.POST:
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
        else:
            expense = Expense.objects.filter(user=user).aggregate(Count('amount'), Sum('amount'))
        return JsonResponse({'expense': expense}, encoder=JSONEncoder)

@method_decorator(csrf_exempt, name='dispatch')
class TotalTransactionReport(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        token = request.POST['token']
        user = Token.objects.filter(token=token).get().user
        if 'from' and 'to' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['to']))\
                .aggregate(Count('amount'), Sum('amount'))
        elif 'from' in request.POST:
            income = Income.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
            relativedelta.relativedelta(months=+1)).aggregate(Count('amount'),
            Sum('amount'))
            expense = Expense.objects.filter(user=user,
            date__gte=datetime.date.fromisoformat(request.POST['from']),
            date__lte=datetime.date.fromisoformat(request.POST['from']) + \
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