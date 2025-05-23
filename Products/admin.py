from django.contrib import admin
from .models import ShopCategory, ProductCategory, Product, Accompaniment,FoodCategory, Food,Order

@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)  # Allows searching by title
    ordering = ('-created_at',)  # Newest categories first
    readonly_fields = ('created_at',)
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)  # Search by name

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','is_pick_and_go','delivery_time', 'created_at')
    list_filter = ('shop_category', 'product_category')  # Add filter sidebar
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    autocomplete_fields = ('shop_category', 'product_category','possible_accompaniments') 
    readonly_fields = ('created_at',)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in ["product_category", "shop_category", "possible_accompaniments", "thumbnail"]:
            form.base_fields[field_name].required = False  # Mark as not required
        return form
@admin.register(Accompaniment)
class AccompanimentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    
@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name',)
    list_filter = ('category',)    
# admin.site.register(Order)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'payment_status', 'created_at')
    search_fields = ('user__phone_number', 'user__id')  
    list_filter = ('payment_status',)  

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # print("Admin Panel Orders:", queryset)  # Debugging
        return queryset
