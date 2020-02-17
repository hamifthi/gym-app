from django.contrib import admin
from .models import Coach, Athlete, Token

# Register your models here.
admin.site.register(Coach)
admin.site.register(Athlete)
admin.site.register(Token)