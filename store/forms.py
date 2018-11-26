from io import BytesIO
from django import forms
from django.forms import formset_factory
from django.core.files.base import ContentFile
from PIL import Image

from .models import Product, ProductReview, Variation


# Enter your forms here.
class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = {
            'author', 'product', 'is_anonymous',
        }


class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'title', 'store', 'product_type', 'category',
            'description', 'extra_description', 'tags',
            'base_price', 'image_a', 'image_b', 'image_c',
            'stock', 'featured', 'has_variants', 'discount'
        )
        labels = {"featured": "Set as featured"}

    def __init__(self, *args, **kwargs):
        super(UpdateProductForm, self).__init__(*args, **kwargs)
        # initial_arguments = kwargs.get('initial', None)
        # print(initial_arguments)
        for field in iter(self.fields):
            if field in ('featured', 'has_variants'):
                pass
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                })

    def save(self, commit=True):
        product = super(UpdateProductForm, self).save(commit=False)
        if commit:
            product.save()
        return product


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'store', 'title', 'product_type', 'category', 'brand',
            'description', 'extra_description', 'tags', 'base_price',
            'image_a', 'image_b', 'image_c',
            'stock', 'featured'
        )
        labels = {"featured": "Set as featured"}

    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field in ('featured', 'has_variants'):
                pass
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })

    def clean(self):
        print(self.data)
        if self.errors:
            print(self.errors)
        print(self.cleaned_data)

    def save(self, commit=True):
        product = super(AddProductForm, self).save(commit=False)
        if commit:
            product.save()
        return product


class ImageAUploadForm(forms.Form):
    x_1 = forms.FloatField(widget=forms.HiddenInput())
    y_1 = forms.FloatField(widget=forms.HiddenInput())
    width_1 = forms.FloatField(widget=forms.HiddenInput())
    height_1 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, product, *args, **kwargs):
        data = self.data

        product_image = product.image_a
        ext = str(product_image).split('.', 1)[1]

        x = float(data.get('x_1'))
        y = float(data.get('y_1'))
        w = float(data.get('width_1'))
        h = float(data.get('height_1'))

        if product_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(product_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((480, 720), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), product_image.name)

            product.image_a.save(product_image.name, img_content, save=False)


class ImageBUploadForm(forms.Form):
    x_2 = forms.FloatField(widget=forms.HiddenInput())
    y_2 = forms.FloatField(widget=forms.HiddenInput())
    width_2 = forms.FloatField(widget=forms.HiddenInput())
    height_2 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, product, *args, **kwargs):
        data = self.data
        product_image = product.image_b
        ext = str(product_image).split('.', 1)[1]

        x = float(data.get('x_2'))
        y = float(data.get('y_2'))
        w = float(data.get('width_2'))
        h = float(data.get('height_2'))

        if product_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(product_image)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((480, 720), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), product_image.name)

            product.image_b.save(product_image.name, img_content, save=False)


class ImageCUploadForm(forms.Form):
    x_3 = forms.FloatField(widget=forms.HiddenInput())
    y_3 = forms.FloatField(widget=forms.HiddenInput())
    width_3 = forms.FloatField(widget=forms.HiddenInput())
    height_3 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, product, *args, **kwargs):
        data = self.data
        product_image = product.image_c
        ext = str(product_image).split('.', 1)[1]

        x = float(data.get('x_3'))
        y = float(data.get('y_3'))
        w = float(data.get('width_3'))
        h = float(data.get('height_3'))

        if product_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(product_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((480, 720), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), product_image.name)

            product.image_c.save(product_image.name, img_content, save=False)


class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = (
            'size', 'quantity'
        )

    def __init__(self, *args, **kwargs):
        super(ProductVariationForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, *args, **kwargs):
        variant = super(ProductVariationForm, self).save(commit=False)
        product = kwargs.get('product')
        if variant:
            variant.product = product
            return variant


ProductVariationFormSet = formset_factory(ProductVariationForm, extra=5, max_num=5)


class SizeVariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ('product',)  # , 'quantity', 'size', )
        labels = {"product": "size"}

    def __init__(self, product, *args, **kwargs):
        super(SizeVariationForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Variation.objects.filter(product=product)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


