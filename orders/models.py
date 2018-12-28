import math
import json
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save

from store.models import Product
from cart.cart import Cart
from addresses.models import Address, ShippingRate
from billing.models import BillingProfile
from marketplace.models import Store
from oneoverthree.utils import unique_order_id_generator


# Create your models here.

ORDER_STATUS_CHOICES = (
  # ('database', 'Display') values,
    ('created', 'created'),
    ('processing', 'processing'),
    ('shipped', 'shipped'),
    ('refunded', 'refunded'),
    ('completed', 'completed'),
)

ORDER_ITEM_STATUS_CHOICES = (
    ('pending', 'pending'),
    ('processing', 'processing'),
    ('shipped', 'shipped'),
    ('refunded', 'refunded'),
    ('completed', 'completed'),
)


class OrderManagerQuerySet(models.query.QuerySet):
    def by_billing_profile(self, billing_profile):
        return self.filter(billing_profile=billing_profile)

    def paid(self):
        return self.exclude(status="created")


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def filter_by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.get_queryset().by_billing_profile(billing_profile)

    def get_by_billing_profile(self, request):
        qs = self.filter_by_billing_profile(request).filter(is_active=True)
        if qs.count() == 1:
            obj = qs.first()
            return obj

    def new_or_get(self, request, billing_profile):
        obj, created = self.get_or_create(
            billing_profile=billing_profile,
            is_active=True,
        )
        return obj, created

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # Product.objects == self.get_querset
        if qs.count() == 1:
            return qs.first()
        return None

    def shipping_total(self, request, shipping_address_id, obj):
        cart = Cart(request)
        shipping_per_kg = ShippingRate.objects.shipping_per_kg(shipping_address_id)
        weight = cart.get_weight()
        shipping_total = 1000
        if float(weight) < 3:
            shipping_total = 1 * int(shipping_per_kg)
        if float(weight) >= 3:
            if weight < 6:
                shipping_total = int(shipping_per_kg) + 500
        obj.shipping_total = shipping_total
        print(shipping_total)
        obj.save()

    # def shipping_per_kg(self, shipping_address_id):
    #     address_obj = Address.objects.get_by_id(id=shipping_address_id)
    #     country = address_obj.country
    #     state = address_obj.state.lower()
    #     print(state)
    #     shipping_rate = {'NG': {'lagos': 1000, 'abuja': 2500}, 'GH': {'lagos': 1000, 'abuja': 2500}}
    #     shipping_per_kg = shipping_rate[country][state]
    #     print(shipping_per_kg)
    #     return shipping_per_kg

    def cart_total(self, request, obj):
        total = request.POST.get("cart_total")
        cart_total = Decimal(total)
        obj.total = cart_total
        obj.save()
        return cart_total

    def order_total(self, request, obj):
        # total = request.POST.get("cart_total")
        cart_total = obj.total
        shipping_total = obj.shipping_total
        new_total = math.fsum([cart_total, shipping_total])
        formatted_total = format(new_total, ".2f")
        obj.total = formatted_total
        obj.save()

    def get_order_item(self, order_obj):  # Not in use yet
        json_decoder = json.decoder.JSONDecoder()
        cart_item = json_decoder.decode(order_obj.cart_json)
        return cart_item


class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True) # Get from checkout view
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True)  # Get from checkout view
    order_id = models.CharField(max_length=120, blank=True)  # Get from signal
    status = models.CharField(max_length=500, default='created', choices=ORDER_STATUS_CHOICES)  # Default
    shipping_total = models.DecimalField(default=1000, max_digits=12, decimal_places=2)  # Figure it out
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)  # Calculated in checkout view
    coupon = models.CharField(max_length=25, blank=True, null=True)
    coupon_applied = models.BooleanField(default=False)
    discount_applied = models.IntegerField(blank=True, null=True)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)
    pdf_sent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Default
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def get_absolute_url(self):
        return reverse("account:order-details", kwargs={'order_id': self.order_id})

    def __str__(self):
        return '{}'.format(self.order_id)

    def check_order_status(self):
        order_items = OrderItem.objects.get_queryset().get_items(self)
        for item in order_items:
            if item.status != 'completed':
                return
        else:
            self.status = 'completed'
        return


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)


pre_save.connect(pre_save_create_order_id, sender=Order)


class OrderItemQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def get_items(self, order_obj):
        return self.filter(is_active=True, order=order_obj)


class OrderItemManager(models.Manager):
    def get_queryset(self):
        return OrderItemQuerySet(self.model, using=self._db)

    def get_by_order_id(self, order_id):
        qs = self.get_queryset().all()
        order_items = [item for item in qs if item.order.order_id == order_id]
        print(order_items)

        return order_items

    def get_items(self, order_obj):
        return self.get_queryset().get_items(order_obj)

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # Product.objects == self.get_querset
        if qs.count() == 1:
            return qs.first()
        return None


class OrderItem(models.Model):
    order = models.ForeignKey(Order, default=None)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, null=True)
    size = models.CharField(max_length=120, blank=True)  #
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField()
    status = models.CharField(max_length=120, choices=ORDER_ITEM_STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)

    objects = OrderItemManager()

    def __str__(self):
        return self.product.title

    def get_total(self):
        self.product * self.price


def pre_save_create_order_item(sender, instance, *args, **kwargs):
    if instance.total_price == 0:
        total_price = instance.price * int(instance.quantity)
        instance.total_price = total_price


pre_save.connect(pre_save_create_order_item, sender=OrderItem)

