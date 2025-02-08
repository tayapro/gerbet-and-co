from .bag import Bag


def bag_contents(request):
    bag = Bag(request)
    return {
        'bag_total_items': bag.get_total_quantity(),
    }
