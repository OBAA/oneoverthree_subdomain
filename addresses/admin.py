from django.contrib import admin

from .models import Address, ProductWeight, ShippingRate


# Register your models here.
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'city', 'country', 'per_kg']

    class Meta:
        model = ShippingRate


admin.site.register(ShippingRate, ShippingRateAdmin)


class ProductWeightAdmin(admin.ModelAdmin):
    list_display = ['product_type', 'weight']

    class Meta:
        model = ProductWeight


admin.site.register(ProductWeight, ProductWeightAdmin)


admin.site.register(Address)
