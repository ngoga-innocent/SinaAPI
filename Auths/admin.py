from django.contrib import admin
from .models import User
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name', 'email', 'is_staff')
admin.site.register(User,UserAdmin)