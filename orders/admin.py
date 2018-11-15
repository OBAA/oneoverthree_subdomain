from django.contrib import admin

from .models import Order, OrderItem


# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'billing_profile', 'status', 'is_active', 'timestamp']
    list_filter = ['status', 'is_active', 'timestamp']
    list_editable = ['status', 'is_active']

    class Meta:
        model = Order


admin.site.register(Order, OrderAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'size', 'quantity', 'order', 'store', 'status', 'is_active']
    list_filter = ['status', 'is_active']
    list_editable = ['status', 'is_active']

    class Meta:
        model = Order


admin.site.register(OrderItem, OrderItemAdmin)
