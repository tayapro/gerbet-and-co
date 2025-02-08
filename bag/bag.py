from decimal import Decimal
from django.conf import settings


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

    def add(self, product_id, product_data=None, quantity=1):
        product_id = str(product_id)
        if not product_data:
            raise ValueError("product_data must include all required fields")

        if product_id not in self.bag:
            self.bag[product_id] = {
                'quantity': quantity,
                'price': str(product_data['price']),
                'title': product_data['title'],
                'image_url': product_data.get('image_url', '')
            }
        else:
            self.bag[product_id]['quantity'] += 1

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.bag:
            del self.bag[product_id]
            self.save()

    def __iter__(self):
        for product_id, item in self.bag.items():
            try:
                item['price'] = item.get('price', 0.00)

                # Add missing fields with defaults
                item.setdefault('title', 'Unknown Product')
                item.setdefault('image_url', '')

                item['product_id'] = int(product_id)

                yield item

            except (KeyError, ValueError) as e:
                print(f"Removing invalid bag item {product_id}: {str(e)}")
                del self.bag[product_id]

        self.save()
        return iter([])

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.bag.values())

    def adjust_quantity(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.bag:
            self.bag[product_id]['quantity'] = quantity
            self.save()

    def get_total_price(self):
        total = 0
        for item in self.bag.values():
            total += Decimal(str(item['price'])) * Decimal(item['quantity'])
        return total

    def clear(self):
        self.session[settings.BAG_SESSION_ID] = {}
        self.save()
