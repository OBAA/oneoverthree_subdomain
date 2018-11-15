import random
import os

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.urls import reverse

from filter.models import Size
from oneoverthree.utils import unique_slug_generator
from tags.models import Tag

from mptt.models import MPTTModel, TreeForeignKey


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






class Collection(MPTTModel):
    title = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title


class CategoriesManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)


class Category(models.Model):
    title = models.CharField(max_length=120,)
    slug = models.SlugField(max_length=120, blank=True, unique=True)
    background_image = models.ImageField(upload_to=upload_image_path, blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(blank=True)
    is_active = models.BooleanField(default=True)

    subcategories = models.ManyToManyField('self', symmetrical=False, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['order']

    def get_absolute_url(self):
        return reverse('store:categories', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(category_pre_save_receiver, sender=Category)


class BrandsManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)


class Brand(models.Model):
    title = models.CharField(max_length=120,)
    slug = models.SlugField(max_length=120, blank=True, unique=True)
    slogan = models.CharField(max_length=120, blank=True)
    background_image_a = models.ImageField(upload_to=upload_image_path, null=True, blank=False)
    background_image_b = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    order = models.IntegerField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = BrandsManager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('store:brands', kwargs={'slug': self.slug})


def brand_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(brand_pre_save_receiver, sender=Brand)


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tag__title__icontains=query)
        )
        return self.filter(lookups).distinct()


class StoreManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # Product.objects == self.get_querset
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().search(query)


class Product(models.Model):
    title           = models.CharField(max_length=120, )
    slug            = models.SlugField(blank=True, unique=True)
    category = models.ForeignKey(Category, related_name='products', default=None, null=True,)
    brand = models.ForeignKey(Brand, related_name='products', default=None, null=True)
    description     = models.TextField()
    tags            = models.ManyToManyField(Tag)
    price           = models.DecimalField(decimal_places=2, max_digits=10, default=00.00)
    image_a         = models.ImageField(upload_to=upload_image_path, null=True, blank=False)
    image_b         = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    image_c         = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    size1           = models.ForeignKey(Size, related_name='size1', null=True, blank=False)
    has_variants    = models.BooleanField(default=False)
    size2           = models.ForeignKey(Size, related_name='size2', null=True, blank=True)
    size3           = models.ForeignKey(Size, related_name='size3', null=True, blank=True)
    featured        = models.BooleanField(default=False)
    new_in          = models.BooleanField(default=False)
    on_sale         = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    stock           = models.PositiveIntegerField(blank=True, null=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = StoreManager()

    def get_absolute_url(self):
        return reverse("store:detail", kwargs={'slug1': self.brand, 'slug2': self.slug})

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


def size_variation_pre_save_receiver(sender, instance, *args, **kwargs):
    s1 = instance.size1
    s2 = instance.size2
    s3 = instance.size3
    stock = s1.stock
    if instance.has_variants and s2 is not None:
        stock = s1.stock + s2.stock
        if s3 is not None:
            stock = s1.stock + s2.stock + s3.stock
    instance.stock = stock


pre_save.connect(size_variation_pre_save_receiver, sender=Product)


# class Brand(models.Model):
#     name = models.CharField(max_length=120, unique=True)
#     slug = models.SlugField(max_length=120, blank=True, unique=True)
#     store = models.ManyToManyField(Product, blank=True, related_name='collections')
#     background_image = models.ImageField(upload_to=upload_image_path, null=True, blank=False)
#
#     # objects =
#
#     class Meta:
#         ordering = ['pk']
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('product:collection', kwargs={'slug': self.slug})
