from django.contrib import admin

from django_auth_system.models import User

# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     pass



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'is_active')
