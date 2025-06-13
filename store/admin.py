# store/admin.py
from django.contrib import admin
from .models import Product, Category, Order, OrderItem

admin.site.register(Product)
admin.site.register(Category)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'created_at']
    inlines = [OrderItemInline]


admin.site.register(OrderItem)
