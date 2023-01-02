from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    model = CustomUser
    list_display = ['username', 'first_name', 'email', 'is_staff', ]


admin.site.register(CustomUser, CustomUserAdmin)
