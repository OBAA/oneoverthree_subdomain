from django.contrib import admin

from .models import Tag


# Register your admins here.
class TagAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_banner', 'ordering', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_banner', 'ordering', 'is_active']

    class Meta:
        model = Tag


admin.site.register(Tag, TagAdmin)
