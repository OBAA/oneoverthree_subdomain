from django.http import JsonResponse

from .cart import Cart
from orders.models import Order, OrderItem


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


def checkout_complete_api_view(request):
    order_id = request.session.get('order_id', None)
    if order_id:
        del request.session['order_id']
    order_obj = Order.objects.get_by_order_id(order_id)
    cart_total = order_obj.total - order_obj.shipping_total
    products = []
    order_items = OrderItem.objects.get_items(order_obj)
    for item in order_items:
        products.append({
            'sku': item['sku'],
            'quantity': item['quantity'],
            'price': item['price'],
        })

    json_data = {
        "cartTotal": cart_total,
        "product": products
    }
    return JsonResponse(json_data)

