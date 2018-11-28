import datetime
from decimal import Decimal
from io import BytesIO
from django.core.files import File
from django.http import Http404
from django.utils.http import is_safe_url
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.views.generic import FormView, View, RedirectView

from django.template.loader import get_template

from accounts.forms import LoginForm, GuestForm
from addresses.forms import CheckoutAddressForm
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order, OrderItem  # , GenerateOrderPdf
from oneoverthree.utils import render_to_pdf
from store.models import Product, Variation
from .cart import Cart
from .forms import CartUpdateForm



# Paystack
paystack = getattr(settings, "PAYSTACK_SECRET_KEY")
paystack_pk = getattr(settings, "PAYSTACK_PUB_KEY")


# Create your views here.
def cart_detail_api_view(request):
    cart = Cart(request)  # //
    cart_total = cart.get_total()
    # store = cart.cart.values()
    action_update = "/cart/update/"
    action_remove = "{% url 'cart:remove' %}"

    products = []
    for item in cart.get_items():
        products.append({
            'id': item['id'],
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
        "product": products,
        "action_update": action_update,
        "action_remove": action_remove
    }
    return JsonResponse(json_data)


def add_to_cart(request):
    product_id = request.POST.get('product_id', None)
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user; Product is gone")
            return redirect("cart:home")
        cart_obj = Cart(request)

        # product_quantity = 1
        # product_size_id = None
        # size, stock = Variation.objects.get_size(product_obj, product_size_id)
        # print(size, stock)
        #
        # # Take inventory
        # msg = "Only " + str(stock) + " items in stock."
        # check_stock = int(stock) - int(product_quantity)
        # if check_stock < 0:
        #     messages.error(request, msg)
        #     return reverse("store:detail", kwargs={'slug': product_obj.slug})
        #
        # cart_obj.add(product=product_obj, size=size, quantity=product_quantity)
        #

        cart_obj.add(product=product_obj, quantity=1)

        added = True
        removed = False
        cart_count = cart_obj.__len__()

        if request.is_ajax():
            print("Ajax request")
            json_data = {
                "added": added,
                "removed": removed,
                "cartCount": cart_count
            }
            return JsonResponse(json_data)
    return redirect("cart:home")


class UpdateCartView(RedirectView):
    def post(self, request, *args, **kwargs):
        request = self.request
        cart_obj = Cart(request)
        data = request.POST
        product_id = data.get('product_id')
        product_size_id = data.get('product', None)
        product_quantity = data.get('product_quantity')
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user; Product is gone")
            return redirect("cart:home")

        size, stock = Variation.objects.get_size(product_obj, product_size_id)
        print(size, stock)

        # Take inventory
        msg = "Only " + str(stock) + " items in stock."
        check_stock = int(stock) - int(product_quantity)
        if check_stock < 0:
            messages.error(request, msg)
            return self.get_success_url(product_obj)

        cart_obj.add(product=product_obj, size=size, quantity=product_quantity, update_quantity=True)
        return self.get_success_url(product_obj)

    def get_success_url(self, product_obj):
        request = self.request
        cart_obj = Cart(request)
        # product_obj = self.get_product()
        cart_count = cart_obj.__len__()
        if request.is_ajax():
            json_data = {
                "cartCount": cart_count,
            }
            return JsonResponse(json_data)
        return reverse("store:detail", kwargs={'slug': product_obj.slug})


def cart_update_view(request):
    product_id = request.POST.get('id', None)
    product_size = request.POST.get('size', None)
    product_quantity = request.POST.get('quantity', None)

    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user; Product is gone")
            return redirect("cart:home")
        cart_obj = Cart(request)

        cart_obj.add(
            product=product_obj, size=product_size,
            quantity=product_quantity, update_quantity=True
        )

        cart_count = cart_obj.__len__()
        if request.is_ajax():
            print("Ajax request")
            json_data = {
                "cartCount": cart_count
            }
            return JsonResponse(json_data)
        return redirect("cart:home")


def cart_remove(request):
    print(request.POST)
    product_id = request.POST.get('product_id', None)
    product_slot = request.POST.get('product_slot', None)
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user; Product is gone")
            return redirect("cart:home")
        cart_obj = Cart(request)
        cart_obj.remove(product=product_obj, slot=product_slot)
        added = False
        removed = True
        cart_count = cart_obj.__len__()
        if request.is_ajax():
            print("Ajax request")
            json_data = {
                "added": added,
                "removed": removed,
                "cartCount": cart_count
            }
            return JsonResponse(json_data)
    return redirect("cart:home")


def cart_home(request):
    return render(request, "cart/cart-home.html", {})


def checkout_home(request):
    cart_obj = Cart(request)
    if cart_obj.__len__() == 0:
        return redirect("cart:home")

    address_book = None
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    order_obj, order_obj_created = Order.objects.new_or_get(request, billing_profile)

    if billing_profile is not None:
        address_book = Address.objects.all().filter(billing_profile=billing_profile)

    context = {
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_book": address_book,
        "form": CheckoutAddressForm,
    }
    return render(request, "cart/checkout.html", context)


def checkout_finalize(request):
    cart_obj = Cart(request)
    if cart_obj.__len__() == 0:
        return redirect("cart:home")

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    order_obj, order_obj_created = Order.objects.new_or_get(request, billing_profile)
    address_book = Address.objects.all().filter(billing_profile=billing_profile)

    shipping_address_id = request.session.get("shipping_address_id", None)

    if shipping_address_id:
        qs = address_book.filter(id=shipping_address_id)
        if qs.count() == 1:
            shipping_address = qs.first()

            if billing_profile is not None and shipping_address:
                order_obj.shipping_address = shipping_address
                order_obj.save()

        raw_order_total = int(order_obj.total)
        formatted_order_total = str(raw_order_total) + str('00')
        order_total = int(formatted_order_total)

        context = {
            "object": order_obj,
            "paystack_public_key": paystack_pk,
            "order_total": order_total,
            "billing_profile": billing_profile
        }
        return render(request, "cart/checkout-finalize.html", context)


def checkout_success(request):
    cart = Cart(request)
    obj = Order.objects.get_by_billing_profile(request)
    if obj is None:
        return redirect("store:home")

    for item in cart.get_items():
        OrderItem.objects.create(
            order=obj,
            product=item['product'],
            store=item['store'],
            size=item['size'],
            price=item['price'],
            quantity=item['quantity'],
        )

    if request.user.is_authenticated:
        customer = request.user.full_name
    else:
        customer = obj.shipping_address.name

    context = {
        'cart': cart.get_items(),
        'date': datetime.date.today(),
        'order_total': obj.total,
        'customer_name': customer,
        'invoice_id': obj.order_id,
    }
    obj.is_active = False
    obj.status = 'processing'
    if not obj.pdf:
        pdf = render_to_pdf('invoice.html', context)
        # pdf = None
        if pdf:
            filename = "Invoice_%s.pdf" % obj.order_id
            obj.pdf.save(filename, File(BytesIO(pdf.content)))
    else:
        obj.save()
    cart.clear()
    return render(request, "cart/checkout-success.html", {'object': obj})


def show_order_invoice(request, *args, **kwargs):
    order_id = request.POST.get("order_id")
    order_obj = Order.objects.get_by_id(id=order_id)

    if order_obj.pdf:
        pdf = order_obj.pdf
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" % order_obj.order_id
        # content = "inline; filename='%s'" %(filename)
        # response['Content-Disposition'] = content
        return response
    return HttpResponse("Not Found")


