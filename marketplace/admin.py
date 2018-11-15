from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Store


# Register your models here.
class StoreMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ['__str__', 'seller_type', 'ordering', 'is_active', 'timestamp']
    list_filter = ['seller_type', 'is_active', 'ordering', 'timestamp']
    list_editable = ['ordering', 'is_active']

    class Meta:
        model = Store


admin.site.register(Store, StoreMPTTModelAdmin)
