from django.http import JsonResponse

from .cart import Cart


def cart_detail_api_view(request):
    cart = Cart(request)  # //
    cart_total = cart.get_total()
    cart_weight = cart.get_weight()
    action_update = "/cart/update/"
    action_remove = "{% url 'cart:remove' %}"

    products = cart.get_items()

    json_data = {
        "cartTotal": cart_total,
        "cartWeight": cart_weight,
        "product": products,
        "action_update": action_update,
        "action_remove": action_remove
    }
    return JsonResponse(json_data)
