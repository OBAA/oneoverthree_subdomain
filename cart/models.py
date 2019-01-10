from django.conf import settings
from datetime import timedelta
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.models import EmailActivation
from billing.models import BillingProfile
from orders.models import Order

User = settings.AUTH_USER_MODEL

#
DISCOUNT_RATES = [(i*5, str(i*5)) for i in range(1, 16)]


class CouponCodeQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_valid=True)


class CouponCodeManager(models.Manager):
    def get_queryset(self):
        return CouponCodeQuerySet(self.model, using=self._db)

    def create_coupon(self, code, description, percentage=None, amount=None, first_order_coupon=False, is_one_use_only=False, is_valid_till=None):
        coupon = self.model(
            code=code,
            description=description,
        )
        if first_order_coupon:
            coupon.first_order_coupon = True
        if is_one_use_only:
            coupon.is_one_use_only = True
        if is_valid_till > 0:
            coupon.is_valid_till = is_valid_till
            coupon.is_valid = True
        if percentage:
            coupon.percentage = percentage
        if amount:
            coupon.percentage = None
            coupon.amount = amount
        coupon.save()
        return coupon

    def get_coupon(self, code):
        now = timezone.now()
        qs = self.get_queryset().all().filter(code=code)
        coupon = None
        if qs.count() == 1:
            coupon = qs.first()
            valid_till = coupon.timestamp + timedelta(days=coupon.is_valid_till)
            if now > valid_till:
                coupon.is_valid = False
        return coupon

    def apply_coupon(self, request, billing_profile, coupon_code, order_obj):
        coupon = self.get_coupon(code=coupon_code)
        if order_obj.coupon:
            messages.error(request, "Sorry, only one coupon code per order.")
            return redirect('cart:checkout')

        if coupon is not None and coupon.is_valid is True:
            if coupon.first_order_coupon is True:
                qs = Order.objects.filter_by_billing_profile(request)
                if qs.count() > 0:
                    messages.error(request, "Ooops, Coupon Only valid on your first order.")
                    return redirect('cart:checkout')
                pass
            if coupon.is_one_use_only and coupon.usage > 0:
                messages.error(request, "Ooops, This coupon has been used and is no longer valid.")
                return redirect('cart:checkout')

            else:  # Check if coupon has been used by current user
                used_coupon_obj, created = UsedCoupon.objects.new_or_get(coupon, billing_profile)

                if created:  # Use Coupon
                    cart_total = order_obj.total

                    if coupon.amount is not None:  # If Cash Voucher
                        discount = coupon.amount
                        if discount >= cart_total:
                            new_total = 0
                        else:
                            new_total = cart_total - discount

                        # Pass discount information to USER session
                        if request.session.get("discount_type", None):
                            del request.session['discount_type']
                        request.session['discount_type'] = 1

                    else:  # If % Percentage OFF
                        discount = coupon.percentage
                        discount_amount = (cart_total * discount) / 100
                        new_total = cart_total - discount_amount

                        # Pass discount information to USER session
                        if request.session.get("discount_type", None):
                            del request.session['discount_type']
                        request.session['discount_type'] = 2

                    if not order_obj.coupon_applied:
                        order_obj.total = new_total
                        order_obj.coupon = coupon_code
                        order_obj.discount_applied = discount
                        order_obj.save()
                        coupon.usage += 1
                        coupon.save()
                        messages.success(request, "Coupon code applied. Proceed to checkout.")
                        return redirect('cart:checkout')

                elif used_coupon_obj.coupon_used:
                    messages.error(request, "This coupon has already been used by you.")

                else:
                    link = reverse('contact')
                    support = """<a href="{support_link}">support</a>""".format(support_link=link)
                    msg = "Unable to process coupon, please contact " + support
                    messages.error(request, msg, extra_tags='safe')

        elif coupon is not None and coupon.is_valid is False:
            messages.error(request, "Sorry. This coupon is no longer valid.")

        else:
            messages.error(request, "Invalid. Check your code and try again.")

    def remove_coupon(self, billing_profile, coupon, order_obj):
        coupon_obj = self.get_coupon(code=coupon)
        used_coupon_obj = UsedCoupon.objects.get_valid_coupon(coupon, billing_profile)
        if coupon_obj and used_coupon_obj.coupon_used is False:
            used_coupon_obj.delete()
            coupon_obj.usage -= 1
            coupon_obj.save()
            order_obj.coupon_applied = False
            order_obj.coupon = None
            order_obj.discount_applied = None
            order_obj.save()


class CouponCode(models.Model):
    code = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=120)
    percentage = models.PositiveIntegerField(choices=DISCOUNT_RATES, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    usage = models.IntegerField(default=0)
    first_order_coupon = models.BooleanField(default=False)
    is_one_use_only = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    is_valid_till = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CouponCodeManager()

    def __str__(self):
        return self.description


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if instance.activated:
        first_name = instance.user.first_name
        proposed_code = "{base}{f_name}".format(base="1O3", f_name=first_name.upper())

        # Create coupon code
        numb = 1
        new_code = proposed_code
        while CouponCode.objects.filter(code=proposed_code).exists():
            new_code = "{p_code}{num}".format(
                p_code=proposed_code,
                num=numb
            )
            numb += 1

        coupon_description = "New User Signup 20% Discount"
        coupon = CouponCode.objects.create_coupon(
            code=new_code,
            description=coupon_description,
            percentage=20,
            first_order_coupon=True,
            is_valid_till=30
        )

        instance.coupon = coupon.code


pre_save.connect(pre_save_email_activation, sender=EmailActivation)


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
        coupon = CouponCode.objects.get_coupon(coupon)
        qs = self.get_queryset().filter(
            coupon=coupon,
            billing_profile=billing_profile
        )
        if qs.count() == 1:
            obj = qs.first()
            return obj


class UsedCoupon(models.Model):
    coupon = models.ForeignKey(CouponCode)
    billing_profile = models.ForeignKey(BillingProfile)
    # user = models.ForeignKey(User)
    coupon_used = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = UsedCouponManager()



