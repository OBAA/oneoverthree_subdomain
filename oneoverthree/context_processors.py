from store.models import Category
from cart.cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def category(request):
    return {'category_list': Category.objects.all()}
