from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

from accounts.models import GuestEmail

from paystackapi.paystack import Paystack, Customer


# Paystack secret key
paystack = getattr(settings, "PAYSTACK_SECRET_LIVE_KEY")

# Create your models here.

User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated():
            'logged in user; remember payment details'
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_email_id is not None:
            'guest user;auto-reloads payment info'
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
        else:
            pass
        return obj, created


class BillingProfile(models.Model):
    user                    = models.OneToOneField(User, blank=True, null=True)
    email                   = models.EmailField()

    mobile_number           = models.TextField(max_length=12, unique=True, blank=True, null=True)
    first_name              = models.CharField(max_length=120, blank=True, null=True)
    last_name               = models.CharField(max_length=120, blank=True, null=True)

    active                  = models.BooleanField(default=True)
    update                  = models.DateTimeField(auto_now=True)
    timestamp               = models.DateTimeField(auto_now_add=True)
    customer_id_stripe      = models.CharField(max_length=120, null=True, blank=True)
    customer_id_paystack    = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.email

    objects = BillingProfileManager()

    def paystack_customer(self):
        return Customer


def billing_profile_created_receiver_paystack(sender, instance, *args, **kwargs):
    if not instance.customer_id_paystack and instance.email:
        print("API request and send to Paystack")
        customer = instance.paystack_customer().create(
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            phone=instance.mobile_number,

            # to collect above info; pass arguements through 'user_created_receiver'
        )
        customer_api_data = customer['data']
        customer_id = customer_api_data.get('customer_code')
        instance.customer_id_paystack = customer_id
        # print(customer)
        print(customer['message'])
        print(customer_id)


pre_save.connect(billing_profile_created_receiver_paystack, sender=BillingProfile)


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(
            user=instance,
            email=instance.email,
            mobile_number=instance.mobile_number,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )


post_save.connect(user_created_receiver, sender=User)

