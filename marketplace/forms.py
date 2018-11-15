from io import BytesIO
from django.core.files.base import ContentFile
from django import forms
from PIL import Image

from .models import Store


class StoreRegisterForm(forms.ModelForm):

    class Meta:
        model = Store
        fields = (
            'title', 'seller_type', 'description',
            'instagram', 'twitter', 'whatsapp',
            'background_image_a', 'background_image_b',
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

    def clean(self):
        print(self.data)
        print(self.cleaned_data)

    def save(self, commit=False, *args, **kwargs):
        store = super(StoreRegisterForm, self).save(commit=False)
        if commit:
            store.save()
        return store


class StoreSliderUploadForm(forms.Form):
    x_1 = forms.FloatField(widget=forms.HiddenInput())
    y_1 = forms.FloatField(widget=forms.HiddenInput())
    width_1 = forms.FloatField(widget=forms.HiddenInput())
    height_1 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, *args, **kwargs):
        data = self.data
        store = kwargs.get('store')

        store_slider_image = store.background_image_a
        ext = str(store_slider_image).split('.', 1)[1]

        x = float(data.get('x_1'))
        y = float(data.get('y_1'))
        w = float(data.get('width_1'))
        h = float(data.get('height_1'))

        if store_slider_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(store_slider_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((1500, 500), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), store_slider_image.name)

            store.background_image_a.save(store_slider_image.name, img_content, save=False)


class StoreHeaderUploadForm(forms.Form):
    x_2 = forms.FloatField(widget=forms.HiddenInput())
    y_2 = forms.FloatField(widget=forms.HiddenInput())
    width_2 = forms.FloatField(widget=forms.HiddenInput())
    height_2 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, *args, **kwargs):
        data = self.data
        store = kwargs.get('store')

        store_header_image = store.background_image_b
        ext = str(store_header_image).split('.', 1)[1]

        x = float(data.get('x_2'))
        y = float(data.get('y_2'))
        w = float(data.get('width_2'))
        h = float(data.get('height_2'))

        if store_header_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(store_header_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((1920, 570), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), store_header_image.name)

            store.background_image_b.save(store_header_image.name, img_content, save=False)


