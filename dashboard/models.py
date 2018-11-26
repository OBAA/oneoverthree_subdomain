from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_save

from marketplace.models import Store
from orders.models import OrderItem
from store.models import Product


# Create your models here.
User = get_user_model()

STAFF_CHOICE_FIELD = (
    ('brand', 'Brand'),
    ('retailer', 'Retailer'),
    ('creative', 'Creative'),
)


class DashboardQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_active=True)


class DashboardManager(models.Manager):
    def get_queryset(self):
        return DashboardQuerySet(self.model, using=self._db)

    def get_dashboard(self, store):
        qs = self.get_queryset().all().filter(store=store)
        if qs.count() == 1:
            dashboard = qs.first()
            # print(dashboard)
            return dashboard

    def pending_orders(self, store):
        order_items = OrderItem.objects.all().filter(store=store, is_active=True)
        pending_orders = []
        for item in order_items:
            if item.status == 'pending':
                pending_orders.append(item)

        dashboard = self.get_dashboard(store)
        dashboard.orders = len(pending_orders)
        dashboard.save()
        return pending_orders

    def processing_orders(self, store):
        dashboard = self.get_dashboard(store)
        order_items = OrderItem.objects.all().filter(store=store, is_active=True)
        processing_orders = []
        for item in order_items:
            if item.status == 'processing':
                processing_orders.append(item)
        return processing_orders

    def completed_orders(self, store):
        dashboard = self.get_dashboard(store)
        order_items = OrderItem.objects.all().filter(store=store)
        completed_orders = []
        for item in order_items:
            if item.status in ('shipped', 'completed'):
                completed_orders.append(item)
        return completed_orders

    def all_time_sales(self, store):
        order_items = OrderItem.objects.all().filter(
            store=store,
            is_active=True,
            status='completed'
        )
        dashboard = self.get_dashboard(store)
        dashboard.sales = order_items.count()
        revenue = [item.price for item in order_items]
        total_revenue = sum(revenue)
        dashboard.total_revenue = total_revenue
        dashboard.save()

    # def get_dashboard(self, user):
    #     store = user.store
    #     print(store)
    #     if store:
    #         qs = self.get_queryset().all().filter(store=store)
    #         if qs.count() == 1:
    #             dashboard = qs.first()
    #             return dashboard


class Dashboard(models.Model):
    store = models.ForeignKey(Store, related_name='dashboard', on_delete=models.SET_NULL, null=True)
    total_revenue = models.DecimalField(decimal_places=2, max_digits=10, default=00.00)
    sales = models.IntegerField(default=0)
    orders = models.IntegerField(default=0)
    tariff = models.DecimalField(decimal_places=2, max_digits=10, default=0.10)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=00.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = DashboardManager()

    def __str__(self):
        return str(self.store)


def store_post_save_receiver(sender, instance, *args, **kwargs):
    Dashboard.objects.get_or_create(
        store=instance
    )


post_save.connect(store_post_save_receiver, sender=Store)



