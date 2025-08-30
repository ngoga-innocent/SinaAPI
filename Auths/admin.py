from django.contrib import admin
from .models import User,Notification,DeviceToken
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name', 'email', 'is_staff')
admin.site.register(User,UserAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at',)
admin.site.register(Notification,NotificationAdmin)


admin.site.register(DeviceToken)