from django.contrib import admin
from .models import Coach, Athlete, Token, Person, Income, Expense

# Register your models here.
admin.site.register(Person)
admin.site.register(Coach)
admin.site.register(Athlete)
admin.site.register(Token)
admin.site.register(Income)
admin.site.register(Expense)