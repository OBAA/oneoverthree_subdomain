import os
import random
from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse

from oneoverthree.utils import unique_slug_generator


# Create your models here.

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1000000, 98495747363748)
    name, ext = get_filename_ext(filename)
    # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    final_filename = f'{new_filename}{ext}'
    # return "store/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
    return f"tags/{new_filename}/{final_filename}"


class Tag(models.Model):
    title       = models.CharField(max_length=120)
    slug        = models.SlugField(blank=True)
    background_image = models.ImageField(upload_to=upload_image_path, blank=True, null=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    ordering       = models.IntegerField(blank=True)
    is_active      = models.BooleanField(default=True)
    is_banner = models.BooleanField(default=False)

    class Meta:
        ordering = ['is_banner', 'ordering']

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse('store:tags', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return reverse('marketplace:category', kwargs={'slug': self.slug})


def tag_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    if not instance.background_image:
        instance.is_banner = False
    all_tags = Tag.objects.all().filter(is_banner=True)
    if not instance.ordering:
        instance.ordering = 0
    if instance.is_banner and instance.ordering == 0:
        instance.ordering = all_tags.count() + 1


pre_save.connect(tag_pre_save_receiver, sender=Tag)
