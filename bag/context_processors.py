from .bag import Bag


def bag_contents(request):
    """
    Adds the shopping bag and total item quantity to the template context,
    allowing dynamic access to bag information across all templates.
    """

    bag = Bag(request)
    return {
        'bag': bag,
        'bag_total_items': bag.get_total_quantity(),
    }
