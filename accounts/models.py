import os
import random
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import get_template

from oneoverthree.utils import random_string_generator, unique_key_generator, unique_slug_generator

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 1)


# Create your models here.
def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1000000, 98495747363748)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f"accounts/{new_filename}/{final_filename}"


class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None, is_active=False, is_admin=False, is_staff=False):
        if not email:
            raise ValueError("Must be a valid email address")
        if not password:
            raise ValueError("Must have password")

        user_obj = self.model(
            email=self.normalize_email(email),
            full_name=full_name
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    email           = models.EmailField(max_length=120, unique=True)
    mobile_num      = models.TextField(max_length=12, unique=True, blank=True, null=True)
    full_name       = models.CharField(max_length=120, blank=True, null=True)
    image           = models.ImageField(upload_to=upload_image_path, blank=True,
                                        help_text='Field is optional.')
    is_active       = models.BooleanField(default=True)     # user can login
    admin           = models.BooleanField(default=False)    # superuser
    staff           = models.BooleanField(default=False)    # staff but not superuser
    editor          = models.BooleanField(default=False)    # user is editor
    has_store       = models.BooleanField(default=False)    # user is store owner
    timestamp       = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    # confirmed       = models.BooleanField(default=False)
    # confirmed_date  = models.DateTimeField(default=False)

    USERNAME_FIELD = 'email'

    # USERNAME_FIELD and password are required by default.
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def first_name(self):
        full_name = self.full_name
        first_name = str(full_name).split(' ', 1)[0]
        return first_name

    def last_name(self):
        full_name = self.full_name
        last_name = str(full_name).split(' ', 1)[1]
        return last_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_user_details(self):
        return "{full_name}\n{email}\n{mobile_num}".format(
            full_name=self.full_name,
            email=self.email,
            mobile_num=self.mobile_num,
        )

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_editor(self):
        return self.editor

    # @property
    # def is_active(self):
    #     return self.active


class EmailActivationQueryset(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(
            activated=False,
            forced_expired=False
        ).filter(
            timestamp__gt=start_range,
            timestamp__lte=end_range,
        )


class EmailActivationManager(models.Manager):
    #  Model Manager Functions

    def get_queryset(self):
        return EmailActivationQueryset(self.model, using=self.db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def all_confirmable(self):
        return self.get_queryset().all().confirmable()

    def email_exists(self, email):
        return self.get_queryset().filter(
            Q(email=email) | Q(user__email=email)
        ).filter(activated=False)


class EmailActivation(models.Model):
    user            = models.ForeignKey(User)
    email           = models.EmailField()
    key             = models.CharField(max_length=120, blank=True, null=True)
    activated       = models.BooleanField(default=False)
    forced_expired  = models.BooleanField(default=False)
    expires         = models.IntegerField(default=1)  # 24hrs
    timestamp       = models.DateTimeField(auto_now_add=True)
    update          = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    #  Model Instance Functions

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            #  Pre activation user signal
            user = self.user
            user.is_active = True
            user.save()
            #  Pre activation user signal for just activated
            self.activated = True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation_email(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                # base_url = getattr(settings, 'BASE_URL', '127.0.0.1:8000')
                base_url = getattr(settings, 'BASE_URL', 'https://www.1over3.store')
                key_path = reverse("account:email-activate", kwargs={'key': self.key})  # Use reverse
                path = "{base}{path}".format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email': self.email,
                    'first_name': self.user.first_name
                }
                txt_    = get_template("registration/emails/verify.txt").render(context)
                html_   = get_template("registration/emails/verify.html").render(context)
                subject = '1-click Email Verification'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]
                sent_mail = send_mail(
                    subject,
                    txt_,
                    from_email,
                    recipient_list,
                    html_message=html_,
                    fail_silently=False,
                )
                return sent_mail
            return False


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.key and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)


pre_save.connect(pre_save_email_activation, sender=EmailActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation_email()


post_save.connect(post_save_user_create_receiver, sender=User)


class GuestEmail(models.Model):
    email       = models.EmailField(max_length=120)
    mobile_num = models.TextField(max_length=12, blank=True, null=True)
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

