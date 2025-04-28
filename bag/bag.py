from decimal import Decimal
from django.conf import settings

from checkout.utils import get_checkout_settings


# Utility class that manages the shopping bag using Django sessions.
# It acts as a lightweight storage mechanism for storing products added
# to the shopping bag without needing a database table.
class Bag:
    """
    A lightweight shopping bag utility for Gerbet & Co.

    Manages products added to the user's session without requiring
    a database table. Handles add, remove, quantity adjustment,
    and total cost calculations.
    """

    def __init__(self, request):
        """
        Initialize the bag using the session from the incoming request.
        If no bag exists yet, create an empty one.
        """

        self.session = request.session
        bag = self.session.get(settings.BAG_SESSION_ID)

        if not bag:
            bag = self.session[settings.BAG_SESSION_ID] = {}

        self.bag = bag

    def is_empty(self):
        """
        Check if the shopping bag is empty based on total quantity.
        """

        return self.get_total_quantity() == 0

    def save(self):
        """
        Mark the session as modified to ensure it gets saved.
        """

        self.session.modified = True

    def add(self, product_id, product_data=None, quantity=1, action="add"):
        """
        Add a new product to the bag or update the quantity of an existing one.

        Args:
            product_id: The ID of the product.
            product_data: Dictionary containing product details like price,
            title, image URL.
            quantity: Number of units to add or set.
            action: Defines behavior - 'add', 'increase', 'decrease', 'update'.
        """

        product_id = str(product_id)

        if not product_data and product_id not in self.bag:
            raise ValueError("product_data must be provided for new items")

        if product_id in self.bag:
            if action == "increase":
                self.bag[product_id]["quantity"] += 1
            elif action == "decrease":
                self.bag[product_id]["quantity"] -= 1
            elif action == "update":
                self.bag[product_id]["quantity"] = max(quantity, 1)
            else:
                self.bag[product_id]["quantity"] += 1
        else:
            self.bag[product_id] = {
                "quantity": max(quantity, 1),
                "price": str(product_data["price"]),
                "title": product_data["title"],
                "image_url": product_data.get("image_url", "")
            }

        self.save()

    def get_quantity(self, product_id):
        """
        Retrieve the quantity of a specific product in the bag.
        """

        try:
            return self.bag[str(product_id)]["quantity"]
        except Exception:
            return 0

    def remove(self, product_id):
        """
        Remove a product from the bag based on its ID.
        """

        product_id = str(product_id)

        if product_id in self.bag:
            del self.bag[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over bag items, enriching them with additional fields
        like title and image URL for template rendering.
        """

        for product_id, item in self.bag.items():
            try:
                item["price"] = item.get("price", 0.00)

                # Add missing fields with defaults
                item.setdefault("title", "Unknown Product")
                item.setdefault("image_url", "")

                item["product_id"] = int(product_id)

                yield item

            except (KeyError, ValueError):
                del self.bag[product_id]

        self.save()
        return iter([])

    def get_total_quantity(self):
        """
        Calculate the total number of items in the bag.
        """

        return sum(int(item["quantity"]) for item in self.bag.values())

    def adjust_quantity(self, product_id, quantity):
        """
        Set a new quantity for a specific product in the bag.

        Args:
            product_id: The ID of the product.
            quantity: The new quantity to set.
        """

        product_id = str(product_id)
        if product_id in self.bag:
            self.bag[product_id]["quantity"] = quantity
            self.save()

    def get_delivery_cost(self):
        """
        Calculate the delivery cost based on the order total
        and the configured free delivery threshold.
        """

        checkout_settings = get_checkout_settings()
        total = self.get_total_price()
        return (
            0 if total >= checkout_settings.free_delivery_threshold
            else checkout_settings.delivery_cost
        )

    def get_total_price(self):
        """
        Calculate the total price of all items in the bag
        excluding delivery costs.
        """

        total = 0
        for item in self.bag.values():
            total += Decimal(str(item["price"])) * Decimal(item["quantity"])
        return total

    def get_grand_total(self):
        """
        Calculate the grand total (product total + delivery cost).
        """

        if not self.get_total_price():
            return 0
        else:
            return self.get_total_price() + self.get_delivery_cost()

    def clear(self):
        """
        Empty the shopping bag and update the session.
        """

        self.session[settings.BAG_SESSION_ID] = {}
        self.save()
