from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from .models import User

class SuperUser(UserAdmin):
    ordering = ['id']

admin.site.register(User, SuperUser)
