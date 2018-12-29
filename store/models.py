import random
import os
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from addresses.models import ProductWeight
from marketplace.models import Store
from oneoverthree.utils import unique_slug_generator, unique_sku_generator
from tags.models import Tag

from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


# Create your models here.
def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1000000, 98495747363748)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f"store/{new_filename}/{final_filename}"


class Category(MPTTModel):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=120, blank=True, unique=True)
    background_image = models.ImageField(upload_to=upload_image_path, blank=True, null=True)
    description = models.TextField(blank=True)
    ordering = models.IntegerField(blank=True)
    is_active = models.BooleanField(default=True)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Categories'
        # unique_together = ('parent', 'slug')

    class MPTTMeta:
        order_insertion_by = ['ordering']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('store:categories', kwargs={'slug': self.slug})


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    all_categories = Category.objects.all()
    if not instance.ordering:
        instance.ordering = all_categories.count() + 1


pre_save.connect(category_pre_save_receiver, sender=Category)


# class BrandsManager(models.Manager):
#     def get_queryset(self):
#         return ProductQuerySet(self.model, using=self._db)


# class Brand(MPTTModel):
#     title = models.CharField(max_length=120,)
#     slug = models.SlugField(max_length=120, blank=True, unique=True)
#     description = models.CharField(max_length=120, blank=True)
#     background_image_a = models.ImageField(upload_to=upload_image_path, null=True, blank=False)
#     background_image_b = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
#     order = models.IntegerField(blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     featured = models.BooleanField(default=False)
#
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', default=None)
#
#     class MPTTMeta:
#         order_insertion_by = ['order']
#
#     def __str__(self):
#         return self.title
#
#     def get_absolute_url(self):
#         return reverse('store:brands', kwargs={'slug': self.slug})
#
#
# def brand_pre_save_receiver(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         instance.slug = unique_slug_generator(instance)
#
#
# pre_save.connect(brand_pre_save_receiver, sender=Brand)


PRODUCT_WEIGHT = (
    # (KG, DISPALY),
    ('0.5', 'Accessory'),
    ('0.7', 'Clothing'),
    ('1', 'Shoe'),
    ('1', 'Bag'),
)

DISCOUNT_RATES = [(i*5, str(i*5)) for i in range(0, 12)]


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def featured(self):
        return self.filter(featured=True, is_active=True)

    def search(self, query):
        lookups = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__title__icontains=query)
        )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def check_new_in(self, store):
        qs = self.all().filter(store=store)
        if qs.count() > 0:
            for product in qs:
                if product.new_in:
                    timestamp = product.timestamp
                    now = timezone.now()
                    # valid_days = timedelta(days=7)
                    life_span = now - timestamp
                    if life_span.days > 10:
                        print("Scream")
                        product.new_in = False
                        product.save()

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
    title               = models.CharField(max_length=120, )
    slug                = models.SlugField(max_length=120, blank=True, unique=True)
    sku                 = models.CharField(max_length=120, blank=True, unique=True)
    product_type        = models.ForeignKey(ProductWeight, default=0.7,
                                  help_text='For calculating shipping cost', null=True)
    store               = TreeForeignKey(Store, related_name='products', default=None, null=True)
    category            = TreeForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand               = models.CharField(max_length=120, blank=True)
    description         = models.TextField()
    extra_description   = models.TextField(blank=True, help_text="Additional Information, Care tips?")
    tags                = models.ManyToManyField(Tag, related_name='products')
    base_price          = models.DecimalField(decimal_places=2, max_digits=10, default=00.00)
    price               = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    image_a             = models.ImageField(upload_to=upload_image_path, null=False,
                                            help_text="First image displayed to customers")
    image_b             = models.ImageField(upload_to=upload_image_path, null=False,
                                            help_text="Second image displayed to customers")
    image_c             = models.ImageField(upload_to=upload_image_path, null=False,
                                            help_text="Third image displayed to customers")
    has_variants        = models.BooleanField(default=False)
    featured            = models.BooleanField(default=False)
    new_in              = models.BooleanField(default=False)
    on_sale             = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)
    discount            = models.PositiveIntegerField(blank=True, null=True, choices=DISCOUNT_RATES,
                                                      help_text="Percentage '%' discount")
    stock               = models.PositiveIntegerField(blank=True, null=True,
                                                      help_text="Overwritten if variants")
    timestamp           = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['pk']

    def get_absolute_url(self):
        return reverse("store:detail", kwargs={'slug1': self.store, 'slug2': self.slug})

    @property
    def name(self):
        return self.title


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

    if not instance.sku:
        instance.sku = unique_sku_generator(instance)

    if not instance.price:
        instance.price = instance.base_price

    if not instance.on_sale:
        instance.price = instance.base_price

    if instance.discount:
        base_price = instance.base_price
        discount = instance.discount
        discounted_amount = (discount * base_price) / 100
        # discounted_amount = discount_rate * base_price
        new_price = base_price - discounted_amount
        instance.price = new_price
        instance.on_sale = True


pre_save.connect(product_pre_save_receiver, sender=Product)


class ProductImage(models.Model):
    file = models.ImageField(upload_to=upload_image_path, null=True, blank=True,
                              help_text="First image displayed to customers")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product)

    class Meta:
        ordering = ['pk']


class ProductReview(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField(max_length=600, help_text="Enter product review here.")
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        """
        String for representing the Model object.
        """
        len_title = 75
        if len(self.content) > len_title:
            title_string = self.content[:len_title] + '...'
        else:
            title_string = self.content
        return title_string


QUANTITY_CHOICES = [(i, str(i)) for i in range(0, 26)]

SIZE_CHOICES = (
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('38', '38'),
    ('39', '39'),
    ('40', '40'),
    ('41', '41'),
    ('42', '42'),
    ('43', '43'),
    ('44', '44'),
    ('45', '45'),
    ('W-30', 'W-30'),
    ('W-32', 'W-32'),
    ('W-34', 'W-34'),
    ('W-36', 'W-36'),
)


class VariationManager(models.Manager):
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def get_size(self, product_obj, size_id):
        if size_id:
            size = Variation.objects.get_by_id(id=size_id)
            stock = size.quantity
        else:
            size = '---'
            stock = product_obj.stock

        return size, stock


class Variation(models.Model):
    size        = models.CharField(max_length=120, choices=SIZE_CHOICES,
                                   blank=True, help_text='select a size.')
    product     = models.ForeignKey(Product, null=True)
    quantity       = models.PositiveIntegerField(null=True, choices=QUANTITY_CHOICES)
    is_active   = models.BooleanField(default=True)

    objects = VariationManager()

    def __str__(self):
        return str(self.size)

    class Meta:
        ordering = ['product', '-size']
        unique_together = ('product', 'size')


def product_stock_pre_save_receiver(sender, instance, *args, **kwargs):
    product = instance.product
    stock = 0
    qs = Variation.objects.all().filter(product=product)
    for variation in qs:
        stock = stock + variation.quantity

    product = Product.objects.get_by_id(id=product.id)
    product.has_variants = True
    product.stock = stock
    product.save()


pre_save.connect(product_stock_pre_save_receiver, sender=Variation)
