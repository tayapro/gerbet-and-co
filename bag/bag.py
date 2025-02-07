from django.conf import settings
from products.models import Product


# Utility class that manages the shopping bag using Django sessions.
# It acts as a lightweight storage mechanism for storing products added
# to the shopping bag without needing a database table.
class Bag:
    def __init__(self, request):
        self.session = request.session
        bag = self.session.get(settings.BAG_SESSION_ID)

        if not bag:
            bag = self.session[settings.BAG_SESSION_ID] = {}

        self.bag = bag

        print(f"BAG: {bag}")

    def add(self, product_id, quantity=1):
        product_id = str(product_id)

        if product_id not in self.bag:
            self.bag[product_id] = {'quantity': quantity}
        else:
            self.bag[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.bag:
            del self.bag[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.bag.keys()
        products = Product.objects.filter(id__in=product_ids)
        bag_instance = self.bag.copy()

        for product in products:
            bag_instance[str(product.id)]['product'] = product

        for item in bag_instance.values():
            yield item

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.bag.values())

    def adjust_quantity(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.bag:
            self.bag[product_id]['quantity'] = quantity
            self.save()

    def get_total_price(self):
        return sum(
            item['quantity'] * item['product'].price 
            for item in self.bag.values()
            if 'product' in item
        )

    def clear(self):
        self.session[settings.BAG_SESSION_ID] = {}
        self.save()
