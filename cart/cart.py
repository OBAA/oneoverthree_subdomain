from decimal import Decimal
from django.conf import settings
from store.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, size, quantity, update_quantity=False):
        # self.cart.clear()  # Clear Cart
        product_id = str(product.id)
        product_title = str(product.title)
        product_size = str(size)
        product_quantity = int(quantity)
        product_price = str(product.price)
        price = product_price.split('.', 1)[0]
        product_price = int(price)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'id': product_id,
                'title': product_title,
                'variation': {'s1': {product_size: product_quantity}, 's2': '--', 's3': '--'},
                'quantity': 1,
                'price': product_price}

            if update_quantity:
                self.cart[product_id]['quantity'] = product_quantity

        else:
            item = self.cart[product_id]
            if not update_quantity:
                item['quantity'] += 1

            else:
                slots = []
                empty_slots = []
                slot_size = []
                slot_quantity = []

                for slot in item['variation'].keys():
                    slot_value = item['variation'][slot]

                    if slot_value == '--':
                        empty_slots.append(slot)

                    else:
                        size_var = str(slot_value).strip('{}')
                        value = size_var.split(':', 1)[0] .strip("' '")
                        quantity = size_var.split(' ', 1)[1]

                        if value == product_size:
                            quantity = product_quantity
                            item['variation'][slot] = {value: quantity}
                            if product_quantity == 0:
                                item['variation'][slot] = '--'

                        slots.append(slot)
                        slot_size.append(value)
                        slot_quantity.append(int(quantity))

                if product_size not in slot_size:
                    if empty_slots:
                        slot = empty_slots[0]
                        item['variation'][slot] = {product_size: product_quantity}
                        if product_quantity == 0:
                            item['variation'][slot] = '--'
                        slot_quantity.append(product_quantity)

                # Calculate total quantity.
                item['quantity'] = sum(slot_quantity)
        item = self.cart[product_id]
        if item['quantity'] == 0:
            del item
        self.save()

    def remove(self, product, slot):
        product_id = str(product.id)
        if product_id in self.cart:
            item = self.cart[product_id]
            item['variation'][slot] = '--'
            item['quantity'] = self.get_item_quantity(product_id)
            if item['quantity'] == 0:
                del item
                self.cart.pop(product_id, None)
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        store = Product.objects.filter(id__in=product_ids)

        for item in self.cart.values():
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total(self):
        total = sum(Decimal(item['price']) * int(item['quantity']) for item in self.cart.values())
        total = str(total) + ('.00')
        return Decimal(total)

    def get_weight(self):
        cart_weight = 0
        for item in self.get_items():
            weight = item['attribute']
            cart_weight += float(weight)
            return cart_weight

    def get_item_quantity(self, product_id):
        item = self.cart[product_id]
        item_quantity = []
        for slot in item['variation'].keys():
            slot_value = item['variation'][slot]
            if slot_value != '--':
                size_var = str(slot_value).strip('{}')
                quantity = size_var.split(' ', 1)[1]
                item_quantity.append(int(quantity))
        return sum(item_quantity)

    def get_items(self):
        products = []
        for item in self.cart.values():
            for slot in item['variation']:
                slot_value = item['variation'][slot]
                if slot_value != '--':
                    size_var = str(slot_value).strip('{}')
                    size = size_var.split(':', 1)[0].strip("' '")
                    quantity = size_var.split(' ', 1)[1]
                    product = Product.objects.get_by_id(id=item['id'])
                    products.append({
                        'id': item['id'],
                        'product': product,
                        'store': product.store,
                        'url': product.get_absolute_url(),
                        'title': product.title,
                        'brand': str(product.brand),
                        'image': str(product.image_a.url),
                        'size': size,
                        'quantity': quantity,
                        'price': product.price,
                        'slot': slot,
                        'attribute': str(product.product_type.weight),
                    })
        return products



