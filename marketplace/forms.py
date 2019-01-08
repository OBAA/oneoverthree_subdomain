from django import forms

from .models import Store


class StoreRegisterForm(forms.ModelForm):

    class Meta:
        model = Store
        fields = (
            'title', 'seller_type', 'description',
            'instagram', 'twitter', 'whatsapp',
        )

    def __init__(self, *args, **kwargs):
        super(StoreRegisterForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'placeholder': " Store / Brand name"})
        self.fields['description'].widget.attrs.update({'placeholder': " Store / Brand slogan"})
        self.fields['instagram'].widget.attrs.update({'placeholder': " IG-@handle"})
        self.fields['twitter'].widget.attrs.update({'placeholder': " IG-@handle"})
        self.fields['whatsapp'].widget.attrs.update({'placeholder': " +234-whatsapp"})
        for field in iter(self.fields):
            if field in ('background_image_a', 'background_image_b'):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'sizefull s-text7 p-l-15 p-r-15',
                })

    def save(self, commit=False, *args, **kwargs):
        store = super(StoreRegisterForm, self).save(commit=False)
        if commit:
            store.save()
        return store

