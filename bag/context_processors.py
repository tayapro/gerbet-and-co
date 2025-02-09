from .bag import Bag


def bag_contents(request):
    bag = Bag(request)
    return {
        'bag': bag,
        'bag_total_items': bag.get_total_quantity(),
    }
