from django import forms

from .models import MarketingPreference


class MarketingPreferenceForm(forms.ModelForm):
    label = "Get Notifications on sales discounts and new arrivals on the site."
    subscribed = forms.BooleanField(label=label, required=False)

    class Meta:
        model = MarketingPreference
        fields = [
            'subscribed'
        ]
