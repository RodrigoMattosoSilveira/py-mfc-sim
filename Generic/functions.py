import Constants.parameters as params


def calculate_kit_items_to_pick(orderItems, kitItemsPicked):
    kit_items_to_pick = 0
    if orderItems != 0:
        if not kitItemsPicked == orderItems:
            if kitItemsPicked + params.KIT_ITEMS_PER_PICK <= orderItems:
                kit_items_to_pick = params.KIT_ITEMS_PER_PICK
            else:
                kit_items_to_pick = orderItems - kitItemsPicked
                if kit_items_to_pick < 0:
                    kit_items_to_pick = 0
    return kit_items_to_pick
