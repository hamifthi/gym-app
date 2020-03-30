from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import PersonCreationForm, PersonChangeForm
from .models import Person, Coach, Athlete, Token, Income, Expense, Day

class PersonAdmin(UserAdmin):
    add_form = PersonCreationForm
    form = PersonChangeForm
    model = Person
    list_display = ('email', 'name', 'last_name')
    list_filter = ('email', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


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