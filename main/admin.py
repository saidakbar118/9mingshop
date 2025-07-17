from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "discount_percent", "category")
    list_filter = ("category",)
    
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'total_price', 'created_at']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

admin.site.register(Banner_model)