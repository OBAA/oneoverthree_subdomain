import random
import os
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.http import Http404
from django.urls import reverse

# from dashboard.models import Dashboard
from oneoverthree.utils import unique_slug_generator

from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


# Create your models here.
def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    # print(instance)
    # print(filename)
    new_filename = random.randint(1000000, 98495747363748)
    name, ext = get_filename_ext(filename)
    # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    final_filename = f'{new_filename}{ext}'
    # return "store/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
    return f"store/{new_filename}/{final_filename}"


SELLER_CHOICE_FIELD = (
    ('brand', 'Brand'),
    ('outlet', 'Outlet'),
)


class StoreQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_active=True).exclude(title="1over3")

    def active(self):
        return self.filter(is_active=True).exclude(title="1over3")

    def brand(self):
        return self.filter(seller_type='brand')

    def featured(self):
        return self.filter(featured=True)

    def retailer(self):
        return self.filter(seller_type='retailer')


class StoreTreeManager(models.Manager):
    def get_queryset(self):
        return StoreQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def brands(self):
        return self.get_queryset().brand()

    def featured(self):
        return self.get_queryset().featured()

    def retailers(self):
        return self.get_queryset().retailer()

    def get_by_id(self, store_id):
        qs = self.get_queryset().filter(id=store_id)
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_email(self, email):
        qs = self.get_queryset().filter(user__email=email)
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_slug(self, slug):
        # qs = self.get_queryset().filter(slug=slug)
        # if qs.count() == 1:
        #     return qs.first()
        #
        try:
            store = Store.objects.get(slug=slug)
        except Store.DoesNotExist:
            raise Http404("Not Found")
        except Store.MultipleObjectsReturned:
            qs = Store.objects.filter(slug=slug)
            store = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        return store

    def search(self, query):
        return self.get_queryset().search(query)


class Store(MPTTModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, blank=True, unique=True)
    seller_type = models.CharField(max_length=120, choices=SELLER_CHOICE_FIELD)
    description = models.CharField(max_length=120, blank=True)  # , help_text="Slogan?")
    instagram   = models.CharField(max_length=120, blank=True)  # , help_text='IG-@handle')
    twitter   = models.CharField(max_length=120, blank=True)  # , help_text='Twitter-@handle')
    whatsapp  = models.CharField(max_length=120, blank=True)  # , help_text='+234-whatsapp')
    slider_image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    header_image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    ordering = models.IntegerField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    shipping_covered = models.BooleanField(default=False)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            default=None)

    objects = StoreTreeManager()

    class MPTTMeta:
        order_insertion_by = ['ordering']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('marketplace:storefront', kwargs={'slug': self.slug})


def store_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    all_stores = Store.objects.all()
    if not instance.ordering:
        instance.ordering = 0
    if instance.is_active and instance.ordering == 0:
        print("2")
        instance.ordering = all_stores.count() + 1


pre_save.connect(store_pre_save_receiver, sender=Store)

