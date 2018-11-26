from django.contrib import admin

from .models import Dashboard


# Register your models here.
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'total_revenue']


admin.site.register(Dashboard, DashboardAdmin)

