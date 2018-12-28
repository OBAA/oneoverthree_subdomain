from django.db import models
from django.core.urlresolvers import reverse
from billing.models import BillingProfile

from django.db.models.signals import pre_save, pre_delete

# Create your models here.

COUNTRY = (
    ('--', 'Country'),
    ('NG', 'Nigeria'),
    # ('GH', 'Ghana'),
    # ('CA', 'Canada'),
    # ('US', 'United States'),
)

STATES = (
    ('Abia', 'Abia'),
    ('Abuja', 'Abuja'),
    ('Adamawa', 'Adamawa'),
    ('Akwa Ibom', 'Akwa Ibom'),
    ('Anambra', 'Anambra'),
    ('Bauchi', 'Bauchi'),
    ('Bayelsa', 'Bayelsa'),
    ('Benue', 'Benue'),
    ('Borno', 'Borno'),
    ('Cross River', 'Cross River'),
    ('Delta', 'Delta'),
    ('Ebonyi', 'Ebonyi'),
    ('Enugu', 'Enugu'),
    ('Edo', 'Edo'),
    ('Ekiti', 'Ekiti'),
    ('Gombe', 'Gombe'),
    ('Imo', 'Imo'),
    ('Jigawa', 'Jigawa'),
    ('Kaduna', 'Kaduna'),
    ('Kano', 'Kano'),
    ('Katsina', 'Katsina'),
    ('Kebbi', 'Kebbi'),
    ('Kogi', 'Kogi'),
    ('Kwara', 'Kwara'),
    ('Lagos', 'Lagos'),
    ('Nasarawa', 'Nasarawa'),
    ('Niger', 'Niger'),
    ('Ogun', 'Ogun'),
    ('Ondo', 'Ondo'),
    ('Osun', 'Osun'),
    ('Oyo', 'Oyo'),
    ('Plateau', 'Plateau'),
    ('Rivers', 'Rivers'),
    ('Sokoto', 'Sokoto'),
    ('Taraba', 'Taraba'),
    ('Yobe', 'Yobe'),
    ('Zamfara', 'Zamfara'),
)


class AddressQueryset(models.query.QuerySet):
    def by_billing_profile(self, billing_profile):
        return self.filter(billing_profile=billing_profile)


class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressQueryset(self.model, using=self.db)

    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.get_queryset().by_billing_profile(billing_profile)

    def get_by_id(self, id):
        print(id)
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def set_default_address(self, request, address_obj):
        qs = self.by_billing_profile(request).filter(default=True)
        if qs.count() == 1:
            obj = qs.first()
            obj.default = False
            obj.save()
            address_obj.default = True

    def force_default_address(self, request, address_obj=None):
        xp = self.by_billing_profile(request)
        qs = xp.filter(default=True)
        if qs.count() == 0:
            if address_obj:
                address_obj.default = True
            else:
                xp.first().default = True

    def new(self, request, billing_profile):
        get = request.POST.get

        address_obj, created = self.get_or_create(
            billing_profile=billing_profile,
            name=get("name"),
            address_line_1=get("address_1"),
            address_line_2=get("address_2"),
            address_type=get("address_type", "shipping"),
            city=get("city"),
            state=get("state"),
            country=get("country"),
            postal_code=get("postal_code"),
            mobile_number=get("mobile_number"),
        )
        return address_obj, created


class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile)
    name            = models.CharField(max_length=120, null=True, blank=True, help_text='Shipping to? Who is it for?')
    address_line_1  = models.CharField(max_length=120)
    address_line_2  = models.CharField(max_length=120, null=True, blank=True)
    city            = models.CharField(max_length=120, null=True)
    state           = models.CharField(max_length=120, choices=STATES)
    country         = models.CharField(max_length=120, choices=COUNTRY, default="NG")  # default="--")
    postal_code     = models.CharField(max_length=120)
    mobile_number   = models.CharField(max_length=120, default=None)
    default         = models.BooleanField(default=False)

    objects = AddressManager()

    def __str__(self):
        return str(self.billing_profile)

    def get_absolute_url(self):
        # return reverse("address:book", kwargs={'order_id': self.order_id})
        return reverse('address:book', kwargs={'pk': self.pk})

    def set_default_address(self, billing_profile):
        qs = Address.objects.get_queryset().by_billing_profile(billing_profile)
        for address in qs:
            if address.default is True:
                address.default = False
                address.save()
        self.default = True
        self.save()

    def get_short_address(self):
        return "{name}\n {line1}, {city}.".format(
                name=self.name,
                line1=self.address_line_1,
                city=self.city
            )

    def get_address(self):
        return "{name}.\n{line1},\n{line2}\n{city}.\n{state}, {postal}.\n{country}.\n{mobile_number}.".format(
            name=self.name,
            line1=self.address_line_1,
            line2=self.address_line_2 or "",
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country,
            mobile_number=self.mobile_number,
        )


def address_pre_save_receiver(sender, instance, *args, **kwargs):
    billing_profile = instance.billing_profile
    qs = Address.objects.get_queryset().by_billing_profile(billing_profile).filter(default=True)
    if qs.count() == 0:
        instance.default = True


pre_save.connect(address_pre_save_receiver, sender=Address)


def address_pre_delete_receiver(sender, instance, *args, **kwargs):
    print("Enter")
    billing_profile = instance.billing_profile
    if instance.default is True:
        qs = Address.objects.get_queryset().by_billing_profile(billing_profile)
        # print(qs)
        # print(qs.count())
        # print(qs[0], qs[1], qs[2])
        if qs.count() > 1:
            next_address = qs[1]
            next_address.set_default_address(billing_profile)


pre_delete.connect(address_pre_delete_receiver, sender=Address)


class ShippingRateQuerySet(models.query.QuerySet):
    def state(self, country, state):
        return self.filter(country=country, state=state)


class ShippingRateManager(models.Manager):
    def get_queryset(self):
        return ShippingRateQuerySet(self.model, using=self._db)

    def shipping_per_kg(self, shipping_address_id):
        address_obj = Address.objects.get_by_id(id=shipping_address_id)
        country = address_obj.country
        state = address_obj.state  # .lower()
        city = address_obj.city.lower()

        # shipping_rate = {'NG': {'lagos': 1000, 'abuja': 2500}, 'GH': {'lagos': 1000, 'abuja': 2500}}
        # shipping_per_kg = shipping_rate[country][state]

        state_ = self.get_queryset().state(country, state)
        if state_.count() > 0:
            city_ = state_.filter(city=city, city__icontains=city)
            # city__ = state_.filter(city__icontains=city)
            default = state_.filter(city='default')
            if city_.count() > 0:
                location = city_.first()
                shipping_per_kg = location.per_kg
            # elif city__.count() > 0:
            #     location = city__.first()
            #     shipping_per_kg = location.per_kg
            else:
                location = default.first()
                shipping_per_kg = location.per_kg
        else:
            shipping_per_kg = 1500

        return shipping_per_kg


class ShippingRate(models.Model):
    country         = models.CharField(max_length=120, choices=COUNTRY, default="NG")  # default="--")
    state           = models.CharField(max_length=120, choices=STATES)
    city            = models.CharField(max_length=120, default='default')
    per_kg          = models.IntegerField(default=1000)

    objects = ShippingRateManager()

    def __str__(self):
        return self.state

    class Meta:
        ordering = ['country', 'state', 'city']


class ProductWeightManager(models.Manager):
    def xp(self):
        return


class ProductWeight(models.Model):
    product_type    = models.CharField(max_length=120)
    weight          = models.CharField(max_length=120, default='0.7')

    objects = ProductWeightManager()

    def __str__(self):
        return self.product_type

    class Meta:
        ordering = ['product_type']



