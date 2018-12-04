from django.db import models
from billing.models import BillingProfile

#
DISCOUNT_RATES = [(i*5, str(i*5)) for i in range(1, 16)]


class CouponCodeQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_active=True)


class CouponCodeManager(models.Manager):
    def get_queryset(self):
        return CouponCodeQuerySet(self.model, using=self._db)

    def get_coupon(self, code):
        print(2)
        qs = self.get_queryset().all().filter(code=code)
        print(qs)
        if qs.count() == 1:
            coupon = qs.first()
            print(coupon)
            # valid = True
        else:
            coupon = None
            # valid = False
        return coupon


class CouponCode(models.Model):
    code = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=120)
    percentage = models.PositiveIntegerField(blank=True, choices=DISCOUNT_RATES)
    amount = models.IntegerField(blank=True, null=True)
    usage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    first_order_coupon = models.BooleanField(default=False)

    objects = CouponCodeManager()

    def __str__(self):
        return self.description


class UsedCouponManager(models.Manager):
    def new_or_get(self, coupon, billing_profile):
        obj, created = self.model.objects.get_or_create(
            coupon=coupon,
            billing_profile=billing_profile
        )
        return obj, created


class UsedCoupon(models.Model):
    coupon = models.ForeignKey(CouponCode)
    billing_profile = models.ForeignKey(BillingProfile)
    coupon_used = models.BooleanField(default=False)

    objects = UsedCouponManager()



