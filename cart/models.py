from django.db import models
from billing.models import BillingProfile
from datetime import timedelta
from django.utils import timezone


#
DISCOUNT_RATES = [(i*5, str(i*5)) for i in range(1, 16)]


class CouponCodeQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_active=True)


class CouponCodeManager(models.Manager):
    def get_queryset(self):
        return CouponCodeQuerySet(self.model, using=self._db)

    def get_coupon(self, code):
        now = timezone.now()
        qs = self.get_queryset().all().filter(code=code)
        print(qs)
        valid = False
        if qs.count() == 1:
            coupon = qs.first()
            valid_till = coupon.timestamp + timedelta(days=coupon.is_valid_till)
            if valid_till > now:
                valid = True
            # else:
            #     coupon.is_valid = False
        else:
            coupon = None

        return coupon, valid


class CouponCode(models.Model):
    code = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=120)
    percentage = models.PositiveIntegerField(blank=True, choices=DISCOUNT_RATES)
    amount = models.IntegerField(blank=True, null=True)
    usage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    first_order_coupon = models.BooleanField(default=False)
    is_one_use_only = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)
    is_valid_till = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CouponCodeManager()

    def __str__(self):
        return self.description


class UsedCouponQuerySet(models.query.QuerySet):
    def xp(self):
        return self.filter(is_active=True)


class UsedCouponManager(models.Manager):
    def get_queryset(self):
        return UsedCouponQuerySet(self.model, using=self._db)

    def new_or_get(self, coupon, billing_profile):
        obj, created = self.model.objects.get_or_create(
            coupon=coupon,
            billing_profile=billing_profile
        )
        return obj, created

    def get_valid_coupon(self, coupon, billing_profile):
        # print("A")
        coupon = CouponCode.objects.get_coupon(coupon)
        # obj = self.model.objects.get(
        #     coupon=coupon,
        #     billing_profile=billing_profile
        # )
        qs = self.get_queryset().filter(
            coupon=coupon,
            billing_profile=billing_profile
        )
        # print("B")
        if qs.count() == 1:
            obj = qs.first()

            # print(obj)
            return obj


class UsedCoupon(models.Model):
    coupon = models.ForeignKey(CouponCode)
    billing_profile = models.ForeignKey(BillingProfile)
    coupon_used = models.BooleanField(default=False)

    objects = UsedCouponManager()



