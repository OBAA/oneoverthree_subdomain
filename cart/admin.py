from django.contrib import admin
from .models import CouponCode, UsedCoupon


# Register your models here.
class CouponCodeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'code', 'percentage', 'usage', 'first_order_coupon', 'is_valid', 'is_valid_till']
    list_filter = ['first_order_coupon', 'is_active']
    list_editable = ['first_order_coupon', 'is_active']

    class Meta:
        model = CouponCode


admin.site.register(CouponCode, CouponCodeAdmin)


class UsedCouponAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'billing_profile']

    class Meta:
        model = UsedCoupon


admin.site.register(UsedCoupon, UsedCouponAdmin)
