

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription.
    The handler forwards updates to it's referenced python object
    """

    def __init__(self, obj):
        self.obj = obj

    def datachange_notification(self, node, val, data):
        # print("Python: New data change event", node, val, data)

        _node_name = node.get_browse_name()
        setattr(self.obj, _node_name.Name, data.monitored_item.Value.Value.Value)


def find_o_types(node, type_to_find):
    """
    Search a nodes children for nodes of a specific object type
    :param node: Parent node which will be searched
    :param type_to_find: Object type node to find
    :return: List of nodes that match the desired object type
    """
    found_nodes = []
    for child in node.get_children():
        if child.get_type_definition() == type_to_find.nodeid:
            found_nodes.append(child)

    return found_nodes


def node_search(parent, browse_name):
    """
    Search a parent node's children for a specific browse name and return that node
    """
    _objects_children = parent.get_children()
    for node in _objects_children:
        _child_name = node.get_browse_name()
        if _child_name.Name == browse_name:
            return node
    return None


def scale_value(value, raw_min, raw_max, scaled_min, scaled_max):
    """
    convert a raw value to one scaled in engineering units
    Args:
        value: unscaled value
        raw_min: unscaled value minimum
        raw_max: unscaled value maximum
        scaled_min: engineering minimum
        scaled_max: engineering maximum

    Returns: value scaled to engineering min and max

    """
    return (value - raw_min) * (scaled_max - scaled_min / raw_max - raw_min) + scaled_min
