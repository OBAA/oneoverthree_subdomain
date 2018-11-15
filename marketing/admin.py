from django.contrib import admin
from .models import MarketingPreference

# Register your models here.


class MarketingPreferenceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'subscribed', 'updated']
    readonly_fields = ['mailchimp_subscribed', 'mailchimp_msg', 'timestamp', 'updated']
    class Meta:
        model = MarketingPreference
        fields = [
            'user',
            'subscribed',
            'mailchimp_msg'
            'timestamp'
            'updated'
        ]


admin.site.register(MarketingPreference, MarketingPreferenceAdmin)

