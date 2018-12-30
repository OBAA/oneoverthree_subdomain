from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Product, ProductImage, ProductReview, Category, Variation  # , Brand


# Register your admins here.
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', '__str__', 'size', 'quantity', 'is_active']
    list_filter = ['is_active']
    list_editable = ['size', 'quantity', 'is_active']

    class Meta:
        model = Variation


admin.site.register(Variation, VariationAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'file', 'timestamp']

    class Meta:
        model = ProductImage


admin.site.register(ProductImage, ProductImageAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'store', 'sku', 'price', 'stock', 'is_active', 'timestamp']
    list_filter = ['is_active', 'timestamp']
    list_editable = ['price', 'is_active']

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'product', '__str__', 'is_active', 'timestamp']
    list_filter = ['is_active', 'timestamp']
    list_editable = ['is_active']

    class Meta:
        model = ProductReview


admin.site.register(ProductReview, ProductReviewAdmin)


class CategoryMPTTModelAdmin(MPTTModelAdmin):
    # specify pixel amount for this ModelAdmin only:
    mptt_level_indent = 20
    list_display = ['__str__', 'description', 'ordering', 'is_active']
    list_editable = ['ordering', 'is_active']


admin.site.register(Category, CategoryMPTTModelAdmin)

