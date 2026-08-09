import unittest

import pandas as pd

from src.model_utils import build_dimension


class BuildDimensionTests(unittest.TestCase):
    def test_build_dimension_single_attribute(self):
        source = pd.DataFrame(
            {
                "product_purchased": [
                    "Phone",
                    "Laptop",
                    "Phone",
                ]
            }
        )

        dimension = build_dimension(
            source=source,
            attributes=["product_purchased"],
            key_name="product_key",
        )

        self.assertEqual(len(dimension), 2)
        self.assertEqual(dimension["product_purchased"].tolist(), ["Laptop", "Phone"])
        self.assertEqual(dimension["product_key"].tolist(), [1, 2])

    def test_build_dimension_multiple_attributes(self):
        source = pd.DataFrame(
            {
                "ticket_type": [
                    "Technical Issue",
                    "Technical Issue",
                    "Billing Inquiry",
                ],
                "ticket_subject": [
                    "Software Bug",
                    "Software Bug",
                    "Payment Issue",
                ],
            }
        )

        dimension = build_dimension(
            source,
            attributes=["ticket_type", "ticket_subject"],
            key_name="issue_key",
        )

        self.assertEqual(len(dimension), 2)
        self.assertTrue(dimension["issue_key"].is_unique)


if __name__ == "__main__":
    unittest.main()
