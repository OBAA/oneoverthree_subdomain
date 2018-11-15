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
                        print(slot + ": Empty Slot.")
                        empty_slots.append(slot)

                    else:
                        print(slot + ": Slot Taken.")
                        size_var = str(slot_value).strip('{}')

                        # Size in slot instance: 'S', 'M', 'LG'
                        value = size_var.split(':', 1)[0] .strip("' '")
                        # Size Instance present in cart
                        quantity = size_var.split(' ', 1)[1]
                        print(value)
                        print(quantity)

                        if value == product_size:
                            quantity = product_quantity
                            item['variation'][slot] = {value: quantity}
                            if product_quantity == 0:
                                item['variation'][slot] = '--'

                        slots.append(slot)
                        slot_size.append(value)
                        slot_quantity.append(int(quantity))

                print(str(slots) + 'Taken')
                print(str(empty_slots) + 'Empty')
                print(slot_size)
                print(slot_quantity)

                if product_size not in slot_size:
                    print("Same product different instance")
                    if empty_slots:
                        slot = empty_slots[0]
                        print('slot ' + slot + ' allocated')
                        item['variation'][slot] = {product_size: product_quantity}
                        if product_quantity == 0:
                            item['variation'][slot] = '--'
                        slot_quantity.append(product_quantity)

                # Calculate total quantity.
                item['quantity'] = sum(slot_quantity)
        item = self.cart[product_id]
        if item['quantity'] == 0:
            del item
            print(item)
        self.save()

    def remove(self, product, slot):
        product_id = str(product.id)
        if product_id in self.cart:
            item = self.cart[product_id]
            item['variation'][slot] = '--'
            item['quantity'] = self.get_item_quantity(product_id)
            if item['quantity'] == 0:
                print(item)
                del item
                self.cart.pop(product_id, None)
                print("Item deleted")
            else:
                print("Variation deleted")
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        store = Product.objects.filter(id__in=product_ids)
        # for product in store:
            # self.cart[str(product.id)]['product'] = product
        for item in self.cart.values():
            # item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']

            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total(self):
        return sum(Decimal(item['price']) * int(item['quantity']) for item in self.cart.values())

    def get_weight(self):
        cart_weight = 0
        for item in self.get_items():
            weight = item['attribute']
            cart_weight += float(weight)
            print(cart_weight)
            return cart_weight

    def get_item_quantity(self, product_id):
        item = self.cart[product_id]
        item_quantity = []
        for slot in item['variation'].keys():
            slot_value = item['variation'][slot]
            if slot_value != '--':
                size_var = str(slot_value).strip('{}')
                # size = size_var.split(':', 1)[0].strip("' '")
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
                    # Size in slot instance: 'S', 'M', 'LG'
                    size = size_var.split(':', 1)[0].strip("' '")
                    # Size Instance quantity in cart
                    quantity = size_var.split(' ', 1)[1]
                    item['product'] = Product.objects.get_by_id(id=item['id'])
                    products.append({
                        'id': item['id'],
                        'product': item['product'],
                        'store': item['product'].store,
                        'url': item['product'].get_absolute_url(),
                        'title': item['product'].title,
                        'brand': str(item['product'].brand),
                        'image': str(item['product'].image_a.url),
                        'size': size,
                        'quantity': quantity,
                        'price': item['product'].price,
                        'slot': slot,
                        'attribute': item['product'].product_type,
                    })
        return products




