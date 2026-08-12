import unittest

import pandas as pd

from src.model_utils import (
    attach_dimension_key,
    build_dimension,
)


class BuildDimensionTests(unittest.TestCase):
    def test_build_dimension_single_attribute(self) -> None:
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
        self.assertEqual(
            dimension["product_purchased"].tolist(),
            ["Laptop", "Phone"],
        )
        self.assertEqual(dimension["product_key"].tolist(), [1, 2])

    def test_build_dimension_multiple_attributes(self) -> None:
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


class AttachDimensionKeyTests(unittest.TestCase):
    def test_attach_dimension_key_preserves_rows_and_maps_keys(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1, 2, 3],
                "product_purchased": ["Phone", "Laptop", "Phone"],
            }
        )
        dimension = build_dimension(
            source=source,
            attributes=["product_purchased"],
            key_name="product_key",
        )

        result = attach_dimension_key(
            source=source,
            dimension=dimension,
            attributes=["product_purchased"],
            key_name="product_key",
        )

        self.assertEqual(len(result), 3)
        self.assertFalse(result["product_key"].isna().any())
        self.assertEqual(result["product_key"].tolist(), [2, 1, 2])
        self.assertNotIn("_dimension_match", result.columns)

    def test_attach_dimension_key_rejects_unmatched_rows(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1, 2],
                "product_purchased": ["Phone", "Unknown Product"],
            }
        )
        dimension = pd.DataFrame(
            {
                "product_key": [1],
                "product_purchased": ["Phone"],
            }
        )

        with self.assertRaisesRegex(ValueError, "could not map"):
            attach_dimension_key(
                source=source,
                dimension=dimension,
                attributes=["product_purchased"],
                key_name="product_key",
            )

    def test_attach_dimension_key_rejects_non_unique_lookup(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1],
                "product_purchased": ["Phone"],
            }
        )
        invalid_dimension = pd.DataFrame(
            {
                "product_key": [1, 2],
                "product_purchased": ["Phone", "Phone"],
            }
        )

        with self.assertRaises(pd.errors.MergeError):
            attach_dimension_key(
                source=source,
                dimension=invalid_dimension,
                attributes=["product_purchased"],
                key_name="product_key",
            )


if __name__ == "__main__":
    unittest.main()
