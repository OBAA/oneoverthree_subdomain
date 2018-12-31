from django.http import JsonResponse

from .cart import Cart


def cart_detail_api_view(request):
    cart = Cart(request)  # //
    cart_total = cart.get_total()
    cart_weight = cart.get_weight()
    action_update = "/cart/update/"
    action_remove = "{% url 'cart:remove' %}"

    products = []
    for item in cart.get_items():
        products.append({
            'id': item['id'],
            'sku': item['sku'],
            'url': item['url'],
            'title': item['title'],
            'brand': item['brand'],
            'image': item['image'],
            'size': item['size'],
            'quantity': item['quantity'],
            'price': item['price'],
            'slot': item['slot'],
            'attribute': str(item['attribute']),
        })
    print(products)

    json_data = {
        "cartTotal": cart_total,
        "cartWeight": cart_weight,
        "product": products,
        "action_update": action_update,
        "action_remove": action_remove
    }
    return JsonResponse(json_data)
