import unittest
import Generic.functions as f


class MyTestCase(unittest.TestCase):
    orderItems = 0
    pickedKitItems = 0

    def test_calculate_kit_items_to_pick(self):
        self.orderItems = 0
        self.pickedKitItems = 0
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 0)  # add assertion here

        self.orderItems = 1
        self.pickedKitItems = 0
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 1)  # add assertion here

        self.orderItems = 1
        self.pickedKitItems = 1
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 0)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 0
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 2)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 1
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 2)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 2
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 2)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 3
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 2)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 4
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 2)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 5
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 1)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 6
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 0)  # add assertion here

        self.orderItems = 6
        self.pickedKitItems = 7
        self.assertEqual(f.calculate_kit_items_to_pick(self.orderItems, self.pickedKitItems), 0)  # add assertion here


if __name__ == '__main__':
    unittest.main()
