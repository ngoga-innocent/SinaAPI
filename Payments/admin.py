from django.contrib import admin
from .models import Payment
# Register your models here.
@admin.register(Payment)  
class PaymentAdmin(admin.ModelAdmin):
    list_display=('id','ref','customer','phone_number','amount','status','created_at')
    list_filter=('status','created_at','phone_number')
    search_fields=('customer__username','phone_number')
# class OrderItemInline(admin.TabularInline):  # Use StackedInline for a different layout
#     model = OrderItem
#     extra = 1  # Allows adding extra items in admin
#     autocomplete_fields = ['product']  # Allows searching for products
#     readonly_fields = ('product', 'quantity')  # Prevent modification if needed

# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'payment', 'total_amount', 'status', 'created_at')
#     list_filter = ('status', 'created_at')
#     search_fields = ('user__username', 'payment__id', 'id')
#     readonly_fields = ('total_amount', 'created_at')  # Prevents modification
#     inlines = [OrderItemInline]  # Allows managing OrderItems inside OrderAdmin

# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity')
#     search_fields = ('order__id', 'product__name')

# admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem, OrderItemAdmin)    

    