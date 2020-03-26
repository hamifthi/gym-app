from django.contrib import admin
from .models import Coach, Athlete, Token, Person, Income, Expense, Day

class DayAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        number_of_days = Day.objects.count()
        if number_of_days >= 7:
            return False
        else:
            return True

# Register your models here.
admin.site.register(Person)
admin.site.register(Coach)
admin.site.register(Athlete)
admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(Token)
admin.site.register(Day, DayAdmin)