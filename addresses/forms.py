from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    """
    User-related CRUD form
    """
    class Meta:
        model = Address
        fields = [
            'address_line_1',
            'city',
            'state',
            'country',
            'postal_code',
            'mobile_number',
            'default',
        ]

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field in ('featured', 'has_variants'):
                pass
            else:
                self.fields[field].widget.attrs.update({
                    # 'class': 'form-control'
                    'class': 'sizefull s-text7 p-l-15 p-r-15'
                })

    def save(self, commit=True):
        address = super(AddressForm, self).save(commit=False)
        if commit:
            address.save()
        return address


class CheckoutAddressForm(forms.ModelForm):
    class Meta:
        model   = Address
        fields  = [
            'name',
            'address_line_1',
            'city',
            'state',
            'country',
            'postal_code',
            'mobile_number',
            'default',
        ]

    def __init__(self, *args, **kwargs):
        super(CheckoutAddressForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field in ('featured', 'has_variants'):
                pass
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'sizefull s-text7 p-l-15 p-r-15'
                })

    def save(self, commit=False):
        address = super(CheckoutAddressForm, self).save(commit=False)
        if commit:
            address.save()
        return address

