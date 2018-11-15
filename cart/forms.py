from django import forms


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]


class CartUpdateForm(forms.Form):
    size = forms.Select(choices="")
    quantity = forms.IntegerField(max_value=10, min_value=1)

