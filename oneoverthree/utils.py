import random
import string

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.text import slugify

from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance):
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key


def unique_order_id_generator(instance):
    order_new_id = "1O3-" + random_string_generator(size=6)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=order_new_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return order_new_id

# Original

# def unique_slug_generator(instance, new_slug=None):
#     """
#     This is for a Django project and it assumes your instance
#     has a model with a slug field and a title character (char) field.
#     """
#     if new_slug is not None:
#         slug = new_slug
#     else:
#         slug = slugify(instance.title)
#
#     Klass = instance.__class__
#     qs_exists = Klass.objects.filter(slug=slug).exists()
#     if qs_exists:
#         new_slug = "{slug}-{randstr}".format(
#                     slug=slug,
#                     randstr=random_string_generator(size=4)
#                 )
#         return unique_slug_generator(instance, new_slug=new_slug)
#     return slug


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    slug = slugify(instance.title)
    new_slug = slug
    Klass = instance.__class__
    numb = 1

    while Klass.objects.filter(slug=new_slug).exists():
        new_slug = "{slug}-{num}".format(
            slug=slug,
            num=numb
        )
        numb += 1
    return new_slug


# def _unique_slug(self):
#     """
#     return unique slug if origin slug is exist.
#     eg: `foo-bar` => `foo-bar-1`
#     """
#     origin_slug = slugify(self.title)
#     unique_slug = origin_slug
#     numb = 1
#     while Question.objects.filter(slug=unique_slug).exists():
#         unique_slug = '%s-%d' % (origin_slug, numb)
#         numb += 1
#     return unique_slug

