from io import BytesIO
from django.core.files.base import ContentFile
from django import forms
from PIL import Image

from .models import Store


class StoreSliderUploadForm(forms.Form):
    slider_image = forms.ImageField(widget=forms.ClearableFileInput(), required=False)
    x_1 = forms.FloatField(widget=forms.HiddenInput())
    y_1 = forms.FloatField(widget=forms.HiddenInput())
    width_1 = forms.FloatField(widget=forms.HiddenInput())
    height_1 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, *args, **kwargs):
        data = self.data
        store = kwargs.get('store')

        store_slider_image = store.slider_image
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
            resized_image = cropped_image.resize((1921, 998), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), store_slider_image.name)

            store.slider_image.save(store_slider_image.name, img_content, save=False)


class StoreHeaderUploadForm(forms.ModelForm):
    header_image = forms.ImageField(widget=forms.ClearableFileInput(), required=False)
    x_2 = forms.FloatField(widget=forms.HiddenInput())
    y_2 = forms.FloatField(widget=forms.HiddenInput())
    width_2 = forms.FloatField(widget=forms.HiddenInput())
    height_2 = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Store
        fields = ('header_image', )

    def save(self, *args, **kwargs):
        data = self.data
        store = kwargs.get('store')

        store_header_image = store.header_image
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
            resized_image = cropped_image.resize((1920, 960), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), store_header_image.name)

            store.header_image.save(store_header_image.name, img_content, save=False)