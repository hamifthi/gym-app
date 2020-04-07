from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import render, redirect

from .forms import PersonCreationForm
from .models import Person, Coach
from finance.models import Income, Expense
from datetime import date

@receiver(user_logged_in, sender=Person)
def check_last_stipend_of_coach(sender, user, **kwargs):
    try:
        coach = Coach.objects.get(user=user)
        d1 = coach.last_transaction
        d2 = date.today()
        delta = d2 - d1
        if delta.days == 0:
            coach.last_transaction = d2
            Income.objects.create(detail='This month stipend', amount=coach.last_transaction,
            user=coach)
    except:
        pass

@receiver(user_logged_in, sender=Person)
def check_last_payment_of_athlete(sender, user, **kwargs):
    try:
        athlete = Athlete.objects.get(user=user)
        d1 = athlete.last_transaction
        d2 = date.today()
        delta = d2 - d1
        if delta.days > 30:
            athlete.last_transaction = d2
            Expense.objects.create(detail='This month gym membership', date=d2,
            amount=athlete.last_transaction, user=coach)
    except:
        pass