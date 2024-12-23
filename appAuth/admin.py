from django.contrib import admin
from .models import User, Profile, OneTimePassword


class UserAdmin(admin.ModelAdmin):
        list_display = ['id', 'username', 'email']
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(OneTimePassword)